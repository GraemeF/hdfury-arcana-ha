"""DataUpdateCoordinator for the HDFury Arcana integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .serial_client import ArcanaSerialClient

_LOGGER = logging.getLogger(__name__)

POLLED_PARAMS: list[str] = [
    "scalemode",
    "audiomode",
    "hdrmode",
    "hdrcustomvalue",
    "hdrboostvalue",
    "lldvtohdrmode",
    "lldvtohdrprimmode",
    "lldvtohdrminlumvalue",
    "lldvtohdrmaxlumvalue",
    "earcsel",
    "arcsel",
    "audsource",
    "earcdelaymode",
    "earcdelayvalue",
    "osdcolorvalue",
    "osdmode",
    "osdfade",
]

SIGNAL_POLLED_PARAMS: list[str] = [
    "rxin5v",
    "txhpd",
    "txtmds",
    "audiochtx",
    "audiopcm",
]

STATUS_PARAMS: list[str] = [
    "rx",
    "tx",
    "txcaps",
    "aud",
    "earc",
    "spd",
]

STATIC_PARAMS: list[str] = [
    "ver",
    "serial",
]

DEFAULT_SIGNAL_POLL_INTERVAL = 30

# Some firmware never answers some signal params, and each unanswered get costs
# a full command timeout on every poll.
TIMEOUTS_BEFORE_GIVING_UP_ON_SILENT_PARAM = 3


class ArcanaCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Coordinator that polls Arcana settings over serial."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(minutes=5),
            always_update=False,
        )
        self._client = ArcanaSerialClient(entry.data["serial_port"])
        self._static_data: dict[str, str] = {}

    async def async_set(self, param: str, value: str | None = None) -> str:
        """Send a set command to the device."""
        try:
            return await self._client.set(param, value)
        except (
            TimeoutError,
            ConnectionError,
            OSError,
            asyncio.IncompleteReadError,
        ) as err:
            raise HomeAssistantError(str(err)) from err

    async def async_disconnect(self) -> None:
        """Disconnect the serial client."""
        await self._client.disconnect()

    async def _async_setup(self) -> None:
        """Connect to the device on first refresh."""
        await self._client.connect()

    async def _async_update_data(self) -> dict[str, str]:
        """Fetch settings data from the Arcana."""
        try:
            params_to_poll = list(POLLED_PARAMS)
            if not self._static_data:
                params_to_poll += STATIC_PARAMS

            data: dict[str, str] = {}
            for param in params_to_poll:
                try:
                    data[param] = await self._client.get(param)
                except TimeoutError:
                    _LOGGER.debug("Timeout polling %s, skipping", param)
                    continue

            if not data:
                raise UpdateFailed("All params timed out")

            if not self._static_data:
                if "ver" not in data or "serial" not in data:
                    raise UpdateFailed("Could not fetch static params")
                self._static_data = {p: data[p] for p in STATIC_PARAMS}

            return {**self._static_data, **data}
        except (
            ConnectionError,
            OSError,
            asyncio.IncompleteReadError,
        ) as err:
            raise UpdateFailed(str(err)) from err


class ArcanaSignalCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Coordinator that polls Arcana signal status at a faster interval."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: ArcanaSerialClient,
        static_data: dict[str, str],
        poll_interval: int = DEFAULT_SIGNAL_POLL_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_signal",
            config_entry=entry,
            update_interval=timedelta(seconds=poll_interval),
            always_update=False,
        )
        self._client = client
        self._static_data = static_data
        self._answered_params: set[str] = set()
        self._silent_param_timeouts: dict[str, int] = {}

    def _gave_up_on(self, param: str) -> bool:
        return (
            self._silent_param_timeouts.get(param, 0)
            >= TIMEOUTS_BEFORE_GIVING_UP_ON_SILENT_PARAM
        )

    def _record_timeout(self, param: str) -> None:
        if param in self._answered_params:
            return
        self._silent_param_timeouts[param] = (
            self._silent_param_timeouts.get(param, 0) + 1
        )
        if self._gave_up_on(param):
            _LOGGER.debug("%s has never answered, no longer polling it", param)

    async def _async_update_data(self) -> dict[str, str]:
        """Fetch signal status data from the Arcana."""
        try:
            data: dict[str, str] = {}
            for param in SIGNAL_POLLED_PARAMS:
                if self._gave_up_on(param):
                    continue
                try:
                    data[param] = await self._client.get(param)
                except TimeoutError:
                    _LOGGER.debug("Timeout polling %s, skipping", param)
                    self._record_timeout(param)
                    continue
                self._answered_params.add(param)

            for param in STATUS_PARAMS:
                try:
                    data[param] = await self._client.get_status(param)
                except TimeoutError:
                    _LOGGER.debug("Timeout polling status %s, skipping", param)
                    continue

            return {**self._static_data, **data}
        except (
            ConnectionError,
            OSError,
            asyncio.IncompleteReadError,
        ) as err:
            raise UpdateFailed(str(err)) from err

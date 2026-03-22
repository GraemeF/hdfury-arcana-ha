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
    "osd",
    "osdtimervalue",
    "rxin5v",
    "txhpd",
    "txtmds",
    "audiochtx",
    "audiopcm",
    "osdfade",
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


class ArcanaCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Coordinator that polls the HDFury Arcana over serial."""

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
            ConnectionError,
            OSError,
            asyncio.TimeoutError,
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
        """Fetch data from the Arcana."""
        try:
            params_to_poll = list(POLLED_PARAMS)
            if not self._static_data:
                params_to_poll += STATIC_PARAMS

            data: dict[str, str] = {}
            for param in params_to_poll:
                data[param] = await self._client.get(param)

            for param in STATUS_PARAMS:
                data[param] = await self._client.get_status(param)

            if not self._static_data:
                self._static_data = {p: data[p] for p in STATIC_PARAMS}

            return {**self._static_data, **data}
        except (
            ConnectionError,
            OSError,
            asyncio.TimeoutError,
            asyncio.IncompleteReadError,
        ) as err:
            raise UpdateFailed(str(err)) from err

"""DataUpdateCoordinator for the HDFury Arcana integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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

            if not self._static_data:
                self._static_data = {p: data[p] for p in STATIC_PARAMS}

            return {**self._static_data, **data}
        except ConnectionError as err:
            raise UpdateFailed(str(err)) from err

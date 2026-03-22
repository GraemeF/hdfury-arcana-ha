"""Select platform for the HDFury Arcana integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ArcanaConfigEntry
from .entity import ArcanaEntity
from .coordinator import ArcanaCoordinator

SELECTS: dict[str, list[str]] = {
    "scalemode": [
        "auto",
        "none",
        "4k60_420_10_hdr",
        "4k60_420_10_sdr",
        "4k60_420_8_hdr",
        "4k60_420_8_sdr",
        "4k30_444_8_hdr",
        "4k30_444_8_sdr",
        "1080p60_12_hdr",
        "1080p60_12_sdr",
        "1080p60_8_sdr",
    ],
    "hdrmode": ["auto", "off", "force1000", "custom"],
    "lldvtohdrprimmode": ["bt2020", "dci-p3"],
    "audsource": ["hdmi", "tv"],
    "audiomode": ["auto", "display", "earc", "both"],
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ArcanaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([ArcanaSelectEntity(coordinator, key) for key in SELECTS])


class ArcanaSelectEntity(ArcanaEntity, SelectEntity):
    """Select entity for Arcana parameters with enumerated options."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: ArcanaCoordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._attr_translation_key = key

    @property
    def options(self) -> list[str]:
        return SELECTS[self._key]

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set(self._key, option)
        await self.coordinator.async_request_refresh()

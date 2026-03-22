"""Number platform for the HDFury Arcana integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity
from homeassistant.const import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import ArcanaEntity
from .coordinator import ArcanaCoordinator


@dataclass
class NumberConfig:
    """Configuration for a number entity."""

    min_value: float
    max_value: float
    step: float = 1


NUMBERS: dict[str, NumberConfig] = {
    "hdrcustomvalue": NumberConfig(0, 10000),
    "hdrboostvalue": NumberConfig(0, 100),
    "earcdelayvalue": NumberConfig(0, 200),
    "lldvtohdrminlumvalue": NumberConfig(0, 10000),
    "lldvtohdrmaxlumvalue": NumberConfig(0, 10000),
    "osdcolorvalue": NumberConfig(0, 63),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([ArcanaNumberEntity(coordinator, key) for key in NUMBERS])


class ArcanaNumberEntity(ArcanaEntity, NumberEntity):
    """Number entity for Arcana parameters with numeric ranges."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: ArcanaCoordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._attr_translation_key = key
        config = NUMBERS[key]
        self._attr_native_min_value = config.min_value
        self._attr_native_max_value = config.max_value
        self._attr_native_step = config.step

    @property
    def native_value(self) -> float | None:
        val = self.coordinator.data.get(self._key)
        if val is not None:
            return float(val)
        return None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator._client.set(self._key, str(int(value)))
        await self.coordinator.async_request_refresh()

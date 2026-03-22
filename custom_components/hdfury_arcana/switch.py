"""Switch platform for the HDFury Arcana integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ArcanaConfigEntry
from .entity import ArcanaEntity
from .coordinator import ArcanaCoordinator

SWITCHES: list[str] = ["earcsel", "arcsel", "earcdelaymode", "lldvtohdrmode", "osdmode"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ArcanaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([ArcanaSwitchEntity(coordinator, key) for key in SWITCHES])


class ArcanaSwitchEntity(ArcanaEntity, SwitchEntity):
    """Switch entity for on/off Arcana parameters."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: ArcanaCoordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._attr_translation_key = key

    @property
    def is_on(self) -> bool:
        if self.coordinator.data is None:
            return False
        return self.coordinator.data.get(self._key) == "on"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set(self._key, "on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set(self._key, "off")
        await self.coordinator.async_request_refresh()

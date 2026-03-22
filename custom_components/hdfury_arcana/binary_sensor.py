"""Binary sensor platform for the HDFury Arcana integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ArcanaConfigEntry
from .entity import ArcanaEntity
from .coordinator import ArcanaCoordinator

BINARY_SENSORS: list[str] = ["rxin5v", "txhpd", "txtmds"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ArcanaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities."""
    coordinator = entry.runtime_data.signal_coordinator
    async_add_entities(
        [ArcanaBinarySensorEntity(coordinator, key) for key in BINARY_SENSORS]
    )


class ArcanaBinarySensorEntity(ArcanaEntity, BinarySensorEntity):
    """Binary sensor entity for read-only on/off Arcana status parameters."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: ArcanaCoordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._attr_translation_key = key

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key) == "on"

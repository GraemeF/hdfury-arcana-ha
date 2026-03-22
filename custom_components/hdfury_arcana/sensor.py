"""Sensor platform for the HDFury Arcana integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ArcanaConfigEntry
from .entity import ArcanaEntity
from .coordinator import ArcanaCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ArcanaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        [
            ArcanaFirmwareSensor(coordinator),
            ArcanaSerialSensor(coordinator),
        ]
    )


class ArcanaFirmwareSensor(ArcanaEntity, SensorEntity):
    """Sensor showing the firmware version."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: ArcanaCoordinator) -> None:
        super().__init__(coordinator, "ver")
        self._attr_translation_key = "firmware_version"

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("ver")


class ArcanaSerialSensor(ArcanaEntity, SensorEntity):
    """Sensor showing the device serial number."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: ArcanaCoordinator) -> None:
        super().__init__(coordinator, "serial")
        self._attr_translation_key = "serial_number"

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("serial")

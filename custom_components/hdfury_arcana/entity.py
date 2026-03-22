"""Base entity for the HDFury Arcana integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ArcanaCoordinator


class ArcanaEntity(CoordinatorEntity[ArcanaCoordinator]):
    """Base entity for HDFury Arcana devices."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ArcanaCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._serial = coordinator.data["serial"]
        self._firmware = coordinator.data["ver"]
        self._attr_unique_id = f"{self._serial}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info linking all entities to one device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._serial)},
            name="HDFury Arcana",
            manufacturer="HDFury",
            model="Arcana",
            sw_version=self._firmware,
            serial_number=self._serial,
        )

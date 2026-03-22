"""Button platform for the HDFury Arcana integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ArcanaConfigEntry
from .entity import ArcanaEntity
from .coordinator import ArcanaCoordinator

BUTTONS: list[str] = ["hotplug", "reboot"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ArcanaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities."""
    coordinator = entry.runtime_data.coordinator
    entities: list[ButtonEntity] = [
        ArcanaButtonEntity(coordinator, key) for key in BUTTONS
    ]
    entities.append(ArcanaRefreshButtonEntity(coordinator))
    async_add_entities(entities)


class ArcanaButtonEntity(ArcanaEntity, ButtonEntity):
    """Button entity for fire-and-forget Arcana actions."""

    def __init__(self, coordinator: ArcanaCoordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._attr_translation_key = key

    async def async_press(self) -> None:
        await self.coordinator.async_set(self._key)


class ArcanaRefreshButtonEntity(ArcanaEntity, ButtonEntity):
    """Button entity that triggers an immediate data refresh."""

    def __init__(self, coordinator: ArcanaCoordinator) -> None:
        super().__init__(coordinator, "refresh")
        self._attr_translation_key = "refresh"

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()

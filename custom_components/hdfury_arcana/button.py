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
    async_add_entities([ArcanaButtonEntity(coordinator, key) for key in BUTTONS])


class ArcanaButtonEntity(ArcanaEntity, ButtonEntity):
    """Button entity for fire-and-forget Arcana actions."""

    def __init__(self, coordinator: ArcanaCoordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._attr_translation_key = key

    async def async_press(self) -> None:
        await self.coordinator.async_set(self._key)

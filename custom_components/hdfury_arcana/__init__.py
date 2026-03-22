"""The HDFury Arcana integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import ArcanaCoordinator

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

type ArcanaConfigEntry = ConfigEntry[ArcanaRuntimeData]


@dataclass
class ArcanaRuntimeData:
    """Runtime data for the HDFury Arcana integration."""

    coordinator: ArcanaCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ArcanaConfigEntry) -> bool:
    """Set up HDFury Arcana from a config entry."""
    coordinator = ArcanaCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = ArcanaRuntimeData(coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ArcanaConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await entry.runtime_data.coordinator.async_disconnect()
    return unload_ok

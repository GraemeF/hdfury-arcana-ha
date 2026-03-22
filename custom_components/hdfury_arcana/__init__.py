"""The HDFury Arcana integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import (
    ArcanaCoordinator,
    ArcanaSignalCoordinator,
    DEFAULT_SIGNAL_POLL_INTERVAL,
)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
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
    signal_coordinator: ArcanaSignalCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ArcanaConfigEntry) -> bool:
    """Set up HDFury Arcana from a config entry."""
    coordinator = ArcanaCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    poll_interval = entry.options.get(
        "signal_poll_interval", DEFAULT_SIGNAL_POLL_INTERVAL
    )
    signal_coordinator = ArcanaSignalCoordinator(
        hass,
        entry,
        coordinator._client,
        static_data={
            "ver": coordinator.data["ver"],
            "serial": coordinator.data["serial"],
        },
        poll_interval=poll_interval,
    )
    await signal_coordinator.async_refresh()

    entry.runtime_data = ArcanaRuntimeData(
        coordinator=coordinator,
        signal_coordinator=signal_coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ArcanaConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await entry.runtime_data.coordinator.async_disconnect()
    return unload_ok

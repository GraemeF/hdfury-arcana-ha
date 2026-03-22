"""Tests for the HDFury Arcana button platform."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.hdfury_arcana.const import DOMAIN
from custom_components.hdfury_arcana.coordinator import ArcanaCoordinator
from custom_components.hdfury_arcana.button import ArcanaButtonEntity, BUTTONS

from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.fixture
def mock_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"serial_port": "/dev/ttyUSB0"},
        unique_id="ABC123",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_client():
    """Create a mock serial client."""
    client = AsyncMock()
    client.connected = True
    return client


@pytest.fixture
def coordinator(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_client
) -> ArcanaCoordinator:
    """Create a coordinator with mock data."""
    coord = ArcanaCoordinator(hass, mock_config_entry)
    coord._client = mock_client
    coord.data = {"ver": "1.2.3", "serial": "ABC123"}
    return coord


class TestButtonDefinitions:
    """Test button entity definitions."""

    def test_hotplug_button_exists(self):
        assert "hotplug" in BUTTONS

    def test_reboot_button_exists(self):
        assert "reboot" in BUTTONS


class TestButtonActions:
    """Test button press actions."""

    async def test_press_sends_set_command(self, coordinator, mock_client):
        entity = ArcanaButtonEntity(coordinator, "hotplug")

        await entity.async_press()

        mock_client.set.assert_called_once_with("hotplug", None)

    async def test_reboot_sends_set_command(self, coordinator, mock_client):
        entity = ArcanaButtonEntity(coordinator, "reboot")

        await entity.async_press()

        mock_client.set.assert_called_once_with("reboot", None)

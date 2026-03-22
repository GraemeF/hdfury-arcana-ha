"""Tests for the HDFury Arcana button platform."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.hdfury_arcana.coordinator import ArcanaCoordinator
from custom_components.hdfury_arcana.button import (
    ArcanaButtonEntity,
    ArcanaFactoryResetButtonEntity,
    ArcanaRefreshButtonEntity,
    BUTTONS,
)

from pytest_homeassistant_custom_component.common import MockConfigEntry


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


class TestRefreshButton:
    """Test the refresh button."""

    async def test_press_triggers_refresh(self, coordinator):
        coordinator.async_request_refresh = AsyncMock()
        entity = ArcanaRefreshButtonEntity(coordinator)

        await entity.async_press()

        coordinator.async_request_refresh.assert_called_once()

    async def test_press_does_not_send_serial_command(self, coordinator, mock_client):
        coordinator.async_request_refresh = AsyncMock()
        entity = ArcanaRefreshButtonEntity(coordinator)

        await entity.async_press()

        mock_client.set.assert_not_called()


class TestFactoryResetButton:
    """Test the factory reset button."""

    async def test_press_sends_factoryreset_with_value_3(
        self, coordinator, mock_client
    ):
        entity = ArcanaFactoryResetButtonEntity(coordinator)

        await entity.async_press()

        mock_client.set.assert_called_once_with("factoryreset", "3")

"""Tests for the HDFury Arcana switch platform."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant

from custom_components.hdfury_arcana.coordinator import ArcanaCoordinator
from custom_components.hdfury_arcana.switch import ArcanaSwitchEntity, SWITCHES

from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.fixture
def coordinator(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_client
) -> ArcanaCoordinator:
    """Create a coordinator with mock data."""
    coord = ArcanaCoordinator(hass, mock_config_entry)
    coord._client = mock_client
    coord.data = {
        "ver": "1.2.3",
        "serial": "ABC123",
        "earcsel": "on",
        "arcsel": "off",
        "earcdelaymode": "on",
    }
    return coord


class TestSwitchDefinitions:
    """Test switch entity definitions."""

    def test_all_switches_are_config_category(self, coordinator):
        for key in SWITCHES:
            entity = ArcanaSwitchEntity(coordinator, key)
            assert entity.entity_category == EntityCategory.CONFIG


class TestSwitchState:
    """Test switch state reading."""

    def test_is_on_when_value_is_on(self, coordinator):
        entity = ArcanaSwitchEntity(coordinator, "earcsel")
        assert entity.is_on is True

    def test_is_off_when_value_is_off(self, coordinator):
        entity = ArcanaSwitchEntity(coordinator, "arcsel")
        assert entity.is_on is False


class TestSwitchActions:
    """Test switch turn on/off actions."""

    async def test_turn_on_sends_set_command(self, coordinator, mock_client):
        entity = ArcanaSwitchEntity(coordinator, "earcsel")
        coordinator.async_request_refresh = AsyncMock()

        await entity.async_turn_on()

        mock_client.set.assert_called_once_with("earcsel", "on")
        coordinator.async_request_refresh.assert_called_once()

    async def test_turn_off_sends_set_command(self, coordinator, mock_client):
        entity = ArcanaSwitchEntity(coordinator, "earcsel")
        coordinator.async_request_refresh = AsyncMock()

        await entity.async_turn_off()

        mock_client.set.assert_called_once_with("earcsel", "off")
        coordinator.async_request_refresh.assert_called_once()


class TestNoneData:
    """Test switch with None coordinator data."""

    def test_is_on_returns_false(self, coordinator):
        entity = ArcanaSwitchEntity(coordinator, "earcsel")
        coordinator.data = None
        assert entity.is_on is False

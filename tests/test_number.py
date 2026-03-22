"""Tests for the HDFury Arcana number platform."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant

from custom_components.hdfury_arcana.const import DOMAIN
from custom_components.hdfury_arcana.coordinator import ArcanaCoordinator
from custom_components.hdfury_arcana.number import ArcanaNumberEntity, NUMBERS

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
    coord.data = {
        "ver": "1.2.3",
        "serial": "ABC123",
        "hdrcustomvalue": "500",
        "hdrboostvalue": "50",
        "earcdelayvalue": "100",
        "lldvtohdrminlumvalue": "0",
        "lldvtohdrmaxlumvalue": "10000",
        "osdcolorvalue": "32",
    }
    return coord


class TestNumberDefinitions:
    """Test number entity definitions."""

    def test_all_numbers_are_config_category(self, coordinator):
        for key in NUMBERS:
            entity = ArcanaNumberEntity(coordinator, key)
            assert entity.entity_category == EntityCategory.CONFIG

    def test_hdrcustomvalue_range(self, coordinator):
        entity = ArcanaNumberEntity(coordinator, "hdrcustomvalue")
        assert entity.native_min_value == 0
        assert entity.native_max_value == 10000
        assert entity.native_step == 1

    def test_hdrboostvalue_range(self, coordinator):
        entity = ArcanaNumberEntity(coordinator, "hdrboostvalue")
        assert entity.native_min_value == 0
        assert entity.native_max_value == 100

    def test_osdcolorvalue_range(self, coordinator):
        entity = ArcanaNumberEntity(coordinator, "osdcolorvalue")
        assert entity.native_min_value == 0
        assert entity.native_max_value == 63


class TestNumberState:
    """Test number state reading."""

    def test_native_value(self, coordinator):
        entity = ArcanaNumberEntity(coordinator, "hdrcustomvalue")
        assert entity.native_value == 500.0


class TestNumberActions:
    """Test number set value."""

    async def test_set_value_sends_set_command(self, coordinator, mock_client):
        entity = ArcanaNumberEntity(coordinator, "hdrcustomvalue")
        coordinator.async_request_refresh = AsyncMock()

        await entity.async_set_native_value(750)

        mock_client.set.assert_called_once_with("hdrcustomvalue", "750")
        coordinator.async_request_refresh.assert_called_once()

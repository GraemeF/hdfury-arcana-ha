"""Tests for the HDFury Arcana binary sensor platform."""

from __future__ import annotations

import pytest
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant

from custom_components.hdfury_arcana.coordinator import ArcanaCoordinator
from custom_components.hdfury_arcana.binary_sensor import (
    ArcanaBinarySensorEntity,
    BINARY_SENSORS,
)

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
        "rxin5v": "on",
        "txhpd": "off",
        "txtmds": "on",
    }
    return coord


class TestBinarySensorDefinitions:
    """Test binary sensor entity definitions."""

    def test_rxin5v_is_a_binary_sensor(self, coordinator):
        assert "rxin5v" in BINARY_SENSORS

    def test_txhpd_is_a_binary_sensor(self, coordinator):
        assert "txhpd" in BINARY_SENSORS

    def test_txtmds_is_a_binary_sensor(self, coordinator):
        assert "txtmds" in BINARY_SENSORS

    def test_all_binary_sensors_are_diagnostic(self, coordinator):
        for key in BINARY_SENSORS:
            entity = ArcanaBinarySensorEntity(coordinator, key)
            assert entity.entity_category == EntityCategory.DIAGNOSTIC


class TestBinarySensorState:
    """Test binary sensor state reading."""

    def test_is_on_when_value_is_on(self, coordinator):
        entity = ArcanaBinarySensorEntity(coordinator, "rxin5v")
        assert entity.is_on is True

    def test_is_off_when_value_is_off(self, coordinator):
        entity = ArcanaBinarySensorEntity(coordinator, "txhpd")
        assert entity.is_on is False


class TestNoneData:
    """Test binary sensor with None coordinator data."""

    def test_is_on_returns_none(self, coordinator):
        entity = ArcanaBinarySensorEntity(coordinator, "rxin5v")
        coordinator.data = None
        assert entity.is_on is None

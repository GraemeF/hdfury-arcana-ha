"""Tests for the HDFury Arcana sensor platform."""

from __future__ import annotations

import pytest
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant

from custom_components.hdfury_arcana.coordinator import ArcanaCoordinator
from custom_components.hdfury_arcana.sensor import (
    ArcanaFirmwareSensor,
    ArcanaSerialSensor,
)

from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.fixture
def coordinator(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_client
) -> ArcanaCoordinator:
    """Create a coordinator with mock data."""
    coord = ArcanaCoordinator(hass, mock_config_entry)
    coord._client = mock_client
    coord.data = {"ver": "1.2.3", "serial": "ABC123", "scalemode": "auto"}
    return coord


class TestFirmwareSensor:
    """Test the firmware version sensor."""

    def test_native_value(self, coordinator):
        sensor = ArcanaFirmwareSensor(coordinator)
        assert sensor.native_value == "1.2.3"

    def test_entity_category_is_diagnostic(self, coordinator):
        sensor = ArcanaFirmwareSensor(coordinator)
        assert sensor.entity_category == EntityCategory.DIAGNOSTIC

    def test_unique_id(self, coordinator):
        sensor = ArcanaFirmwareSensor(coordinator)
        assert sensor.unique_id == "ABC123_ver"


class TestSerialSensor:
    """Test the serial number sensor."""

    def test_native_value(self, coordinator):
        sensor = ArcanaSerialSensor(coordinator)
        assert sensor.native_value == "ABC123"

    def test_entity_category_is_diagnostic(self, coordinator):
        sensor = ArcanaSerialSensor(coordinator)
        assert sensor.entity_category == EntityCategory.DIAGNOSTIC

    def test_unique_id(self, coordinator):
        sensor = ArcanaSerialSensor(coordinator)
        assert sensor.unique_id == "ABC123_serial"

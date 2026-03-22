"""Tests for the HDFury Arcana sensor platform."""

from __future__ import annotations

import pytest
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant

from custom_components.hdfury_arcana.coordinator import ArcanaCoordinator
from custom_components.hdfury_arcana.sensor import (
    ArcanaDiagnosticSensor,
    ArcanaFirmwareSensor,
    ArcanaSerialSensor,
    SIGNAL_SENSORS,
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


class TestSignalSensors:
    """Test signal status sensors."""

    def test_all_signal_sensors_defined(self, coordinator):
        expected = ["rx", "tx", "txcaps", "aud", "earc", "spd", "audiochtx", "audiopcm"]
        assert SIGNAL_SENSORS == expected

    def test_signal_sensor_value(self, coordinator):
        coordinator.data["rx"] = "4K23.97 297MHz 444 BT709 8b"
        sensor = ArcanaDiagnosticSensor(coordinator, "rx")
        assert sensor.native_value == "4K23.97 297MHz 444 BT709 8b"

    def test_signal_sensor_is_diagnostic(self, coordinator):
        coordinator.data["rx"] = "something"
        sensor = ArcanaDiagnosticSensor(coordinator, "rx")
        assert sensor.entity_category == EntityCategory.DIAGNOSTIC

    def test_signal_sensor_none_data(self, coordinator):
        sensor = ArcanaDiagnosticSensor(coordinator, "rx")
        coordinator.data = None
        assert sensor.native_value is None


class TestNoneData:
    """Test entity properties when coordinator data is None."""

    def test_firmware_sensor_returns_none(self, coordinator):
        sensor = ArcanaFirmwareSensor(coordinator)
        coordinator.data = None
        assert sensor.native_value is None

    def test_serial_sensor_returns_none(self, coordinator):
        sensor = ArcanaSerialSensor(coordinator)
        coordinator.data = None
        assert sensor.native_value is None

"""Tests for the HDFury Arcana base entity class."""

from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from custom_components.hdfury_arcana.const import DOMAIN
from custom_components.hdfury_arcana.coordinator import ArcanaCoordinator
from custom_components.hdfury_arcana.entity import ArcanaEntity

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


class TestBaseEntity:
    """Test the base entity class."""

    def test_has_entity_name(self, coordinator):
        entity = ArcanaEntity(coordinator, "test_key")
        assert entity.has_entity_name is True

    def test_unique_id_includes_serial_and_key(self, coordinator):
        entity = ArcanaEntity(coordinator, "scalemode")
        assert entity.unique_id == "ABC123_scalemode"

    def test_device_info(self, coordinator):
        entity = ArcanaEntity(coordinator, "test_key")
        info = entity.device_info
        assert info == DeviceInfo(
            identifiers={(DOMAIN, "ABC123")},
            name="HDFury Arcana",
            manufacturer="HDFury",
            model="Arcana",
            sw_version="1.2.3",
            serial_number="ABC123",
        )

"""Tests for the HDFury Arcana select platform."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant

from custom_components.hdfury_arcana.const import DOMAIN
from custom_components.hdfury_arcana.coordinator import ArcanaCoordinator
from custom_components.hdfury_arcana.select import ArcanaSelectEntity, SELECTS

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
        "scalemode": "auto",
        "audiomode": "auto",
        "hdrmode": "auto",
        "lldvtohdrmode": "off",
        "lldvtohdrprimmode": "bt2020",
        "audsource": "hdmi",
    }
    return coord


class TestSelectDefinitions:
    """Test select entity definitions."""

    def test_all_selects_are_config_category(self, coordinator):
        for key in SELECTS:
            entity = ArcanaSelectEntity(coordinator, key)
            assert entity.entity_category == EntityCategory.CONFIG

    def test_scalemode_has_correct_options(self, coordinator):
        entity = ArcanaSelectEntity(coordinator, "scalemode")
        assert "auto" in entity.options
        assert "none" in entity.options
        assert "4k60_420_10_hdr" in entity.options


class TestSelectState:
    """Test select state reading."""

    def test_current_option(self, coordinator):
        entity = ArcanaSelectEntity(coordinator, "scalemode")
        assert entity.current_option == "auto"


class TestSelectActions:
    """Test select option change."""

    async def test_select_option_sends_set_command(self, coordinator, mock_client):
        entity = ArcanaSelectEntity(coordinator, "scalemode")
        coordinator.async_request_refresh = AsyncMock()

        await entity.async_select_option("none")

        mock_client.set.assert_called_once_with("scalemode", "none")
        coordinator.async_request_refresh.assert_called_once()

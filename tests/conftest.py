"""Global test fixtures for the HDFury Arcana integration."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.hdfury_arcana.const import DOMAIN

from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


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

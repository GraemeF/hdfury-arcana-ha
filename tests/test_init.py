"""Tests for the HDFury Arcana integration lifecycle."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.hdfury_arcana.const import DOMAIN
from custom_components.hdfury_arcana.coordinator import (
    POLLED_PARAMS,
    SIGNAL_POLLED_PARAMS,
    STATIC_PARAMS,
)

from pytest_homeassistant_custom_component.common import MockConfigEntry


def _mock_client_with_data():
    """Create a mock client that returns data for all params."""
    client = AsyncMock()
    client.connected = True
    get_responses = {
        p: f"{p}_val" for p in POLLED_PARAMS + STATIC_PARAMS + SIGNAL_POLLED_PARAMS
    }
    client.get = AsyncMock(side_effect=lambda p: get_responses[p])
    client.get_status = AsyncMock(side_effect=lambda p: f"{p}_status")
    return client


@pytest.fixture
def mock_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"serial_port": "/dev/ttyUSB0"},
        unique_id="ABC123",
    )
    entry.add_to_hass(hass)
    return entry


class TestUnloadOrdering:
    """Test that unload disconnects after platform teardown."""

    async def test_disconnect_called_after_platform_unload(
        self, hass: HomeAssistant, mock_entry: MockConfigEntry
    ):
        call_order = []
        mock_client = _mock_client_with_data()

        with patch(
            "custom_components.hdfury_arcana.coordinator.ArcanaSerialClient",
            return_value=mock_client,
        ):
            await hass.config_entries.async_setup(mock_entry.entry_id)
            await hass.async_block_till_done()

        coordinator = mock_entry.runtime_data.coordinator
        original_disconnect = coordinator.async_disconnect

        async def tracking_disconnect():
            call_order.append("disconnect")
            await original_disconnect()

        coordinator.async_disconnect = tracking_disconnect

        original_unload_platforms = hass.config_entries.async_unload_platforms

        async def tracking_unload_platforms(entry, platforms):
            call_order.append("unload_platforms")
            return await original_unload_platforms(entry, platforms)

        hass.config_entries.async_unload_platforms = tracking_unload_platforms

        await hass.config_entries.async_unload(mock_entry.entry_id)
        await hass.async_block_till_done()

        assert call_order == ["unload_platforms", "disconnect"]


class TestSignalCoordinatorFailure:
    """Test that setup succeeds even when signal commands fail."""

    async def test_setup_succeeds_when_signal_commands_fail(
        self, hass: HomeAssistant, mock_entry: MockConfigEntry
    ):
        mock_client = _mock_client_with_data()
        mock_client.get_status = AsyncMock(
            side_effect=asyncio.TimeoutError("no response")
        )

        with patch(
            "custom_components.hdfury_arcana.coordinator.ArcanaSerialClient",
            return_value=mock_client,
        ):
            await hass.config_entries.async_setup(mock_entry.entry_id)
            await hass.async_block_till_done()

        assert mock_entry.state.value == "loaded"

    async def test_setup_succeeds_when_signal_get_fails(
        self, hass: HomeAssistant, mock_entry: MockConfigEntry
    ):
        mock_client = _mock_client_with_data()
        # Settings get works, but signal params fail
        settings_responses = {p: f"{p}_val" for p in POLLED_PARAMS + STATIC_PARAMS}

        def selective_get(p):
            if p in settings_responses:
                return settings_responses[p]
            raise asyncio.TimeoutError("no response")

        mock_client.get = AsyncMock(side_effect=selective_get)
        mock_client.get_status = AsyncMock(
            side_effect=asyncio.TimeoutError("no response")
        )

        with patch(
            "custom_components.hdfury_arcana.coordinator.ArcanaSerialClient",
            return_value=mock_client,
        ):
            await hass.config_entries.async_setup(mock_entry.entry_id)
            await hass.async_block_till_done()

        assert mock_entry.state.value == "loaded"

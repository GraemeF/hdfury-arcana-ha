"""Tests for the HDFury Arcana DataUpdateCoordinator."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.hdfury_arcana.coordinator import (
    ArcanaCoordinator,
    POLLED_PARAMS,
    STATIC_PARAMS,
)

from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.fixture
def coordinator(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_client
) -> ArcanaCoordinator:
    """Create a coordinator with a mock client."""
    coord = ArcanaCoordinator(hass, mock_config_entry)
    coord._client = mock_client
    return coord


class TestFirstPoll:
    """Test that the first poll fetches static and polled params."""

    async def test_first_poll_fetches_static_params(self, coordinator, mock_client):
        responses = {p: f"{p}_val" for p in POLLED_PARAMS + STATIC_PARAMS}
        mock_client.get = AsyncMock(side_effect=lambda p: responses[p])

        data = await coordinator._async_update_data()

        for param in STATIC_PARAMS:
            mock_client.get.assert_any_call(param)
            assert data[param] == f"{param}_val"

    async def test_first_poll_fetches_polled_params(self, coordinator, mock_client):
        responses = {p: f"{p}_val" for p in POLLED_PARAMS + STATIC_PARAMS}
        mock_client.get = AsyncMock(side_effect=lambda p: responses[p])

        data = await coordinator._async_update_data()

        for param in POLLED_PARAMS:
            mock_client.get.assert_any_call(param)
            assert data[param] == f"{param}_val"


class TestSubsequentPolls:
    """Test that subsequent polls only fetch polled params."""

    async def test_does_not_refetch_static_params(self, coordinator, mock_client):
        all_responses = {p: f"{p}_val" for p in POLLED_PARAMS + STATIC_PARAMS}
        mock_client.get = AsyncMock(side_effect=lambda p: all_responses[p])

        # First poll
        await coordinator._async_update_data()
        mock_client.get.reset_mock()

        # Second poll - only polled params
        polled_responses = {p: f"{p}_val2" for p in POLLED_PARAMS}
        mock_client.get = AsyncMock(side_effect=lambda p: polled_responses[p])

        data = await coordinator._async_update_data()

        # Static params should retain first poll values
        for param in STATIC_PARAMS:
            assert data[param] == f"{param}_val"

        # Polled params should have new values
        for param in POLLED_PARAMS:
            assert data[param] == f"{param}_val2"

    async def test_static_params_not_called_on_second_poll(
        self, coordinator, mock_client
    ):
        all_responses = {p: f"{p}_val" for p in POLLED_PARAMS + STATIC_PARAMS}
        mock_client.get = AsyncMock(side_effect=lambda p: all_responses[p])

        await coordinator._async_update_data()
        mock_client.get.reset_mock()

        polled_responses = {p: f"{p}_val2" for p in POLLED_PARAMS}
        mock_client.get = AsyncMock(side_effect=lambda p: polled_responses[p])

        await coordinator._async_update_data()

        called_params = [call.args[0] for call in mock_client.get.call_args_list]
        for param in STATIC_PARAMS:
            assert param not in called_params


class TestErrorHandling:
    """Test coordinator error handling."""

    async def test_serial_error_raises_update_failed(self, coordinator, mock_client):
        mock_client.get = AsyncMock(side_effect=ConnectionError("port gone"))

        with pytest.raises(UpdateFailed, match="port gone"):
            await coordinator._async_update_data()

    async def test_timeout_raises_update_failed(self, coordinator, mock_client):
        mock_client.get = AsyncMock(side_effect=asyncio.TimeoutError)

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    async def test_oserror_raises_update_failed(self, coordinator, mock_client):
        mock_client.get = AsyncMock(side_effect=OSError("device gone"))

        with pytest.raises(UpdateFailed, match="device gone"):
            await coordinator._async_update_data()


class TestConnection:
    """Test coordinator manages client connection."""

    async def test_setup_connects_client(self, coordinator, mock_client):
        mock_client.connected = False
        all_responses = {p: f"{p}_val" for p in POLLED_PARAMS + STATIC_PARAMS}
        mock_client.get = AsyncMock(side_effect=lambda p: all_responses[p])

        await coordinator._async_setup()
        await coordinator._async_update_data()

        mock_client.connect.assert_called_once()

    async def test_disconnect_closes_client(self, coordinator, mock_client):
        await coordinator.async_disconnect()

        mock_client.disconnect.assert_called_once()


class TestSendCommand:
    """Test the public send_command API."""

    async def test_delegates_set_to_client(self, coordinator, mock_client):
        mock_client.set = AsyncMock()

        await coordinator.async_set("scalemode", "auto")

        mock_client.set.assert_called_once_with("scalemode", "auto")

    async def test_delegates_set_without_value(self, coordinator, mock_client):
        mock_client.set = AsyncMock()

        await coordinator.async_set("hotplug")

        mock_client.set.assert_called_once_with("hotplug", None)

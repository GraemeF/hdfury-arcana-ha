"""Tests for the HDFury Arcana config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.hdfury_arcana.const import DOMAIN


class TestUserStep:
    """Test the manual user configuration step."""

    async def test_shows_form(self, hass: HomeAssistant):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

    async def test_creates_entry_on_success(self, hass: HomeAssistant):
        with patch(
            "custom_components.hdfury_arcana.config_flow.ArcanaSerialClient"
        ) as mock_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                side_effect=lambda p: {"ver": "1.0", "serial": "SN001"}[p]
            )
            mock_client.disconnect = AsyncMock()
            mock_cls.return_value = mock_client

            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={"serial_port": "/dev/ttyUSB0"},
            )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "HDFury Arcana"
        assert result["data"]["serial_port"] == "/dev/ttyUSB0"

    async def test_stores_firmware_and_serial(self, hass: HomeAssistant):
        with patch(
            "custom_components.hdfury_arcana.config_flow.ArcanaSerialClient"
        ) as mock_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                side_effect=lambda p: {"ver": "2.5", "serial": "XYZ789"}[p]
            )
            mock_client.disconnect = AsyncMock()
            mock_cls.return_value = mock_client

            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={"serial_port": "/dev/ttyUSB0"},
            )

        assert result["data"]["firmware_version"] == "2.5"
        assert result["data"]["serial_number"] == "XYZ789"

    async def test_sets_unique_id_from_serial(self, hass: HomeAssistant):
        with patch(
            "custom_components.hdfury_arcana.config_flow.ArcanaSerialClient"
        ) as mock_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                side_effect=lambda p: {"ver": "1.0", "serial": "SN001"}[p]
            )
            mock_client.disconnect = AsyncMock()
            mock_cls.return_value = mock_client

            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={"serial_port": "/dev/ttyUSB0"},
            )

        assert result["result"].unique_id == "SN001"


class TestConnectionErrors:
    """Test error handling during connection verification."""

    async def test_shows_error_on_connection_failure(self, hass: HomeAssistant):
        with patch(
            "custom_components.hdfury_arcana.config_flow.ArcanaSerialClient"
        ) as mock_cls:
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock(side_effect=ConnectionError("nope"))
            mock_cls.return_value = mock_client

            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={"serial_port": "/dev/ttyUSB0"},
            )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "cannot_connect"

    async def test_shows_error_on_timeout(self, hass: HomeAssistant):
        import asyncio

        with patch(
            "custom_components.hdfury_arcana.config_flow.ArcanaSerialClient"
        ) as mock_cls:
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock(side_effect=asyncio.TimeoutError)
            mock_cls.return_value = mock_client

            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={"serial_port": "/dev/ttyUSB0"},
            )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "cannot_connect"

"""Tests for the HDFury Arcana config flow."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.hdfury_arcana.config_flow import MANUAL_ENTRY
from custom_components.hdfury_arcana.const import DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry


def _mock_comport(device="/dev/ttyUSB0", serial_number="ABC", manufacturer="FTDI"):
    """Create a mock serial port info object."""
    port = type("PortInfo", (), {})()
    port.device = device
    port.serial_number = serial_number
    port.manufacturer = manufacturer
    port.description = "USB Serial"
    return port


def _make_client_mock(ver="1.0", serial="SN001"):
    """Create a mock ArcanaSerialClient that returns given ver/serial."""
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=lambda p: {"ver": ver, "serial": serial}[p])
    mock_client.disconnect = AsyncMock()
    return mock_client


class TestUserStep:
    """Test the port selection step."""

    async def test_shows_detected_ports_in_dropdown(self, hass: HomeAssistant):
        ports = [_mock_comport("/dev/ttyUSB0"), _mock_comport("/dev/ttyUSB1")]

        with patch(
            "custom_components.hdfury_arcana.config_flow.comports",
            return_value=ports,
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        schema_keys = list(result["data_schema"].schema.keys())
        assert len(schema_keys) == 1

    async def test_includes_manual_entry_option(self, hass: HomeAssistant):
        ports = [_mock_comport()]

        with patch(
            "custom_components.hdfury_arcana.config_flow.comports",
            return_value=ports,
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )

        # The dropdown options should include the manual entry sentinel
        schema = result["data_schema"].schema
        port_key = list(schema.keys())[0]
        validator = schema[port_key]
        assert MANUAL_ENTRY in validator.container

    async def test_selecting_port_validates_and_creates_entry(
        self, hass: HomeAssistant
    ):
        ports = [_mock_comport("/dev/ttyUSB0")]

        with (
            patch(
                "custom_components.hdfury_arcana.config_flow.comports",
                return_value=ports,
            ),
            patch(
                "custom_components.hdfury_arcana.config_flow.ArcanaSerialClient"
            ) as mock_cls,
        ):
            mock_cls.return_value = _make_client_mock()

            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={"serial_port": "/dev/ttyUSB0"},
            )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"]["serial_port"] == "/dev/ttyUSB0"

    async def test_selecting_manual_goes_to_manual_step(self, hass: HomeAssistant):
        ports = [_mock_comport()]

        with patch(
            "custom_components.hdfury_arcana.config_flow.comports",
            return_value=ports,
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={"serial_port": MANUAL_ENTRY},
            )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "manual"

    async def test_no_ports_detected_goes_straight_to_manual(self, hass: HomeAssistant):
        with patch(
            "custom_components.hdfury_arcana.config_flow.comports",
            return_value=[],
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "manual"


class TestManualStep:
    """Test the manual port entry step."""

    async def test_creates_entry_on_success(self, hass: HomeAssistant):
        with (
            patch(
                "custom_components.hdfury_arcana.config_flow.comports",
                return_value=[],
            ),
            patch(
                "custom_components.hdfury_arcana.config_flow.ArcanaSerialClient"
            ) as mock_cls,
        ):
            mock_cls.return_value = _make_client_mock(ver="2.5", serial="XYZ789")

            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={"serial_port": "/dev/ttyACM0"},
            )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"]["serial_port"] == "/dev/ttyACM0"
        assert result["data"]["firmware_version"] == "2.5"
        assert result["data"]["serial_number"] == "XYZ789"
        assert result["result"].unique_id == "XYZ789"


class TestOptionsFlow:
    """Test the options flow for configuring poll interval."""

    async def test_shows_current_interval(self, hass: HomeAssistant):
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"serial_port": "/dev/ttyUSB0"},
            unique_id="OPT1",
        )
        entry.add_to_hass(hass)

        result = await hass.config_entries.options.async_init(entry.entry_id)

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "init"

    async def test_saves_new_interval(self, hass: HomeAssistant):
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"serial_port": "/dev/ttyUSB0"},
            unique_id="OPT2",
        )
        entry.add_to_hass(hass)

        result = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"signal_poll_interval": 60},
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert entry.options["signal_poll_interval"] == 60


class TestConnectionErrors:
    """Test error handling during connection verification."""

    async def test_shows_error_on_connection_failure(self, hass: HomeAssistant):
        ports = [_mock_comport()]

        with (
            patch(
                "custom_components.hdfury_arcana.config_flow.comports",
                return_value=ports,
            ),
            patch(
                "custom_components.hdfury_arcana.config_flow.ArcanaSerialClient"
            ) as mock_cls,
        ):
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
        ports = [_mock_comport()]

        with (
            patch(
                "custom_components.hdfury_arcana.config_flow.comports",
                return_value=ports,
            ),
            patch(
                "custom_components.hdfury_arcana.config_flow.ArcanaSerialClient"
            ) as mock_cls,
        ):
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

    async def test_shows_error_on_incomplete_read(self, hass: HomeAssistant):
        ports = [_mock_comport()]

        with (
            patch(
                "custom_components.hdfury_arcana.config_flow.comports",
                return_value=ports,
            ),
            patch(
                "custom_components.hdfury_arcana.config_flow.ArcanaSerialClient"
            ) as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                side_effect=asyncio.IncompleteReadError(b"partial", 100)
            )
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

    async def test_manual_step_shows_error_on_failure(self, hass: HomeAssistant):
        with (
            patch(
                "custom_components.hdfury_arcana.config_flow.comports",
                return_value=[],
            ),
            patch(
                "custom_components.hdfury_arcana.config_flow.ArcanaSerialClient"
            ) as mock_cls,
        ):
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock(side_effect=ConnectionError("nope"))
            mock_cls.return_value = mock_client

            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={"serial_port": "/dev/ttyACM0"},
            )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "manual"
        assert result["errors"]["base"] == "cannot_connect"

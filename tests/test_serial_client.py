"""Tests for the HDFury Arcana serial client."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.hdfury_arcana.serial_client import ArcanaSerialClient


@pytest.fixture
def mock_serial_connection():
    """Create mock reader/writer pair simulating a serial connection."""
    reader = AsyncMock()
    writer = MagicMock()
    writer.write = MagicMock()
    writer.close = MagicMock()
    writer.wait_closed = AsyncMock()
    return reader, writer


@pytest.fixture
def client():
    """Create a serial client instance."""
    return ArcanaSerialClient("/dev/ttyUSB0")


class TestCommandFormatting:
    """Test that commands are formatted correctly for the wire."""

    async def test_get_command_sends_correct_bytes(
        self, client, mock_serial_connection
    ):
        reader, writer = mock_serial_connection
        reader.readuntil = AsyncMock(return_value=b"auto\r\n")

        with (
            patch.object(client, "_reader", reader),
            patch.object(client, "_writer", writer),
            patch.object(client, "_connected", True),
        ):
            await client.get("scalemode")

        writer.write.assert_called_once_with(b"#arcana get scalemode\r")

    async def test_set_command_sends_correct_bytes(
        self, client, mock_serial_connection
    ):
        reader, writer = mock_serial_connection
        reader.readuntil = AsyncMock(return_value=b"ok\r\n")

        with (
            patch.object(client, "_reader", reader),
            patch.object(client, "_writer", writer),
            patch.object(client, "_connected", True),
        ):
            await client.set("scalemode", "auto")

        writer.write.assert_called_once_with(b"#arcana set scalemode auto\r")

    async def test_set_command_without_value(self, client, mock_serial_connection):
        reader, writer = mock_serial_connection
        reader.readuntil = AsyncMock(return_value=b"ok\r\n")

        with (
            patch.object(client, "_reader", reader),
            patch.object(client, "_writer", writer),
            patch.object(client, "_connected", True),
        ):
            await client.set("hotplug")

        writer.write.assert_called_once_with(b"#arcana set hotplug\r")


class TestResponseParsing:
    """Test that responses are parsed correctly."""

    async def test_strips_crlf_from_response(self, client, mock_serial_connection):
        reader, writer = mock_serial_connection
        reader.readuntil = AsyncMock(return_value=b"auto\r\n")

        with (
            patch.object(client, "_reader", reader),
            patch.object(client, "_writer", writer),
            patch.object(client, "_connected", True),
        ):
            result = await client.get("scalemode")

        assert result == "auto"

    async def test_strips_whitespace_from_response(
        self, client, mock_serial_connection
    ):
        reader, writer = mock_serial_connection
        reader.readuntil = AsyncMock(return_value=b"  1.2.3  \r\n")

        with (
            patch.object(client, "_reader", reader),
            patch.object(client, "_writer", writer),
            patch.object(client, "_connected", True),
        ):
            result = await client.get("ver")

        assert result == "1.2.3"


class TestTimeout:
    """Test command timeout behaviour."""

    async def test_raises_on_read_timeout(self, client, mock_serial_connection):
        reader, writer = mock_serial_connection
        reader.readuntil = AsyncMock(side_effect=asyncio.TimeoutError)

        with (
            patch.object(client, "_reader", reader),
            patch.object(client, "_writer", writer),
            patch.object(client, "_connected", True),
        ):
            with pytest.raises(asyncio.TimeoutError):
                await client.get("scalemode")


class TestLocking:
    """Test that serial access is serialised through the lock."""

    async def test_concurrent_commands_are_serialised(
        self, client, mock_serial_connection
    ):
        reader, writer = mock_serial_connection
        call_order = []

        async def slow_read(*args, **kwargs):
            call_order.append("read_start")
            await asyncio.sleep(0.05)
            call_order.append("read_end")
            return b"ok\r\n"

        reader.readuntil = slow_read

        with (
            patch.object(client, "_reader", reader),
            patch.object(client, "_writer", writer),
            patch.object(client, "_connected", True),
        ):
            await asyncio.gather(
                client.get("scalemode"),
                client.get("audiomode"),
            )

        # If serialised, reads never overlap
        assert call_order == [
            "read_start",
            "read_end",
            "read_start",
            "read_end",
        ]


class TestConnection:
    """Test connect and disconnect behaviour."""

    async def test_connect_opens_serial_port(self, client):
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()

        with patch(
            "custom_components.hdfury_arcana.serial_client.open_serial_connection",
            new_callable=AsyncMock,
            return_value=(mock_reader, mock_writer),
        ) as mock_open:
            await client.connect()

        mock_open.assert_called_once_with(
            url="/dev/ttyUSB0", baudrate=19200, bytesize=8, parity="N", stopbits=1
        )
        assert client.connected

    async def test_disconnect_closes_writer(self, client):
        mock_writer = MagicMock()
        mock_writer.close = MagicMock()
        mock_writer.wait_closed = AsyncMock()

        with (
            patch.object(client, "_writer", mock_writer),
            patch.object(client, "_connected", True),
        ):
            await client.disconnect()

        mock_writer.close.assert_called_once()
        assert not client.connected

    async def test_not_connected_by_default(self, client):
        assert not client.connected


class TestReconnect:
    """Test automatic reconnection with exponential backoff."""

    async def test_reconnects_on_send_when_disconnected(self, client):
        mock_reader = AsyncMock()
        mock_reader.readuntil = AsyncMock(return_value=b"ok\r\n")
        mock_writer = MagicMock()
        mock_writer.write = MagicMock()

        with patch(
            "custom_components.hdfury_arcana.serial_client.open_serial_connection",
            new_callable=AsyncMock,
            return_value=(mock_reader, mock_writer),
        ) as mock_open:
            result = await client.get("ver")

        mock_open.assert_called_once()
        assert result == "ok"

    async def test_backoff_increases_on_repeated_failures(self, client):
        attempt_times = []

        async def failing_connect(*args, **kwargs):
            attempt_times.append(asyncio.get_event_loop().time())
            raise ConnectionError("nope")

        with patch(
            "custom_components.hdfury_arcana.serial_client.open_serial_connection",
            new_callable=AsyncMock,
            side_effect=failing_connect,
        ):
            with pytest.raises(ConnectionError):
                await client.get("ver")

        # Should have attempted multiple times
        assert len(attempt_times) > 1
        # Gaps between attempts should increase
        gaps = [
            attempt_times[i + 1] - attempt_times[i]
            for i in range(len(attempt_times) - 1)
        ]
        assert gaps[-1] > gaps[0]

    async def test_backoff_resets_after_successful_reconnect(self, client):
        call_count = 0
        mock_reader = AsyncMock()
        mock_reader.readuntil = AsyncMock(return_value=b"ok\r\n")
        mock_writer = MagicMock()
        mock_writer.write = MagicMock()

        async def flaky_connect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("nope")
            return mock_reader, mock_writer

        with patch(
            "custom_components.hdfury_arcana.serial_client.open_serial_connection",
            new_callable=AsyncMock,
            side_effect=flaky_connect,
        ):
            await client.get("ver")

        assert client.connected
        assert client._backoff_delay == client.INITIAL_BACKOFF


class TestTransportErrorMarksDisconnected:
    """Test that transport errors during commands mark connection as failed."""

    async def test_timeout_marks_disconnected(self, client, mock_serial_connection):
        reader, writer = mock_serial_connection
        reader.readuntil = AsyncMock(side_effect=asyncio.TimeoutError)

        client._reader = reader
        client._writer = writer
        client._connected = True

        with pytest.raises(asyncio.TimeoutError):
            await client.get("scalemode")

        assert not client.connected

    async def test_oserror_marks_disconnected(self, client, mock_serial_connection):
        reader, writer = mock_serial_connection
        reader.readuntil = AsyncMock(side_effect=OSError("device unplugged"))

        client._reader = reader
        client._writer = writer
        client._connected = True

        with pytest.raises(OSError):
            await client.get("scalemode")

        assert not client.connected

    async def test_incomplete_read_marks_disconnected(
        self, client, mock_serial_connection
    ):
        reader, writer = mock_serial_connection
        reader.readuntil = AsyncMock(
            side_effect=asyncio.IncompleteReadError(b"partial", 100)
        )

        client._reader = reader
        client._writer = writer
        client._connected = True

        with pytest.raises(asyncio.IncompleteReadError):
            await client.get("scalemode")

        assert not client.connected

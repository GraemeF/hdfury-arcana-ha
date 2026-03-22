"""Serial client for communicating with the HDFury Arcana over RS-232."""

from __future__ import annotations

import asyncio
import logging

from serial_asyncio_fast import open_serial_connection

_LOGGER = logging.getLogger(__name__)

BAUD_RATE = 19200
COMMAND_TIMEOUT = 2.0


class ArcanaSerialClient:
    """Async serial client for the HDFury Arcana."""

    INITIAL_BACKOFF = 1.0
    MAX_BACKOFF = 60.0
    MAX_RETRIES = 3

    def __init__(self, port: str) -> None:
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._connected = False
        self._lock = asyncio.Lock()
        self._backoff_delay = self.INITIAL_BACKOFF

    @property
    def connected(self) -> bool:
        """Return whether the client is connected."""
        return self._connected

    async def connect(self) -> None:
        """Open the serial connection."""
        self._reader, self._writer = await open_serial_connection(
            url=self._port, baudrate=BAUD_RATE, bytesize=8, parity="N", stopbits=1
        )
        self._connected = True
        self._backoff_delay = self.INITIAL_BACKOFF

    async def disconnect(self) -> None:
        """Close the serial connection."""
        if self._writer is not None:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except OSError:
                pass
        self._reader = None
        self._writer = None
        self._connected = False

    async def get(self, param: str) -> str:
        """Send a get command and return the response value."""
        return await self._send_command(f"#arcana get {param}\r")

    async def set(self, param: str, value: str | None = None) -> str:
        """Send a set command and return the response."""
        if value is not None:
            cmd = f"#arcana set {param} {value}\r"
        else:
            cmd = f"#arcana set {param}\r"
        return await self._send_command(cmd)

    async def _ensure_connected(self) -> None:
        """Reconnect with exponential backoff if not connected."""
        if self._connected:
            return

        for attempt in range(self.MAX_RETRIES):
            try:
                await self.connect()
                return
            except (ConnectionError, OSError):
                if attempt == self.MAX_RETRIES - 1:
                    raise
                _LOGGER.debug(
                    "Connection attempt %d failed, retrying in %.1fs",
                    attempt + 1,
                    self._backoff_delay,
                )
                await asyncio.sleep(self._backoff_delay)
                self._backoff_delay = min(self._backoff_delay * 2, self.MAX_BACKOFF)

    async def _send_command(self, cmd: str) -> str:
        """Send a command under lock with timeout, return stripped response."""
        async with self._lock:
            await self._ensure_connected()
            try:
                self._writer.write(cmd.encode())
                raw = await asyncio.wait_for(
                    self._reader.readuntil(b"\r\n"), timeout=COMMAND_TIMEOUT
                )
                return raw.decode().strip()
            except (OSError, asyncio.TimeoutError, asyncio.IncompleteReadError):
                self._connected = False
                raise

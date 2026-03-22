"""Serial client for communicating with the HDFury Arcana over RS-232."""

from __future__ import annotations

import asyncio

from serial_asyncio_fast import open_serial_connection

BAUD_RATE = 19200
COMMAND_TIMEOUT = 2.0


class ArcanaSerialClient:
    """Async serial client for the HDFury Arcana."""

    def __init__(self, port: str) -> None:
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._connected = False
        self._lock = asyncio.Lock()

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

    async def disconnect(self) -> None:
        """Close the serial connection."""
        if self._writer is not None:
            self._writer.close()
            await self._writer.wait_closed()
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

    async def _send_command(self, cmd: str) -> str:
        """Send a command under lock with timeout, return stripped response."""
        async with self._lock:
            self._writer.write(cmd.encode())
            raw = await asyncio.wait_for(
                self._reader.readuntil(b"\r\n"), timeout=COMMAND_TIMEOUT
            )
            return raw.decode().strip()

"""Config flow for the HDFury Arcana integration."""

from __future__ import annotations

import asyncio
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN
from .serial_client import ArcanaSerialClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("serial_port"): str,
    }
)


class ArcanaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HDFury Arcana."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await self._validate_connection(user_input["serial_port"])
            except (ConnectionError, asyncio.TimeoutError, OSError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during config flow")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["serial_number"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="HDFury Arcana",
                    data={
                        "serial_port": user_input["serial_port"],
                        "firmware_version": info["firmware_version"],
                        "serial_number": info["serial_number"],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _validate_connection(self, serial_port: str) -> dict[str, str]:
        """Validate the serial connection by querying version and serial."""
        client = ArcanaSerialClient(serial_port)
        try:
            await client.connect()
            firmware = await client.get("ver")
            serial = await client.get("serial")
            return {"firmware_version": firmware, "serial_number": serial}
        finally:
            await client.disconnect()

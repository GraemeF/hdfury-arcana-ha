"""Config flow for the HDFury Arcana integration."""

from __future__ import annotations

import asyncio
import logging

import voluptuous as vol
from serial.tools.list_ports import comports

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN
from .serial_client import ArcanaSerialClient

_LOGGER = logging.getLogger(__name__)

MANUAL_ENTRY = "Enter manually..."


class ArcanaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HDFury Arcana."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle port selection step."""
        errors: dict[str, str] = {}

        ports = await self.hass.async_add_executor_job(comports)
        port_list = [p.device for p in ports]

        if not port_list:
            return await self.async_step_manual()

        if user_input is not None:
            if user_input["serial_port"] == MANUAL_ENTRY:
                return await self.async_step_manual()
            return await self._validate_and_create(
                user_input["serial_port"], "user", errors
            )

        port_list.append(MANUAL_ENTRY)
        schema = vol.Schema({vol.Required("serial_port"): vol.In(port_list)})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_manual(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle manual port entry step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return await self._validate_and_create(
                user_input["serial_port"], "manual", errors
            )

        schema = vol.Schema({vol.Required("serial_port"): str})
        return self.async_show_form(step_id="manual", data_schema=schema, errors=errors)

    async def _validate_and_create(
        self, serial_port: str, step_id: str, errors: dict[str, str]
    ) -> FlowResult:
        """Validate connection and create config entry, or show errors."""
        try:
            info = await self._validate_connection(serial_port)
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
                    "serial_port": serial_port,
                    "firmware_version": info["firmware_version"],
                    "serial_number": info["serial_number"],
                },
            )

        if step_id == "manual":
            schema = vol.Schema({vol.Required("serial_port"): str})
        else:
            ports = await self.hass.async_add_executor_job(comports)
            port_list = [p.device for p in ports] + [MANUAL_ENTRY]
            schema = vol.Schema({vol.Required("serial_port"): vol.In(port_list)})
        return self.async_show_form(step_id=step_id, data_schema=schema, errors=errors)

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

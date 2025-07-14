"""
Config Flow för Loggamera Integration
Möjliggör GUI-konfiguration i Home Assistant
"""

import voluptuous as vol
import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, SENSOR_TYPES
from .api_client import LoggameraApiClient, LoggameraDataParser

_LOGGER = logging.getLogger(__name__)

CONF_LOCATION_ID = "location_id"
CONF_SENSOR_TYPE = "sensor_type"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_BASE_URL = "base_url"

DEFAULT_BASE_URL = "https://portal.loggamera.se"

class LoggameraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Loggamera."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            # Validate the location by trying to fetch data
            session = async_get_clientsession(self.hass)
            client = LoggameraApiClient(session, user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL))
            
            try:
                # Test API connection
                html = await client.fetch_data(user_input[CONF_LOCATION_ID])
                parser = LoggameraDataParser()
                value = parser.parse_sensor_data(html, user_input[CONF_SENSOR_TYPE])
                
                if value is None:
                    errors["base"] = "no_data_found"
                else:
                    # Success - create entry
                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=user_input
                    )
                    
            except Exception as err:
                _LOGGER.error("Error testing Loggamera connection: %s", err)
                errors["base"] = "cannot_connect"

        # Show form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default="Loggamera Sensor"): cv.string,
                vol.Required(CONF_LOCATION_ID): cv.positive_int,
                vol.Required(CONF_SENSOR_TYPE, default="temperature"): vol.In(SENSOR_TYPES.keys()),
                vol.Optional(CONF_UPDATE_INTERVAL, default=5): vol.All(
                    cv.positive_int, vol.Range(min=1, max=60)
                ),
                vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): cv.url,
            }),
            errors=errors,
        )

    async def async_step_import(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return LoggameraOptionsFlowHandler(config_entry)


class LoggameraOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Loggamera options."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=self.config_entry.options.get(CONF_UPDATE_INTERVAL, 5),
                ): vol.All(cv.positive_int, vol.Range(min=1, max=60)),
                vol.Optional(
                    CONF_BASE_URL,
                    default=self.config_entry.options.get(CONF_BASE_URL, DEFAULT_BASE_URL),
                ): cv.url,
            }),
        ) 
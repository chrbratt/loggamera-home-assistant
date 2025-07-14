"""Config flow for Loggamera integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, SENSORS

_LOGGER = logging.getLogger(__name__)

# Scan interval options (in seconds for backend)
SCAN_INTERVALS = {
    "1 minute": 60,
    "5 minutes": 300,
    "15 minutes": 900,
    "30 minutes": 1800,
    "1 hour": 3600,
    "6 hours": 21600,
    "12 hours": 43200,
    "24 hours": 86400
}

class LoggameraConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for Loggamera."""

    domain = DOMAIN
    VERSION = 1



    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        # Check if already configured
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            # Get selected sensors
            selected_sensors = []
            if user_input.get("sensor_vattern", False):
                selected_sensors.append(22)
            if user_input.get("sensor_mullsjon", False):
                selected_sensors.append(21)
            
            if not selected_sensors:
                errors["base"] = "no_sensors_selected"
            else:
                # Create config entry
                config_data = {
                    "sensors": selected_sensors,
                    "scan_interval": user_input.get("scan_interval", 300)
                }
                
                return self.async_create_entry(
                    title="Loggamera Temperature Sensors",
                    data=config_data
                )

        # Create schema for sensor selection
        data_schema = vol.Schema({
            vol.Optional("sensor_vattern", default=True): cv.boolean,
            vol.Optional("sensor_mullsjon", default=True): cv.boolean,
            vol.Optional("scan_interval", default=300): vol.In(SCAN_INTERVALS.values())
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "sensor_vattern": "Lake Vättern (ID: 22)",
                "sensor_mullsjon": "Lake Mullsjön (ID: 21)"
            }
        )

    async def async_step_import(self, user_input=None) -> FlowResult:
        """Handle import from YAML configuration."""
        # Support for migrating from YAML config
        return await self.async_step_user(user_input) 
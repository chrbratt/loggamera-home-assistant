"""Config flow for Loggamera integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Available sensor locations
SENSORS = {
    22: "Lake Vättern",
    21: "Lake Mullsjön"
}

# Scan interval options (in minutes for user-friendly display)
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
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL



    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate that at least one sensor is selected
            selected_sensors = [
                sensor_id for sensor_id, enabled in user_input.items() 
                if sensor_id in SENSORS and enabled
            ]
            
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
            **{
                vol.Optional(sensor_id, default=True): cv.boolean
                for sensor_id in SENSORS.keys()
            },
            vol.Optional("scan_interval", default=300): vol.In(SCAN_INTERVALS.values())
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "sensor_22": SENSORS[22],
                "sensor_21": SENSORS[21]
            }
        )

    async def async_step_import(self, user_input=None) -> FlowResult:
        """Handle import from YAML configuration."""
        # Support for migrating from YAML config
        return await self.async_step_user(user_input) 
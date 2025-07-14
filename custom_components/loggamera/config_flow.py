"""Config flow for Loggamera integration."""
from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN, SENSORS, DEFAULT_SCAN_INTERVAL

class LoggameraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Loggamera."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            # Get selected sensors
            selected_sensors = []
            if user_input.get("sensor_vattern", False):
                selected_sensors.append(22)
            if user_input.get("sensor_mullsjon", False):
                selected_sensors.append(21)
            
            # Validate that at least one sensor is selected
            if not selected_sensors:
                errors["base"] = "no_sensors_selected"
            else:
                # Set unique ID to prevent duplicate config entries
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                
                # Create config entry with selected sensors
                return self.async_create_entry(
                    title="Badtemperaturer Hjo Energi",
                    data={
                        "sensors": selected_sensors,
                        "scan_interval": DEFAULT_SCAN_INTERVAL
                    }
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional("sensor_vattern", default=True): bool,
                vol.Optional("sensor_mullsjon", default=True): bool,
            }),
            errors=errors,
            description_placeholders={
                "vattern": "Lake Vättern",
                "mullsjon": "Lake Mullsjön"
            }
        ) 
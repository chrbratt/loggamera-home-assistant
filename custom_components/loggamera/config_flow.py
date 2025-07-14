"""Config flow for Loggamera integration."""
from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN, SENSORS, DEFAULT_SCAN_INTERVAL

class LoggameraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Loggamera."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Set unique ID to prevent duplicate config entries
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            
            # Create config entry with expected data structure
            return self.async_create_entry(
                title="Loggamera Temperature Sensors",
                data={
                    "sensors": [22, 21],  # Both Lake Vättern and Lake Mullsjön
                    "scan_interval": DEFAULT_SCAN_INTERVAL
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("setup", default="proceed"): vol.In(["proceed"])
            }),
            description_placeholders={
                "sensors": "Lake Vättern och Lake Mullsjön"
            }
        ) 
"""Config flow for Loggamera integration."""
from homeassistant import config_entries
import voluptuous as vol

DOMAIN = "loggamera"

class LoggameraConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for Loggamera."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Loggamera Sensors",
                data={"test": True}
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("setup"): vol.In(["proceed"])
            })
        ) 
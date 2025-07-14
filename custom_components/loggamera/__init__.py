"""
Loggamera Integration för Home Assistant.
Hämtar temperaturdata från Loggamera IoT-plattformen.
"""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "loggamera"
PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Loggamera integration."""
    _LOGGER.info("Setting up Loggamera integration")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Loggamera from a config entry."""
    _LOGGER.info("Setting up Loggamera config entry")
    
    # Forward to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.info("Unloading Loggamera config entry")
    
    # Unload sensor platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok 
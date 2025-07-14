"""
Loggamera Integration for Home Assistant.
Retrieves temperature data from Loggamera IoT platform.
"""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Loggamera integration from YAML (deprecated)."""
    # YAML configuration is deprecated, use Config Flow instead
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Loggamera from a config entry."""
    _LOGGER.info("Setting up Loggamera integration with config entry")
    
    # Store config data for platforms to access
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Forward to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok 
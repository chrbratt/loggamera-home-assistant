"""
Loggamera Integration for Home Assistant.
Retrieves temperature data from Loggamera IoT platform.
"""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.NUMBER, Platform.SWITCH]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Loggamera integration from YAML (deprecated)."""
    # YAML configuration is deprecated, use Config Flow instead
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Loggamera from a config entry."""
    _LOGGER.info("Setting up Loggamera integration with config entry")
    
    # Import dependencies only when needed to avoid blocking
    import asyncio
    import aiohttp
    from homeassistant.helpers.aiohttp_client import async_get_clientsession
    
    # Test API connectivity before setting up platforms
    session = async_get_clientsession(hass)
    config_data = entry.data
    selected_sensors = config_data.get("sensors", [22, 21])
    
    # Test at least one sensor to verify API connectivity
    test_sensor_id = selected_sensors[0] if selected_sensors else 22
    
    try:
        await _test_api_connectivity(session, test_sensor_id)
        _LOGGER.debug(f"API connectivity test successful for sensor {test_sensor_id}")
    except (asyncio.TimeoutError, aiohttp.ClientError) as err:
        _LOGGER.warning(f"Cannot connect to Loggamera API: {err}")
        raise ConfigEntryNotReady(f"Cannot connect to Loggamera API: {err}") from err
    except Exception as err:
        _LOGGER.error(f"Unexpected error testing Loggamera API: {err}")
        raise ConfigEntryNotReady(f"Unexpected error: {err}") from err
    
    # Store config data for platforms to access
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Load platforms asynchronously to avoid blocking
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def _test_api_connectivity(session, sensor_id):
    """Test connectivity to Loggamera API."""
    url = "https://portal.loggamera.se/PublicViews/OverviewInside"
    data = {"id": sensor_id}
    
    async with session.post(url, data=data, timeout=10) as response:
        if response.status != 200:
            import aiohttp
            raise aiohttp.ClientError(f"HTTP {response.status}")
        
        html = await response.text()
        if len(html) < 100:  # Basic sanity check
            import aiohttp
            raise aiohttp.ClientError("Received empty or very short response")

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # Unload platforms asynchronously
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok 
"""
Loggamera Temperature Sensor Integration for Home Assistant
"""

import asyncio
import aiohttp
import re
import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSORS

_LOGGER = logging.getLogger(__name__)

# Legacy YAML platform schema (for backward compatibility)
PLATFORM_SCHEMA = vol.Schema({
    vol.Required("platform"): "loggamera",
    vol.Required("sensors"): vol.All(cv.ensure_list, [
        vol.Schema({
            vol.Required("name"): cv.string,
            vol.Required("location_id"): cv.positive_int,
            vol.Optional("unit", default=TEMP_CELSIUS): cv.string,
            vol.Optional("scan_interval", default=300): vol.All(
                cv.positive_int, 
                vol.Range(min=60, max=86400)
            ),
        })
    ])
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up Loggamera sensors from YAML (deprecated)."""
    _LOGGER.warning("YAML configuration is deprecated. Please use the UI to configure Loggamera integration.")
    
    session = async_get_clientsession(hass)
    sensors = []
    
    for sensor_config in config["sensors"]:
        scan_interval = timedelta(seconds=sensor_config["scan_interval"])
        
        coordinator = LoggameraDataUpdateCoordinator(
            hass, session, sensor_config["location_id"], scan_interval
        )
        await coordinator.async_config_entry_first_refresh()
        
        sensors.append(LoggameraTemperatureSensor(
            coordinator,
            sensor_config["name"],
            sensor_config["location_id"],
            sensor_config["unit"],
            sensor_config["scan_interval"]
        ))
    
    async_add_entities(sensors, True)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Loggamera sensors from config entry."""
    session = async_get_clientsession(hass)
    
    # Get configuration from config entry
    config_data = hass.data[DOMAIN][config_entry.entry_id]
    selected_sensors = config_data["sensors"]
    scan_interval_seconds = config_data["scan_interval"]
    scan_interval = timedelta(seconds=scan_interval_seconds)
    
    sensors = []
    
    for sensor_id in selected_sensors:
        if sensor_id in SENSORS:
            coordinator = LoggameraDataUpdateCoordinator(
                hass, session, sensor_id, scan_interval
            )
            await coordinator.async_config_entry_first_refresh()
            
            sensors.append(LoggameraTemperatureSensor(
                coordinator,
                f"{SENSORS[sensor_id]} Temperature",
                sensor_id,
                TEMP_CELSIUS,
                scan_interval_seconds
            ))
    
    async_add_entities(sensors, True)

class LoggameraDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator for fetching data from Loggamera."""
    
    def __init__(self, hass, session, location_id, scan_interval):
        """Initialize the coordinator."""
        self.session = session
        self.location_id = location_id
        super().__init__(
            hass,
            _LOGGER,
            name=f"loggamera_{location_id}",
            update_interval=scan_interval,
        )
    
    async def _async_update_data(self):
        """Fetch data from Loggamera."""
        try:
            url = "https://portal.loggamera.se/PublicViews/OverviewInside"
            data = {"id": self.location_id}
            
            async with self.session.post(url, data=data, timeout=30) as response:
                if response.status != 200:
                    raise UpdateFailed(f"HTTP {response.status}")
                
                html = await response.text()
                
                # Extract temperature with regex
                temp_pattern = r'data-value="(-?\d+\.?\d*)"'
                matches = re.findall(temp_pattern, html)
                
                for match in matches:
                    temp = float(match)
                    # Sanity check for reasonable water temperature
                    if -5 <= temp <= 40:
                        _LOGGER.debug(f"Retrieved temperature {temp}°C for location {self.location_id}")
                        return temp
                
                raise UpdateFailed("No valid temperature found in response")
                
        except Exception as err:
            _LOGGER.error(f"Error communicating with Loggamera API: {err}")
            raise UpdateFailed(f"Error communicating with API: {err}")

class LoggameraTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Loggamera temperature sensor."""
    
    def __init__(self, coordinator, name, location_id, unit, scan_interval):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = name
        self._location_id = location_id
        self._unit = unit
        self._scan_interval = scan_interval
        self._attr_unique_id = f"loggamera_{location_id}"
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data
    
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit
    
    @property
    def device_class(self):
        """Return the device class."""
        return "temperature"
    
    @property
    def state_class(self):
        """Return the state class."""
        return "measurement"
    
    @property
    def icon(self):
        """Return the icon."""
        return "mdi:waves"
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"location_{self._location_id}")},
            name=f"Loggamera {SENSORS.get(self._location_id, f'Location {self._location_id}')}",
            manufacturer="Loggamera",
            model="Temperature Sensor",
            configuration_url="https://portal.loggamera.se/",
        )
    
    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "location_id": self._location_id,
            "source": "Loggamera Portal",
            "scan_interval_seconds": self._scan_interval,
            "api_endpoint": "https://portal.loggamera.se/PublicViews/OverviewInside",
        } 
"""
Loggamera Temperature Sensor Integration för Home Assistant
Placera denna fil i custom_components/loggamera/sensor.py
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

_LOGGER = logging.getLogger(__name__)

DOMAIN = "loggamera"
SCAN_INTERVAL = timedelta(minutes=5)

PLATFORM_SCHEMA = vol.Schema({
    vol.Required("platform"): "loggamera",
    vol.Required("sensors"): vol.All(cv.ensure_list, [
        vol.Schema({
            vol.Required("name"): cv.string,
            vol.Required("location_id"): cv.positive_int,
            vol.Optional("unit", default=TEMP_CELSIUS): cv.string,
        })
    ])
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Sätt upp Loggamera-sensorer."""
    session = async_get_clientsession(hass)
    
    sensors = []
    for sensor_config in config["sensors"]:
        coordinator = LoggameraDataUpdateCoordinator(
            hass, session, sensor_config["location_id"]
        )
        await coordinator.async_config_entry_first_refresh()
        
        sensors.append(LoggameraTemperatureSensor(
            coordinator,
            sensor_config["name"],
            sensor_config["location_id"],
            sensor_config["unit"]
        ))
    
    async_add_entities(sensors, True)

class LoggameraDataUpdateCoordinator(DataUpdateCoordinator):
    """Koordinator för att hämta data från Loggamera."""
    
    def __init__(self, hass, session, location_id):
        """Initiera koordinatorn."""
        self.session = session
        self.location_id = location_id
        super().__init__(
            hass,
            _LOGGER,
            name=f"loggamera_{location_id}",
            update_interval=SCAN_INTERVAL,
        )
    
    async def _async_update_data(self):
        """Hämta data från Loggamera."""
        try:
            url = "https://portal.loggamera.se/PublicViews/OverviewInside"
            data = {"id": self.location_id}
            
            async with self.session.post(url, data=data, timeout=30) as response:
                if response.status != 200:
                    raise UpdateFailed(f"HTTP {response.status}")
                
                html = await response.text()
                
                # Extrahera temperatur med regex
                temp_pattern = r'data-value="(-?\d+\.?\d*)"'
                matches = re.findall(temp_pattern, html)
                
                for match in matches:
                    temp = float(match)
                    # Sanity check
                    if -5 <= temp <= 40:
                        return temp
                
                raise UpdateFailed("Ingen giltig temperatur hittades")
                
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

class LoggameraTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Loggamera temperatursensor."""
    
    def __init__(self, coordinator, name, location_id, unit):
        """Initiera sensorn."""
        super().__init__(coordinator)
        self._name = name
        self._location_id = location_id
        self._unit = unit
        self._attr_unique_id = f"loggamera_{location_id}"
    
    @property
    def name(self):
        """Returnera sensorns namn."""
        return self._name
    
    @property
    def state(self):
        """Returnera sensorns tillstånd."""
        return self.coordinator.data
    
    @property
    def unit_of_measurement(self):
        """Returnera enhet."""
        return self._unit
    
    @property
    def device_class(self):
        """Returnera device class."""
        return "temperature"
    
    @property
    def state_class(self):
        """Returnera state class."""
        return "measurement"
    
    @property
    def icon(self):
        """Returnera ikon."""
        return "mdi:waves"
    
    @property
    def device_info(self) -> DeviceInfo:
        """Returnera device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"location_{self._location_id}")},
            name=f"Loggamera Location {self._location_id}",
            manufacturer="Loggamera",
            model="Temperature Sensor",
        )
    
    @property
    def extra_state_attributes(self):
        """Returnera extra attribut."""
        return {
            "location_id": self._location_id,
            "source": "Loggamera Portal",
        } 
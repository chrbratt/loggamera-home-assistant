"""
Enhanced Loggamera Integration för Home Assistant
Placera i custom_components/loggamera/

Förbättringar:
- Konfigurerbar med config flow
- Stöd för flera sensor typer
- Robustare felhantering
- Testbar arkitektur
- Bättre logging
"""

import asyncio
import aiohttp
import re
import logging
from datetime import timedelta, datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

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

_LOGGER = logging.getLogger(__name__)

DOMAIN = "loggamera"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 5

# Sensor type definitions
@dataclass
class SensorConfig:
    """Configuration for different sensor types."""
    name: str
    pattern: str
    unit: str
    device_class: str
    icon: str
    validation_range: tuple

SENSOR_TYPES = {
    "temperature": SensorConfig(
        name="Temperature",
        pattern=r'data-value="(-?\d+\.?\d*)"',
        unit=TEMP_CELSIUS,
        device_class="temperature",
        icon="mdi:waves",
        validation_range=(-5, 40)
    ),
    "humidity": SensorConfig(
        name="Humidity",
        pattern=r'humidity["\s]*:\s*["\s]*(\d+\.?\d*)',
        unit="%",
        device_class="humidity",
        icon="mdi:water-percent",
        validation_range=(0, 100)
    ),
}

class LoggameraApiClient:
    """API client for Loggamera platform."""
    
    def __init__(self, session: aiohttp.ClientSession, base_url: str = None):
        self.session = session
        self.base_url = base_url or "https://portal.loggamera.se"
        
    async def fetch_data(self, location_id: int, endpoint: str = "PublicViews/OverviewInside") -> str:
        """Fetch raw data from Loggamera API with retry logic."""
        url = f"{self.base_url}/{endpoint}"
        data = {"id": location_id}
        
        for attempt in range(MAX_RETRIES):
            try:
                _LOGGER.debug(f"Fetching data for location {location_id}, attempt {attempt + 1}")
                
                async with self.session.post(url, data=data, timeout=DEFAULT_TIMEOUT) as response:
                    if response.status == 200:
                        content = await response.text()
                        _LOGGER.debug(f"Successfully fetched {len(content)} characters")
                        return content
                    else:
                        _LOGGER.warning(f"HTTP {response.status} for location {location_id}")
                        
            except asyncio.TimeoutError:
                _LOGGER.warning(f"Timeout on attempt {attempt + 1} for location {location_id}")
            except Exception as err:
                _LOGGER.error(f"Error on attempt {attempt + 1}: {err}")
                
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
                
        raise UpdateFailed(f"Failed to fetch data after {MAX_RETRIES} attempts")

class LoggameraDataParser:
    """Parser for extracting sensor data from Loggamera responses."""
    
    @staticmethod
    def parse_sensor_data(html: str, sensor_type: str) -> Optional[float]:
        """Parse sensor data from HTML using configured patterns."""
        if sensor_type not in SENSOR_TYPES:
            _LOGGER.error(f"Unknown sensor type: {sensor_type}")
            return None
            
        config = SENSOR_TYPES[sensor_type]
        matches = re.findall(config.pattern, html)
        
        for match in matches:
            try:
                value = float(match)
                min_val, max_val = config.validation_range
                
                if min_val <= value <= max_val:
                    _LOGGER.debug(f"Parsed {sensor_type}: {value}{config.unit}")
                    return value
                else:
                    _LOGGER.warning(f"Value {value} outside valid range {config.validation_range}")
                    
            except ValueError as err:
                _LOGGER.warning(f"Failed to parse value '{match}': {err}")
                
        _LOGGER.warning(f"No valid {sensor_type} data found in response")
        return None

class LoggameraDataUpdateCoordinator(DataUpdateCoordinator):
    """Enhanced coordinator with better error handling and caching."""
    
    def __init__(self, hass: HomeAssistant, api_client: LoggameraApiClient, 
                 location_id: int, sensor_type: str, update_interval: timedelta = None):
        self.api_client = api_client
        self.location_id = location_id
        self.sensor_type = sensor_type
        self.parser = LoggameraDataParser()
        self._last_successful_update: Optional[datetime] = None
        self._cached_data: Optional[float] = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"loggamera_{location_id}_{sensor_type}",
            update_interval=update_interval or DEFAULT_SCAN_INTERVAL,
        )
    
    async def _async_update_data(self) -> float:
        """Fetch and parse data with enhanced error handling."""
        try:
            html = await self.api_client.fetch_data(self.location_id)
            value = self.parser.parse_sensor_data(html, self.sensor_type)
            
            if value is not None:
                self._last_successful_update = datetime.now()
                self._cached_data = value
                return value
            else:
                # Return cached data if parsing fails but we have recent data
                if (self._cached_data is not None and 
                    self._last_successful_update and 
                    (datetime.now() - self._last_successful_update).total_seconds() < 1800):  # 30 min
                    
                    _LOGGER.info(f"Using cached data for location {self.location_id}")
                    return self._cached_data
                    
                raise UpdateFailed(f"No valid {self.sensor_type} data available")
                
        except Exception as err:
            # Enhanced error context
            error_msg = f"Failed to update {self.sensor_type} for location {self.location_id}: {err}"
            _LOGGER.error(error_msg)
            raise UpdateFailed(error_msg)

class LoggameraSensor(CoordinatorEntity, SensorEntity):
    """Enhanced Loggamera sensor with better configurability."""
    
    def __init__(self, coordinator: LoggameraDataUpdateCoordinator, 
                 name: str, location_id: int, sensor_type: str):
        super().__init__(coordinator)
        self._name = name
        self._location_id = location_id
        self._sensor_type = sensor_type
        self._config = SENSOR_TYPES[sensor_type]
        self._attr_unique_id = f"loggamera_{location_id}_{sensor_type}"
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def state(self) -> Optional[float]:
        return self.coordinator.data
    
    @property
    def unit_of_measurement(self) -> str:
        return self._config.unit
    
    @property
    def device_class(self) -> str:
        return self._config.device_class
    
    @property
    def state_class(self) -> str:
        return "measurement"
    
    @property
    def icon(self) -> str:
        return self._config.icon
    
    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"location_{self._location_id}")},
            name=f"Loggamera Location {self._location_id}",
            manufacturer="Loggamera",
            model="IoT Sensor Hub",
            sw_version="2.0",
        )
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        attrs = {
            "location_id": self._location_id,
            "sensor_type": self._sensor_type,
            "source": "Loggamera Portal",
        }
        
        # Add diagnostic info
        if hasattr(self.coordinator, '_last_successful_update'):
            if self.coordinator._last_successful_update:
                attrs["last_update"] = self.coordinator._last_successful_update.isoformat()
                
        return attrs

# Platform setup function
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Loggamera sensors from config entry."""
    config = entry.data
    session = async_get_clientsession(hass)
    api_client = LoggameraApiClient(session, config.get("base_url"))
    
    sensors = []
    for sensor_config in config.get("sensors", []):
        coordinator = LoggameraDataUpdateCoordinator(
            hass,
            api_client,
            sensor_config["location_id"],
            sensor_config.get("sensor_type", "temperature"),
            timedelta(minutes=sensor_config.get("update_interval", 5))
        )
        
        await coordinator.async_config_entry_first_refresh()
        
        sensors.append(LoggameraSensor(
            coordinator,
            sensor_config["name"],
            sensor_config["location_id"],
            sensor_config.get("sensor_type", "temperature")
        ))
    
    async_add_entities(sensors, True)

# Legacy platform support
PLATFORM_SCHEMA = vol.Schema({
    vol.Required("platform"): "loggamera",
    vol.Required("sensors"): vol.All(cv.ensure_list, [
        vol.Schema({
            vol.Required("name"): cv.string,
            vol.Required("location_id"): cv.positive_int,
            vol.Optional("sensor_type", default="temperature"): vol.In(SENSOR_TYPES.keys()),
            vol.Optional("update_interval", default=5): cv.positive_int,
        })
    ]),
    vol.Optional("base_url", default="https://portal.loggamera.se"): cv.url,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Legacy platform setup for backwards compatibility."""
    session = async_get_clientsession(hass)
    api_client = LoggameraApiClient(session, config.get("base_url"))
    
    sensors = []
    for sensor_config in config["sensors"]:
        coordinator = LoggameraDataUpdateCoordinator(
            hass,
            api_client,
            sensor_config["location_id"],
            sensor_config.get("sensor_type", "temperature"),
            timedelta(minutes=sensor_config.get("update_interval", 5))
        )
        
        await coordinator.async_config_entry_first_refresh()
        
        sensors.append(LoggameraSensor(
            coordinator,
            sensor_config["name"],
            sensor_config["location_id"],
            sensor_config.get("sensor_type", "temperature")
        ))
    
    async_add_entities(sensors, True) 
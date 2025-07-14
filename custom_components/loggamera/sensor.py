"""Sensor entities for Loggamera integration."""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSORS, get_device_info

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Loggamera sensors from config entry."""
    
    # Get session for API calls
    session = async_get_clientsession(hass)
    
    # Get configuration
    config_data = hass.data[DOMAIN][config_entry.entry_id]
    selected_sensors = config_data["sensors"]
    scan_interval_seconds = config_data["scan_interval"]
    scan_interval = timedelta(seconds=scan_interval_seconds)
    
    # Create shared data manager
    data_manager = LoggameraDataManager(hass, session, selected_sensors, scan_interval)
    
    # Initial data fetch
    try:
        await data_manager.async_update_data()
        _LOGGER.info("Initial data fetch successful")
    except Exception as err:
        _LOGGER.warning(f"Initial data fetch failed: {err}")
    
    # Create entities
    entities = []
    
    # Add temperature sensors for selected lakes
    for sensor_id in selected_sensors:
        if sensor_id in SENSORS:
            entities.append(LoggameraTemperatureSensor(
                data_manager,
                sensor_id,
                SENSORS[sensor_id]
            ))
    
    # Add last updated sensor
    entities.append(LoggameraLastUpdatedSensor(data_manager))
    
    # Add status sensor
    entities.append(LoggameraStatusSensor(data_manager, config_entry))
    
    # Add all entities
    async_add_entities(entities, True)

class LoggameraDataManager:
    """Manages data fetching for all Loggamera sensors."""
    
    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession, sensor_ids: list, scan_interval: timedelta):
        """Initialize data manager."""
        self.hass = hass
        self.session = session
        self.sensor_ids = sensor_ids
        self.scan_interval = scan_interval
        self.data = {}
        self.last_update = None
        self._update_lock = asyncio.Lock()
        
        # Status tracking
        self.status = "Starting..."
        self.last_error = None
        self.successful_updates = 0
        self.failed_updates = 0
        
    async def async_update_data(self):
        """Fetch data from all sensors."""
        async with self._update_lock:
            new_data = {}
            errors = []
            success_count = 0
            
            for sensor_id in self.sensor_ids:
                try:
                    temperature = await self._fetch_temperature(sensor_id)
                    new_data[sensor_id] = {
                        'temperature': temperature,
                        'available': True,
                        'last_update': datetime.now()
                    }
                    success_count += 1
                    _LOGGER.debug(f"Successfully fetched {temperature}°C for sensor {sensor_id}")
                except Exception as err:
                    _LOGGER.warning(f"Failed to fetch data for sensor {sensor_id}: {err}")
                    errors.append(f"Sensor {sensor_id}: {str(err)}")
                    new_data[sensor_id] = {
                        'temperature': None,
                        'available': False,
                        'last_update': self.data.get(sensor_id, {}).get('last_update')
                    }
            
            # Update status
            if success_count == len(self.sensor_ids):
                self.status = "OK"
                self.last_error = None
                self.successful_updates += 1
            elif success_count > 0:
                self.status = "Partial"
                self.last_error = f"Some sensors failed: {'; '.join(errors)}"
                self.failed_updates += 1
            else:
                self.status = "Error"
                self.last_error = f"All sensors failed: {'; '.join(errors)}"
                self.failed_updates += 1
            
            self.data = new_data
            self.last_update = datetime.now()
            
            return self.data
    
    async def _fetch_temperature(self, location_id: int) -> float:
        """Fetch temperature for a specific location."""
        url = "https://portal.loggamera.se/PublicViews/OverviewInside"
        data = {"id": location_id}
        
        try:
            async with self.session.post(url, data=data, timeout=10) as response:
                response.raise_for_status()
                html = await response.text()
                
                soup = BeautifulSoup(html, 'html.parser')
                temp_elements = soup.find_all(class_='display-value')
                
                for element in temp_elements:
                    temp_text = element.get_text().strip()
                    temp_match = re.search(r'([-+]?\d*\.?\d+)', temp_text)
                    if temp_match:
                        temp_value = float(temp_match.group(1))
                        if -5 <= temp_value <= 40:  # Reasonable range
                            return temp_value
                
                raise UpdateFailed("No valid temperature found in response")
                
        except asyncio.TimeoutError:
            raise UpdateFailed("Timeout while fetching data")
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Network error: {err}")

class LoggameraTemperatureSensor(SensorEntity):
    """Temperature sensor for a specific lake."""
    
    def __init__(self, data_manager: LoggameraDataManager, sensor_id: int, lake_name: str):
        """Initialize temperature sensor."""
        self.data_manager = data_manager
        self.sensor_id = sensor_id
        self.lake_name = lake_name
        
        self._attr_name = f"{lake_name} Badtemperatur"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}_temperature"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_icon = "mdi:thermometer-water"
        
    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return get_device_info()
    
    @property
    def native_value(self) -> float | None:
        """Return the temperature value."""
        sensor_data = self.data_manager.data.get(self.sensor_id, {})
        return sensor_data.get('temperature')
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        sensor_data = self.data_manager.data.get(self.sensor_id, {})
        return sensor_data.get('available', False)
    
    async def async_update(self) -> None:
        """Update the sensor."""
        await self.data_manager.async_update_data()

class LoggameraLastUpdatedSensor(SensorEntity):
    """Sensor showing when data was last updated."""
    
    def __init__(self, data_manager: LoggameraDataManager):
        """Initialize last updated sensor."""
        self.data_manager = data_manager
        
        self._attr_name = "Senast Uppdaterad"
        self._attr_unique_id = f"{DOMAIN}_last_updated"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-check"
        
    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return get_device_info()
    
    @property
    def native_value(self) -> datetime | None:
        """Return the last update timestamp."""
        return self.data_manager.last_update
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.data_manager.last_update is not None
    
    async def async_update(self) -> None:
        """Update the sensor."""
        # Data manager updates timestamps automatically
        pass

class LoggameraStatusSensor(SensorEntity):
    """Sensor showing system status and errors."""
    
    def __init__(self, data_manager: LoggameraDataManager, config_entry: ConfigEntry):
        """Initialize status sensor."""
        self.data_manager = data_manager
        self._config_entry = config_entry
        
        self._attr_unique_id = f"{DOMAIN}_status"
        self._attr_icon = "mdi:check-network"
    
    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        debug_mode = self._config_entry.data.get("debug_mode", False)
        if debug_mode:
            return "System Status (DEBUG)"
        return "System Status"
        
    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return get_device_info()
    
    @property
    def native_value(self) -> str:
        """Return the status value."""
        debug_mode = self._config_entry.data.get("debug_mode", False)
        
        if debug_mode:
            # Show detailed status in debug mode
            status = self.data_manager.status
            success = self.data_manager.successful_updates
            failed = self.data_manager.failed_updates
            return f"{status} ({success}✓/{failed}✗)"
        
        return self.data_manager.status
    
    @property
    def icon(self) -> str:
        """Return icon based on status."""
        if self.data_manager.status == "OK":
            return "mdi:check-circle"
        elif self.data_manager.status == "Partial":
            return "mdi:alert-circle"
        elif self.data_manager.status == "Error":
            return "mdi:close-circle"
        else:
            return "mdi:help-circle"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        # Check if debug mode is enabled
        debug_mode = self._config_entry.data.get("debug_mode", False)
        
        # Basic attributes always shown
        attrs = {
            "last_update": self.data_manager.last_update,
            "update_interval_seconds": self.data_manager.scan_interval.total_seconds(),
        }
        
        # Debug attributes only shown when debug mode is on
        if debug_mode:
            attrs.update({
                "lyckade_uppdateringar": self.data_manager.successful_updates,
                "misslyckade_uppdateringar": self.data_manager.failed_updates,
            })
            
            if self.data_manager.last_error:
                attrs["last_error"] = self.data_manager.last_error
                
            # Add individual sensor debug status
            for sensor_id, sensor_data in self.data_manager.data.items():
                sensor_name = SENSORS.get(sensor_id, f"Sensor {sensor_id}")
                attrs[f"{sensor_name.lower().replace(' ', '_')}_status"] = (
                    "OK" if sensor_data.get('available', False) else "Error"
                )
                if sensor_data.get('temperature') is not None:
                    attrs[f"{sensor_name.lower().replace(' ', '_')}_temperatur"] = sensor_data['temperature']
        
        return attrs
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return True  # Status sensor is always available
    
    async def async_update(self) -> None:
        """Update the sensor."""
        # Status is updated by data manager
        pass 
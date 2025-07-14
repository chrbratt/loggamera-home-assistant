"""Sensor entities for Loggamera integration."""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from homeassistant.util import dt as dt_util
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSORS, DEVICE_IDENTIFIER, DEVICE_NAME, DEVICE_MANUFACTURER, DEVICE_MODEL, DEVICE_SW_VERSION

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
    
    # Create coordinator for managing updates
    coordinator = LoggameraDataCoordinator(hass, session, selected_sensors, scan_interval)
    
    # Initial data fetch
    try:
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.info("Initial data fetch successful")
    except Exception as err:
        _LOGGER.warning(f"Initial data fetch failed: {err}")
    
    # Create entities
    entities = []
    
    # Add temperature sensors for selected lakes
    for sensor_id in selected_sensors:
        if sensor_id in SENSORS:
            entities.append(LoggameraTemperatureSensor(
                coordinator,
                sensor_id,
                SENSORS[sensor_id]
            ))
    
    # Add last updated sensor
    entities.append(LoggameraLastUpdatedSensor(coordinator))
    
    # Add status sensor
    entities.append(LoggameraStatusSensor(coordinator, config_entry))
    
    # Store entities in hass.data for number entity to access
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["entities"] = entities
    hass.data[DOMAIN]["coordinator"] = coordinator
    
    # Add all entities
    async_add_entities(entities, True)

class LoggameraDataCoordinator(DataUpdateCoordinator):
    """Manages data fetching for all Loggamera sensors."""
    
    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession, sensor_ids: list, scan_interval: timedelta):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )
        self.session = session
        self.sensor_ids = sensor_ids
        self.data = {}
        self.last_update = None
        
        # Status tracking
        self.status = "Starting..."
        self.last_error = None
        self.successful_updates = 0
        self.failed_updates = 0
        
    async def _async_update_data(self):
        """Fetch data from all sensors."""
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
        self.last_update = dt_util.now()
        
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

class LoggameraTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Temperature sensor for a specific lake."""
    
    def __init__(self, coordinator: LoggameraDataCoordinator, sensor_id: int, lake_name: str):
        """Initialize temperature sensor."""
        super().__init__(coordinator)
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
        return DeviceInfo(
            identifiers={(DOMAIN, DEVICE_IDENTIFIER)},
            name=DEVICE_NAME,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
            sw_version=DEVICE_SW_VERSION,
        )
    
    @property
    def native_value(self) -> float | None:
        """Return the temperature value."""
        sensor_data = self.coordinator.data.get(self.sensor_id, {})
        return sensor_data.get('temperature')
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        sensor_data = self.coordinator.data.get(self.sensor_id, {})
        return sensor_data.get('available', False)

class LoggameraLastUpdatedSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing when data was last updated."""
    
    def __init__(self, coordinator: LoggameraDataCoordinator):
        """Initialize last updated sensor."""
        super().__init__(coordinator)
        
        self._attr_name = "Senast Uppdaterad"
        self._attr_unique_id = f"{DOMAIN}_last_updated"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-check"
        
    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, DEVICE_IDENTIFIER)},
            name=DEVICE_NAME,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
            sw_version=DEVICE_SW_VERSION,
        )
    
    @property
    def native_value(self) -> datetime | None:
        """Return the last update timestamp."""
        return self.coordinator.last_update
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update is not None

class LoggameraStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing system status and errors."""
    
    def __init__(self, coordinator: LoggameraDataCoordinator, config_entry: ConfigEntry):
        """Initialize status sensor."""
        super().__init__(coordinator)
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
        return DeviceInfo(
            identifiers={(DOMAIN, DEVICE_IDENTIFIER)},
            name=DEVICE_NAME,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
            sw_version=DEVICE_SW_VERSION,
        )
    
    @property
    def native_value(self) -> str:
        """Return the status value."""
        debug_mode = self._config_entry.data.get("debug_mode", False)
        
        if debug_mode:
            # Show detailed status in debug mode
            status = self.coordinator.status
            success = self.coordinator.successful_updates
            failed = self.coordinator.failed_updates
            return f"{status} ({success}✓/{failed}✗)"
        
        return self.coordinator.status
    
    @property
    def icon(self) -> str:
        """Return icon based on status."""
        if self.coordinator.status == "OK":
            return "mdi:check-circle"
        elif self.coordinator.status == "Partial":
            return "mdi:alert-circle"
        elif self.coordinator.status == "Error":
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
            "senast_uppdaterad": self.coordinator.last_update,
            "uppdateringsintervall_sekunder": self.coordinator.update_interval.total_seconds(),
        }
        
        # Debug attributes only shown when debug mode is on
        if debug_mode:
            attrs.update({
                "lyckade_uppdateringar": self.coordinator.successful_updates,
                "misslyckade_uppdateringar": self.coordinator.failed_updates,
            })
            
            if self.coordinator.last_error:
                attrs["senaste_fel"] = self.coordinator.last_error
                
            # Add individual sensor debug status with clean names
            for sensor_id, sensor_data in self.coordinator.data.items():
                sensor_name = SENSORS.get(sensor_id, f"Sensor {sensor_id}")
                clean_name = sensor_name.replace(" ", "_").lower()
                attrs[f"{clean_name}_status"] = (
                    "OK" if sensor_data.get('available', False) else "Fel"
                )
                if sensor_data.get('temperature') is not None:
                    attrs[f"{clean_name}_temperatur"] = f"{sensor_data['temperature']}°C"
        
        return attrs
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return True  # Status sensor is always available 
"""Switch entities for Loggamera integration."""

import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, DEVICE_IDENTIFIER, DEVICE_NAME, DEVICE_MANUFACTURER, DEVICE_MODEL, DEVICE_SW_VERSION

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Loggamera switch entities."""
    
    # Create debug switch entity
    async_add_entities([LoggameraDebugSwitch(config_entry)], True)

class LoggameraDebugSwitch(SwitchEntity):
    """Switch entity for enabling debug mode."""

    def __init__(self, config_entry: ConfigEntry):
        """Initialize the switch entity."""
        self._config_entry = config_entry
        self._attr_name = "Debug Läge"
        self._attr_unique_id = f"{DOMAIN}_debug_mode"
        self._attr_icon = "mdi:bug"
        
        # Get initial state from config entry (default off)
        self._is_on = config_entry.data.get("debug_mode", False)

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
    def is_on(self) -> bool:
        """Return true if debug mode is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on debug mode."""
        # Update config entry data
        new_data = dict(self._config_entry.data)
        new_data["debug_mode"] = True
        
        self.hass.config_entries.async_update_entry(
            self._config_entry, data=new_data
        )
        
        self._is_on = True
        self.async_write_ha_state()
        
        _LOGGER.info("Debug mode activated - detailed status information enabled")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off debug mode."""
        # Update config entry data
        new_data = dict(self._config_entry.data)
        new_data["debug_mode"] = False
        
        self.hass.config_entries.async_update_entry(
            self._config_entry, data=new_data
        )
        
        self._is_on = False
        self.async_write_ha_state()
        
        _LOGGER.info("Debug mode deactivated - simplified status view") 
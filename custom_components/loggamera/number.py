"""Number entities for Loggamera integration."""

import logging
from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Loggamera number entities."""
    
    # Create update interval entity
    async_add_entities([LoggameraUpdateIntervalNumber(config_entry)], True)

class LoggameraUpdateIntervalNumber(NumberEntity):
    """Number entity for configuring update interval."""

    def __init__(self, config_entry: ConfigEntry):
        """Initialize the number entity."""
        self._config_entry = config_entry
        self._attr_name = "Uppdateringsintervall"
        self._attr_unique_id = f"{DOMAIN}_update_interval"
        self._attr_native_min_value = 60  # 1 minute
        self._attr_native_max_value = 86400  # 24 hours  
        self._attr_native_step = 60  # 1 minute steps
        self._attr_native_unit_of_measurement = "sekunder"
        self._attr_mode = "box"
        self._attr_icon = "mdi:timer-cog"
        
        # Get current value from config entry
        current_interval = config_entry.data.get("scan_interval", 300)
        self._attr_native_value = current_interval

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, "hjo_energi_badtemperaturer")},
            name="Hjo Energi Badtemperaturer",
            manufacturer="Hjo Energi AB",
            model="Loggamera Temperatursensorer",
            sw_version="1.0.0",
        )

    async def async_set_native_value(self, value: float) -> None:
        """Update the scan interval."""
        # Update config entry data
        new_data = dict(self._config_entry.data)
        new_data["scan_interval"] = int(value)
        
        self.hass.config_entries.async_update_entry(
            self._config_entry, data=new_data
        )
        
        self._attr_native_value = value
        self.async_write_ha_state()
        
        _LOGGER.info(f"Updated scan interval to {int(value)} seconds")
        
        # Notify user that restart may be needed for full effect
        self.hass.components.persistent_notification.async_create(
            f"Uppdateringsintervall ändrat till {int(value/60)} minuter. "
            "Starta om integrationen för full effekt.",
            title="Badtemperaturer Hjo Energi",
            notification_id=f"{DOMAIN}_interval_changed"
        ) 
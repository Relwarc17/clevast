"""ClevastEntity class"""
from .entity import ClevastEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.humidifier import HumidifierEntity
from homeassistant.core import callback


from .const import DOMAIN
from .const import NAME
from .const import ICON

import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)

async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([ClevastHumidifier(coordinator, entry)])

class ClevastHumidifier(ClevastEntity, HumidifierEntity):

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def name(self):
        return f"{NAME} - Humidifier"

    @property
    def icon(self):
        return ICON

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self.coordinator.data.get("title", "") == "foo"
    
    async def async_set_mode(self, mode):
        """Set new target preset mode."""
        return True

    async def async_set_humidity(self, humidity):
        """Set new target humidity."""
        return True
    
    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        return True

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        return True

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data[self.config_entry]["state"]
        self.async_write_ha_state()

       

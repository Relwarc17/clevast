"""ClevastEntity class"""

from typing import Any, cast
from .entity import ClevastEntity
from homeassistant.components.humidifier import (
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.core import callback


from .const import DOMAIN
from .const import NAME
from .const import ICON

import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)

#async def async_setup_entry(hass, entry, async_add_devices):
async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    #async_add_devices([ClevastHumidifier(coordinator, entry)])
    for device in coordinator._devices:
        if "productType" not in device or device["productType"] != "HUMIDIFIER":
            continue
        device["version"] = "2.0.11"
        async_add_entities(
            ClevastHumidifier(coordinator, device["deviceId"])
        )

class ClevastHumidifier(ClevastEntity, HumidifierEntity):

    def __init__(self, coordinator, idx):
        super().__init__(coordinator, context=idx)
        #self._coordinator = coordinator
        #self._idx = idx
        self._attr_min_humidity: float = 40
        self._attr_max_humidity: float = 70
        self._attr_min_mist_level: 1
        self._attr_max_mist_level: 8
        self._attr_device_class = HumidifierDeviceClass.HUMIDIFIER
        self._attr_supported_features = HumidifierEntityFeature.MODES

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self._idx

    @property
    def name(self):
        return f"{NAME} - Humidifier"

    @property
    def icon(self):
        return ICON

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._coordinator.data.get("status", 0) == 1

    @property
    def get_current_humidity(self) -> float | None:
        return cast("float", self._coordinator.data.get("current_humidity", 0))
    
    @property
    def get_current_mist_level(self) -> float | None:
        return cast("float", self._coordinator.data.get("mist_level", 0))

    @property
    def get_target_humidity(self) -> float:
        return cast("float", self._coordinator.data.get("humidity", 0))

    async def async_set_mist_level(self, mist_level: int) -> None:
        if mist_level < self._attr_min_mist_level or mist_level > self._attr_max_mist_level:
            return
        c_h = self.get_current_humidity()
        args = f'{{"humidity":{c_h},"switch":1,"mist_level":{mist_level}}}'
        await self._coordinator._my_api.sync_data(self._idx, args)

    async def async_set_humidity(self, humidity: int) -> None:
        if humidity < self._attr_min_humidity or humidity > self._attr_max_humidity:
            return
        c_m_l = self.get_current_mist_level()
        args = f'{{"humidity":{humidity},"switch":1,"mist_level":{c_m_l}}}'
        await self._coordinator._my_api.sync_data(self._idx, args)

    async def async_turn_on(self, **kwargs: Any) -> None:  
        #c_m_l = self.get_current_mist_level()
        #c_h = self.get_current_humidity()
        #args = f'{{"humidity":{c_h},"switch":1,"mist_level":{c_m_l}}}'
        args = '{"switch":1}'
        self._coordinator._my_api.sync_data(self._idx, args)

    async def async_turn_off(self, **kwargs: Any) -> None:
        args = '{"switch":0}'
        await self._coordinator._my_api.sync_data(self._idx, args)

    def update_state(self, status: Any) -> None:
        """Midea Humidifier update state."""
        if not self.hass:
            _LOGGER.error("Humidifier update_state for %s [%s]", self.name, type(self))
        self.schedule_update_ha_state()
    
    async def async_set_mode(self, mode):
        """Set new target preset mode."""
        return True


    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data[self.config_entry]["status"]
        self.async_write_ha_state()

       

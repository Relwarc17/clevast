"""ClevastEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import ATTRIBUTION
from .const import DOMAIN
from .const import NAME
from .const import VERSION


class ClevastEntity(CoordinatorEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """
    def __init__(self, coordinator, idx):
        super().__init__(coordinator, context=idx)
        self._device_id = coordinator._devices[0]["deviceId"]
        self._device_name = coordinator._devices[0]["nickname"]
        self._state = None
        self._available = True
        self._device_type = coordinator._devices[0]["productType"].capitalize()
        self._coordinator = coordinator
        self._idx = idx

    @property
    def unique_id(self):
        """Return a unique ID for the switch."""
        return self._idx

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.unique_id)
            },
            name = self._device_name | "{NAME} - Humidifier - hardoced",
            manufacturer = NAME,
            model = self._coordinator._devices[0]["model"],
            model_id = self._coordinator._devices[0]["deviceId"],
            sw_version = str(self.coordinator.data.get("version")),
        )

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": str(self._coordinator.data.get("id")),
            "integration": DOMAIN,
        }

       

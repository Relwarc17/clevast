"""ClevastEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._device_id = coordinator._devices[0]["deviceId"]
        self._device_name = coordinator._devices[0]["nickname"]
        self._state = None
        self._available = True
        self._device_type = coordinator._devices[0]["productType"].capitalize()
        self._coordinaor = coordinator

    @property
    def unique_id(self):
        """Return a unique ID for the switch."""
        return (
            f"{self._config_entry.entry_id}_switch_{self._device_id}"
            if self._device_id
            else f"{self._config_entry.entry_id}_switch_{self._device_type}"
        )

    @property
    def device_info(self):
        """Return device information for linking with the device registry."""
        if not self._device_id or not self._device_name:
            return None

        return {
            "identifiers": {
                (DOMAIN, self._device_id)
            },  # Match the registered device ID
            "name": self._device_name,  # Use the dynamic deviceName
            "manufacturer": NAME,
            "model": f"Mars Hydro {self._device_type}",
        }
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": NAME,
            "model": VERSION,
            "manufacturer": NAME,
        }

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
        }

       

"""ClevastEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.humidifier import HumidifierEntity
from homeassistant.core import callback
from .humidifier import ClevastEntity

from .const import ATTRIBUTION
from .const import DOMAIN
from .const import NAME
from .const import VERSION


class ClevastHumidifier(ClevastEntity, HumidifierEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": NAME,
            "model": "",
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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data[self.config_entry]["state"]
        self.async_write_ha_state()

       

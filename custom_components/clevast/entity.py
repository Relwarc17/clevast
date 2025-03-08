"""ClevastEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.humidifier import HumidifierEntity
from homeassistant.core import callback

from .const import ATTRIBUTION
from .const import DOMAIN
from .const import NAME
from .const import VERSION


class ClevastEntity(CoordinatorEntity, HumidifierEntity):
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

    async def set_mode(self, mode):
        """Set new target preset mode."""
         # Do the turning off.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()


    async def set_humidity(self, humidity):
        """Set new target humidity."""
         # Do the turning off.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()

    async def turn_on(self, **kwargs):
        """Turn the device on."""
         # Do the turning on.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()

    async def turn_off(self, **kwargs):
        """Turn the device off."""
         # Do the turning off.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data[self.config_entry]["state"]
        self.async_write_ha_state()

       

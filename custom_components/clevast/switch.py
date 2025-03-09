"""Switch platform for Clevast."""
from homeassistant.components.switch import SwitchEntity

from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import ICON
from .const import SWITCH
from .entity import ClevastEntity


#async def async_setup_entry(hass, entry, async_add_devices):
async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    #async_add_devices([ClevastSwitch(coordinator, entry)])
    for device in coordinator._devices:
        if "productType" not in device or device["productType"] != "HUMIDIFIER":
            continue
        device["version"] = "2.0.11"
        async_add_entities(
            [ClevastSwitch(coordinator, device["deviceId"])]
        )


class ClevastSwitch(ClevastEntity, SwitchEntity):
    """clevast switch class."""

    def __init__(self, coordinator, idx):
        super().__init__(coordinator, idx)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f'{self._idx}-switch'
    
    @property
    def entity_id(self):
        """Return a unique ID to use for this entity."""
        return f"switch.{self.entity_id_base}_humidity"

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        args = '{"switch":1}'
        await self._coordinator._my_api.sync_data(self._idx, args)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        args = '{"switch":0}'
        await self._coordinator._my_api.sync_data(self._idx, args)
        await self.coordinator.async_request_refresh()

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self._device_name}_{SWITCH}"

    @property
    def icon(self):
        """Return the icon of this switch."""
        return ICON

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self.coordinator.data.get("status", 0) == 1

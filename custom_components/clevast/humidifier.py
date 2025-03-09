"""Example integration using DataUpdateCoordinator."""

from datetime import timedelta
import logging

import async_timeout

from .clevast_device import ClevastDevices

from homeassistant.components.humidifier import HumidifierEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .const import NAME
from .const import ICON
from .const import ATTRIBUTION

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Config entry example."""
    # assuming API object stored here by __init__.py
    my_api = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = MyCoordinator(hass, config_entry, my_api)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        ClevastHumidifier(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )


class MyCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, config_entry, my_api):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name = "My sensor",
            config_entry = config_entry,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval = timedelta(seconds=30),
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update = True
        )
        _LOGGER.info("Initializing Cordinator")
        self._platforms = []
        self._my_api = my_api
        self._config_entry = config_entry
        self._devices: ClevastDevices | list = list

    async def _async_setup(self) -> None:
        """Set up the coordinator

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        _LOGGER.info("Cordinator _async_setup")
        self._devices = await self._my_api.get_devices()


    async def _async_update_data(self) -> ...:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        """Update data via library."""
        try:
            _LOGGER.info("Coordinator _async_update_data before async_timeout")
            async with async_timeout.timeout(10):
                _LOGGER.info("Coordinator _async_update_data after async_timeout")
                await self._my_api.login()
                listening_idx = set(self.async_contexts())
                _LOGGER.info("Listening idx: %s", listening_idx)
                #return await self.my_api.fetch_data(listening_idx)
                return await self._my_api.get_device_data(listening_idx)
        except Exception as exception:
            raise UpdateFailed() from exception


class ClevastHumidifier(CoordinatorEntity, HumidifierEntity):

    def __init__(self, coordinator, idx):
        super().__init__(coordinator, context=idx)
        self._coordinator = coordinator
        self._idx = idx
        
    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self._coordinator.config_entry.entry_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.unique_id)
            },
            name = self.name,
            manufacturer = NAME,
            model = self._coordinator._devices[0]["model"],
            model_id = self._coordinator._devices[0]["deviceId"],
            sw_version = "0.0.0",
        )

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": str(self._coordinator.data.get("id")),
            "integration": DOMAIN,
        }

    @property
    def name(self):
        return f"{NAME} - Humidifier"

    @property
    def icon(self):
        return ICON

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._coordinator.data.get("title", "") == "foo"
    
    async def async_set_mode(self, mode):
        """Set new target preset mode."""
        return True

    async def async_set_humidity(self, humidity):
        """Set new target humidity."""
        return True
    
    async def async_turn_on(self, **kwargs):
        """Turn the light on.

        Example method how to request data updates.
        """
        # Do the turning on.
        # ...

        # Update the data
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        return True

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self._coordinator.data[self._idx]["state"]
        self.async_write_ha_state()
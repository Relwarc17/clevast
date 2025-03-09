"""Example integration using DataUpdateCoordinator."""

from datetime import timedelta
import logging

import async_timeout

from .clevast_device import ClevastDevices
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)

class ClevastDataUpdateCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, config_entry, my_api):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name = DOMAIN,
            config_entry = config_entry,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval = SCAN_INTERVAL,
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update = False
        )
        _LOGGER.info("Initializing Cordinator")
        self._platforms = []
        self._my_api = my_api
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
                #listening_idx = set(self.async_contexts())
                #_LOGGER.info("Listening idx: %s", listening_idx)
                #return await self.my_api.fetch_data(listening_idx)
                listening_idx = self._devices[0]["deviceId"]
                args = '{"state_synch":1}'
                await self._my_api.sync_data(listening_idx, args)
                return await self._my_api.get_device_data(listening_idx)
        except Exception as exception:
            raise UpdateFailed() from exception


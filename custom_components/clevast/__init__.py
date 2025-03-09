"""
Custom integration to integrate Clevast with Home Assistant.

For more details about this integration, please refer to
https://github.com/Relwarc17/clevast
"""
import asyncio
import logging
import json
from datetime import timedelta

from .coordinator import ClevastDataUpdateCoordinator

from .humidifier import ClevastEntity

from .clevast_device import ClevastDeviceInfo, ClevastDevices
from homeassistant.config_entries import ConfigEntry
from homeassistant.core_config import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .api import ClevastApiClient
from .const import CONF_PASSWORD
from .const import CONF_USERNAME
from .const import DOMAIN
from .const import PLATFORMS
from .const import STARTUP_MESSAGE

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Config entry example."""
    # assuming API object stored here by __init__.py
    my_api = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = ClevastDataUpdateCoordinator(hass, config_entry, my_api)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    _LOGGER.info("Coordinator data: %s", json.dumps(coordinator.data, indent=2))
    async_add_entities(
        ClevastEntity(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)

    session = async_get_clientsession(hass)
    client = ClevastApiClient(username, password, session)
    hass.data[DOMAIN][entry.entry_id] = client
    coordinator = ClevastDataUpdateCoordinator(hass, entry)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    devices: ClevastDevices = client.get_devices()
    for device in devices:
       dev = ClevastDeviceInfo(device)
    #for platform in PLATFORMS:
    #    if entry.options.get(platform, True):
    #        coordinator._platforms.append(platform)
    #        hass.async_add_job(
    #            await hass.config_entries.async_forward_entry_setups(entry, platform)
    #        )

    entry.add_update_listener(async_reload_entry)
    return True



async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator._platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

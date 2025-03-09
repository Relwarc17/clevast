"""
Custom integration to integrate Clevast with Home Assistant.

For more details about this integration, please refer to
https://github.com/Relwarc17/clevast
"""
import asyncio
import logging
from datetime import timedelta

from .coordinator import ClevastDataUpdateCoordinator

from homeassistant.config_entries import ConfigEntry
from homeassistant.core_config import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import device_registry as dr

from .api import ClevastApiClient
from .const import CONF_PASSWORD
from .const import CONF_USERNAME
from .const import DOMAIN
from .const import NAME
from .const import PLATFORMS
from .const import STARTUP_MESSAGE

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)

async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)


    _LOGGER.info("Creating session")
    session = async_get_clientsession(hass)
    my_api = ClevastApiClient(username, password, session)

    _LOGGER.info("Creating cordinator")
    coordinator = ClevastDataUpdateCoordinator(hass, entry, my_api)
    _LOGGER.info("Sync coordinator")
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        _LOGGER.error("Error synchronizing coordinator")
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    _LOGGER.info("Setting entries up")
    
    device_registry = dr.async_get(hass)

    for device in coordinator._devices:
        platforms = PLATFORMS
        device_registry.async_get_or_create(
            config_entry_id = entry.entry_id,
            identifiers = {(DOMAIN, device["deviceId"])},
            manufacturer = NAME,
            name = device["deviceName"],
            model = device["model"],
            name_by_user = device["nickname"],
        )
        _LOGGER.info(
            f"Humidifier {device['nickname']} registered successfully."
        )
        main_platform = device["productType"]
        platforms.append(main_platform)
        for platform in platforms:
            if entry.options.get(platform, False):
                continue
            coordinator._platforms.append(platform)

    
        

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

"""Sensor platform for Clevast."""

from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import ICON
from .const import SENSOR
from .entity import ClevastEntity

from homeassistant.const import PERCENTAGE
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)


#async def async_setup_entry(hass, entry, async_add_devices):
async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    #async_add_devices([ClevastSensor(coordinator, entry)])
    for device in coordinator._devices:
        if "productType" not in device or device["productType"] != "HUMIDIFIER":
            continue
        device["version"] = "2.0.11"
        async_add_entities(
            [ClevastSensor(coordinator, device["deviceId"])]
        )


class ClevastSensor(ClevastEntity, SensorEntity):
    """clevast Sensor class."""
    
    _attr_translation_key = "humidity"
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, idx) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, idx)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f'{self._idx}-humidity'
    
    @property
    def entity_id(self):
        """Return a unique ID to use for this entity."""
        return f"sensor.{self.unique_id}_humidity"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._device_name}_humidity_{SENSOR}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("status")

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return self._attr_device_class
    
    @property
    def native_value(self) -> int:
        """Return current environment humidity."""
        return self.coordinator.data.get("current_humidity")
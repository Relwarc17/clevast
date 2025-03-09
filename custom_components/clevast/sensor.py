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


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([ClevastSensor(coordinator, entry)])


class ClevastSensor(ClevastEntity, SensorEntity):
    """clevast Sensor class."""
    
    _attr_translation_key = "humidity"
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator,
        device,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        assert self.unique_id is not None
        self.unique_id += "-humidity"
        self.entity_id = f"sensor.{self.entity_id_base}_humidity"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_humidity_{SENSOR}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("body")

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return "clevast__custom_device_class"
    
    @property
    def native_value(self) -> int:
        """Return current environment humidity."""
        return self.coordinator.data.state.environment_humidity
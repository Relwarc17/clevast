"""Constants for Clevast."""
# Base component constants
NAME = "Clevast"
DOMAIN = "clevast"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.0"

ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL = "https://github.com/Relwarc17/clevast/issues"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
#BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
HUMIDIFIER = "humidifier"
#PLATFORMS = [BINARY_SENSOR, SENSOR, SWITCH]
#PLATFORMS = [HUMIDIFIER, SENSOR, SWITCH]
PLATFORMS = [HUMIDIFIER]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

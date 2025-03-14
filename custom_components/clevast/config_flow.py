"""Adds config flow for Clevast."""
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow, CONN_CLASS_CLOUD_POLL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import ClevastApiClient
from .const import CONF_PASSWORD
from .const import CONF_USERNAME
from .const import DOMAIN
from .const import PLATFORMS


class ClevastFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for clevast."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    @property
    def errors(self) -> dict:
        return dict()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return await self._show_config_form(user_input)
        
        valid = await self._test_credentials(
            user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
        )
        if valid:
            return self.async_create_entry(
                title=user_input[CONF_USERNAME], data=user_input
            )
        
        self._errors["base"] = "auth"
        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        return ClevastOptionsFlowHandler()

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, username, password):
        """Return true if credentials is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = ClevastApiClient(username, password, session)
            await client.login()
            return True
        except Exception:  # pylint: disable=broad-except
            pass
        return False


class ClevastOptionsFlowHandler(OptionsFlow):
    """Config flow options handler for clevast."""


    @property
    def options(self) -> dict:
        return dict(self.config_entry.options)
    
    @property
    def config_entry(self):
        return self.hass.config_entries.async_get_entry(self.handler)


    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_USERNAME), data=self.options
        )

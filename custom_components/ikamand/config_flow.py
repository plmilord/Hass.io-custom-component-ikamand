"""Config flow for iKamand integration."""
import voluptuous as vol

# Import the device class from the component that you want to support
from .const import _LOGGER, DOMAIN
from .ikamand import Ikamand
from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_HOST
from homeassistant.core import callback

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


@callback
def configured_instances(hass):
    """Return a set of configured iKamand instances."""

    return {entry.title for entry in hass.config_entries.async_entries(DOMAIN)}


class iKamandConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iKamand."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input:
            try:
                await validate_input(self.hass, user_input)
                return self.async_create_entry(title="", data=user_input)
            except AlreadyConfigured:
                return self.async_abort(reason="already_configured")
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)


async def validate_input(hass, data):
    """Validate the user input allows us to connect."""

    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data[CONF_HOST] == data[CONF_HOST]:
            raise AlreadyConfigured

    ikamand = Ikamand(data[CONF_HOST])

    await ikamand.get_info()

    if not ikamand._online:
        raise CannotConnect


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class AlreadyConfigured(exceptions.HomeAssistantError):
    """Error to indicate this device is already configured."""

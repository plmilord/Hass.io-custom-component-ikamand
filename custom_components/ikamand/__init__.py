"""iKamand integration."""
import asyncio
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

# Import the device class from the component that you want to support
from .const import _LOGGER, API, DOMAIN, IKAMAND_COMPONENTS
from .ikamand import Ikamand
from datetime import timedelta
from homeassistant.const import CONF_HOST
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_time_interval

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, base_config):
    """Configure the iKamand component using flow only."""

    hass.data.setdefault(DOMAIN, {})

    if DOMAIN in base_config:
        for entry in base_config[DOMAIN]:
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": SOURCE_IMPORT}, data=entry
                )
            )
    return True


async def async_setup_entry(hass, config_entry):
    """Set up iKamand from a config entry."""

    ikamand = Ikamand(config_entry.data[CONF_HOST])
    hass.data[DOMAIN][config_entry.entry_id] = {API: ikamand}

    await ikamand.get_info()

    if not ikamand._online:
        _LOGGER.error("Failed to connect iKamand at %s", config_entry.data[CONF_HOST])
        raise ConfigEntryNotReady

    hass.loop.create_task(ikamand.get_data())

    for component in IKAMAND_COMPONENTS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, component))

    return True


async def async_unload_entry(hass, config_entry) -> bool:
    """Unload a config entry."""

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in IKAMAND_COMPONENTS
            ]
        )
    )

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)
        return True

    return False


class iKamandDevice(Entity):
    """Representation of a iKamand device."""

    def __init__(self, ikamand, config_entry):
        """Initialize the iKamand device."""
        self._ikamand = ikamand
        self._unique_id = "iKamand"

    async def async_added_to_hass(self):
        """Register state update callback."""

    @property
    def should_poll(self) -> bool:
        """Home Assistant will poll an entity when the should_poll property returns True."""
        return True

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_info(self):
        """Return the device information for this entity."""
        return {
            "identifiers": {(DOMAIN, self._ikamand.mac_address)},
            "manufacturer": "Kamado Joe",
            "name": f"iKamand-{self._ikamand.mac_address[-4:]}",
            "sw_version": self._ikamand.firmware_version,
        }

"""iKamand integration."""
import asyncio

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

# Import the device class from the component that you want to support
from .const import (
    _LOGGER,
    DATA_LISTENER,
    DOMAIN,
    IKAMAND,
    IKAMAND_COMPONENTS,
)
from homeassistant.const import CONF_HOST
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_time_interval
from ikamand.ikamand import Ikamand

from datetime import timedelta
IKAMAND_SYNC_INTERVAL = timedelta(seconds=15)


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
    hass.data[DOMAIN][config_entry.entry_id] = {IKAMAND: ikamand, DATA_LISTENER: [config_entry.add_update_listener(update_listener)]}

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["api"] = ikamand
    hass.data[DOMAIN]["instance"] = config_entry.data[CONF_HOST]
    # setting initial to zero to help with graphing
    hass.data[DOMAIN]["pt"] = 0
    hass.data[DOMAIN]["t1"] = 0
    hass.data[DOMAIN]["t2"] = 0
    hass.data[DOMAIN]["t3"] = 0
    hass.data[DOMAIN]["online"] = False
    hass.data[DOMAIN]["fan"] = 0

    def ikamand_update(event_time):
        """Update data from nextcloud api."""
        try:
            ikamand.get_data()
            hass.data[DOMAIN]["pt"] = ikamand.pit_temp
            hass.data[DOMAIN]["t1"] = ikamand.probe_1
            hass.data[DOMAIN]["t2"] = ikamand.probe_2
            hass.data[DOMAIN]["t3"] = ikamand.probe_3
            hass.data[DOMAIN]["online"] = ikamand.online
            hass.data[DOMAIN]["fan"] = ikamand.fan_speed
        except Exception:
            _LOGGER.error("iKamand update failed")
            return False

    await update_listener(hass, config_entry)

    #track_time_interval(hass, ikamand_update, IKAMAND_SYNC_INTERVAL)

    for component in IKAMAND_COMPONENTS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, component))
#(hass, component, DOMAIN, {}, config)
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

    hass.data[DOMAIN][config_entry.entry_id][DATA_LISTENER]:listener()

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)
        return True

    return False


async def update_listener(hass, config_entry):
    """Handle options update."""


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
            "manufacturer": "Kamado Joe",
        }

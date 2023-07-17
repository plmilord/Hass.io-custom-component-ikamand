"""iKamand integration."""
import asyncio

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

# Import the device class from the component that you want to support
from .const import (
    _LOGGER,
    API,
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
    hass.data[DOMAIN][config_entry.entry_id] = {API: ikamand}

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["api"] = ikamand
    hass.data[DOMAIN]["instance"] = config_entry.data[CONF_HOST]
    # setting initial to zero to help with graphing
    hass.data[DOMAIN]["pit_temp"] = 0
    hass.data[DOMAIN]["probe_1"] = 0
    hass.data[DOMAIN]["probe_2"] = 0
    hass.data[DOMAIN]["probe_3"] = 0
    hass.data[DOMAIN]["online"] = False
    hass.data[DOMAIN]["fan_speed"] = 0

    async def ikamand_update():
        while True:
            try:
                ikamand.get_data()
            except Exception:
                pass

            if ikamand.online:
                hass.data[DOMAIN]["pit_temp"] = ikamand.pit_temp
                hass.data[DOMAIN]["probe_1"] = ikamand.probe_1
                hass.data[DOMAIN]["probe_2"] = ikamand.probe_2
                hass.data[DOMAIN]["probe_3"] = ikamand.probe_3
                hass.data[DOMAIN]["online"] = ikamand.online
                hass.data[DOMAIN]["fan_speed"] = ikamand.fan_speed

            await asyncio.sleep(15)

    hass.loop.create_task(ikamand_update())

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

    hass.data[DOMAIN][config_entry.entry_id][DATA_LISTENER]:listener()

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
            "identifiers": {(DOMAIN, "Device MAC address")},
            "manufacturer": "Kamado Joe",
            "name": "iKamand-___E",
            "sw_version": "1.0.56",
        }

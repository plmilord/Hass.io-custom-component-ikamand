"""iKamand switches."""
from . import iKamandDevice
from .const import _LOGGER, API, DOMAIN
from datetime import timedelta
from homeassistant.components.switch import SwitchEntity

SCAN_INTERVAL = timedelta(seconds=5)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup the iKamand switches."""

    ikamand = hass.data[DOMAIN][config_entry.entry_id][API]
    entities = []

    entities.append(FireItUp(ikamand, config_entry))

    async_add_entities(entities, True)


class FireItUp(iKamandDevice, SwitchEntity):
    """Representation of Start iKamand switch."""

    def __init__(self, ikamand, config_entry):
        """Initialise the device."""
        super().__init__(ikamand, config_entry)
        self._ikamand = ikamand

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._ikamand.mac_address}#fireitup"

    @property
    def name(self):
        """Return the name of the device."""
        return "Fire It Up"

    @property
    def icon(self):
        """Return the icon of the device."""
        return "mdi:fire"

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        attrs = {}
        attrs["Recommended Times"] = ""
        attrs["200-400°F"] = "10 min"
        attrs["400-600°F"] = "20 min"
        attrs["600+°F"] = "30 min"
        return attrs

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._ikamand.starting

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        await self._ikamand.fire_it_up()

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        await self._ikamand.shut_it_down()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._ikamand.online

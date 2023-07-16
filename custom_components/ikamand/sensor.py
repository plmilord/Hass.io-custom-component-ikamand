"""Sensor data from iKamand."""
from . import iKamandDevice
from .const import _LOGGER, API, DOMAIN, PROBES
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE, TEMP_CELSIUS
from homeassistant.helpers.entity import Entity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the iKamand sensors."""

    ikamand = hass.data[DOMAIN][API]
    entities = []

    for name in PROBES:
        entities.append(iKamandProbeSensor(name, ikamand, config_entry))

    entities.append(iKamandFanSensor("Fan", ikamand, config_entry))

    async_add_entities(entities, True)


class iKamandProbeSensor(iKamandDevice, SensorEntity):
    """Represents a iKamand sensor."""

    def __init__(self, item, ikamand, config_entry):
        """Initialize the device."""
        super().__init__(ikamand, config_entry)
        self._name = item
        self._state = None

    @property
    def icon(self):
        """Return the icon for this sensor."""
        return "mdi:thermometer"

    @property
    def name(self):
        """Return the name for this sensor."""
        return f"iKamand {self._name}"

    @property
    def state(self):
        """Return the state for this sensor."""
        return self._state

    @property
    def unique_id(self):
        """Return the unique ID for this sensor."""
        return f"{self.hass.data[DOMAIN]['instance']}#{self._name}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement the value is expressed in."""
        return TEMP_CELSIUS

    def update(self):
        """Update the sensor."""
        self._state = self.hass.data[DOMAIN][PROBES[self._name]]

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.hass.data[DOMAIN]["online"]


class iKamandFanSensor(iKamandDevice, SensorEntity):
    """Represents a iKamand sensor."""

    def __init__(self, item, ikamand, config_entry):
        """Initialize the device."""
        super().__init__(ikamand, config_entry)
        self._name = item
        self._state = None

    @property
    def icon(self):
        """Return the icon for this sensor."""
        return "mdi:fan"

    @property
    def name(self):
        """Return the name for this sensor."""
        return f"iKamand {self._name}"

    @property
    def state(self):
        """Return the state for this sensor."""
        return self._state

    @property
    def unique_id(self):
        """Return the unique ID for this sensor."""
        return f"{self.hass.data[DOMAIN]['instance']}#{self._name}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement the value is expressed in."""
        return PERCENTAGE

    def update(self):
        """Update the sensor."""
        self._state = self.hass.data[DOMAIN]["fan"]

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.hass.data[DOMAIN]["online"]

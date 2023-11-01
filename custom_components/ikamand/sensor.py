"""Sensor data from iKamand."""
from . import iKamandDevice
from .const import _LOGGER, API, DOMAIN
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE, TEMP_CELSIUS

from datetime import timedelta
SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the iKamand sensors."""

    ikamand = hass.data[DOMAIN][config_entry.entry_id][API]
    entities = []

    entities.append(iKamandFanSensor("Fan", ikamand, config_entry))
    entities.append(iKamandPitSensor("Pit", ikamand, config_entry))

    for i in range(0, 3):
        entities.append(iKamandProbeSensor(i + 1, ikamand, config_entry))

    async_add_entities(entities, True)


class iKamandFanSensor(iKamandDevice, SensorEntity):
    """Represents a iKamand sensor."""

    def __init__(self, item, ikamand, config_entry):
        """Initialize the device."""
        super().__init__(ikamand, config_entry)
        self._ikamand = ikamand
        self._name = item

    @property
    def icon(self):
        """Return the icon for this sensor."""
        return "mdi:fan"

    @property
    def name(self):
        """Return the name for this sensor."""
        return self._name

    @property
    def state(self):
        """Return the state for this sensor."""
        return self._ikamand.fan_speed

    @property
    def unique_id(self):
        """Return the unique ID for this sensor."""
        return f"{self._ikamand.mac_address}#{self._name}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement the value is expressed in."""
        return PERCENTAGE

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._ikamand.online


class iKamandPitSensor(iKamandDevice, SensorEntity):
    """Represents a iKamand sensor."""

    def __init__(self, item, ikamand, config_entry):
        """Initialize the device."""
        super().__init__(ikamand, config_entry)
        self._ikamand = ikamand
        self._name = item

    @property
    def icon(self):
        """Return the icon for this sensor."""
        return "mdi:thermometer"

    @property
    def name(self):
        """Return the name for this sensor."""
        return self._name

    @property
    def state(self):
        """Return the state for this sensor."""
        return self._ikamand.pit_temp

    @property
    def unique_id(self):
        """Return the unique ID for this sensor."""
        return f"{self._ikamand.mac_address}#{self._name}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement the value is expressed in."""
        return TEMP_CELSIUS

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._ikamand.online


class iKamandProbeSensor(iKamandDevice, SensorEntity):
    """Represents a iKamand sensor."""

    def __init__(self, item, ikamand, config_entry):
        """Initialize the device."""
        super().__init__(ikamand, config_entry)
        self._ikamand = ikamand
        self._name = item

    @property
    def icon(self):
        """Return the icon for this sensor."""
        return "mdi:thermometer"

    @property
    def name(self):
        """Return the name for this sensor."""
        return 'Probe ' + str(self._name)

    @property
    def state(self):
        """Return the state for this sensor."""
        return getattr(self._ikamand, f"probe_{self._name}")

    @property
    def unique_id(self):
        """Return the unique ID for this sensor."""
        return f"{self._ikamand.mac_address}#probe_{self._name}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement the value is expressed in."""
        return TEMP_CELSIUS

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._ikamand.online

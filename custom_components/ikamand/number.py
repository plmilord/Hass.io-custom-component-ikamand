"""iKamand numbers."""
from . import iKamandDevice
from .const import _LOGGER, API, DOMAIN
from datetime import timedelta
from homeassistant.const import UnitOfTemperature
from homeassistant.components.number import NumberEntity, NumberDeviceClass

SCAN_INTERVAL = timedelta(seconds=5)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup the iKamand numbers."""

    ikamand = hass.data[DOMAIN][config_entry.entry_id][API]
    entities = []

    entities.append(SetFanDuration(ikamand, config_entry))

    for i in range(0, 3):
        entities.append(ProbeTargetTemperature(i + 1, ikamand, config_entry))

    async_add_entities(entities, True)


class SetFanDuration(iKamandDevice, NumberEntity):
    """Representation of Start iKamand number."""

    def __init__(self, ikamand, config_entry):
        """Initialise the device."""
        super().__init__(ikamand, config_entry)
        self._ikamand = ikamand

    @property
    def unique_id(self):
        """Return the unique ID for this sensor."""
        return f"{self._ikamand.mac_address}#set_fan_duration"

    @property
    def name(self):
        """Return the name for this sensor."""
        return "Set Fan Duration"

    @property
    def icon(self):
        """Return the icon for this sensor."""
        return "mdi:fan-clock"

    @property
    def native_max_value(self) -> int:
        """Return the maximum value."""
        return 30

    @property
    def native_min_value(self) -> int:
        """Return the minimum value."""
        return 0

    @property
    def native_value(self) -> int:
        """Return the value of the number."""
        return self._ikamand.set_fan_duration

    async def async_set_native_value(self, value: int) -> None:
        """Set value of the number."""
        self._ikamand._set_fan_duration = int(value)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._ikamand.online


class ProbeTargetTemperature(iKamandDevice, NumberEntity):
    """Representation of Start iKamand number."""

    def __init__(self, item, ikamand, config_entry):
        """Initialise the device."""
        super().__init__(ikamand, config_entry)
        self._ikamand = ikamand
        self._name = item
        self._sensor_type = NumberDeviceClass.TEMPERATURE

    @property
    def unique_id(self):
        """Return the unique ID for this sensor."""
        return f"{self._ikamand.mac_address}#probe_{self._name}_target_temperature"

    @property
    def device_class(self):
        """Return the class of this binary sensor."""
        return self._sensor_type

    @property
    def name(self):
        """Return the name for this sensor."""
        return "Probe " + str(self._name) + " Target T°"

    @property
    def icon(self):
        """Return the icon for this sensor."""
        return "mdi:thermometer-alert"

    @property
    def native_max_value(self) -> int:
        """Return the maximum value."""
        """The iKamand can control between 150°F-500°F (66°C-260°C)"""
        if self.hass.config.units.temperature_unit == UnitOfTemperature.FAHRENHEIT:
            return 500
        return 260

    @property
    def native_min_value(self) -> int:
        """Return the minimum value."""
        return 0

    @property
    def native_value(self) -> int:
        """Return the value of the number."""
        return getattr(self._ikamand, f"_probe_{self._name}_target_temperature")

    async def async_set_native_value(self, value: int) -> None:
        """Set value of the number."""
        setattr(self._ikamand, f"_probe_{self._name}_target_temperature", int(value))
        await self._ikamand.start_cooking(self._name)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if getattr(self._ikamand, f"probe_{self._name}") == None:
            return False
        return self._ikamand.online

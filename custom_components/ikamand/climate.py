"""iKamand thermostats."""
from . import iKamandDevice
from .const import _LOGGER, API, DOMAIN
from datetime import timedelta
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.util.unit_conversion import TemperatureConverter

SCAN_INTERVAL = timedelta(seconds=5)

SUPPORT_HVAC = [HVACMode.HEAT, HVACMode.OFF]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the iKamand thermostats."""

    ikamand = hass.data[DOMAIN][config_entry.entry_id][API]
    entities = []

    entities.append(IkamandThermostat(ikamand, config_entry))

    async_add_entities(entities, True)


class IkamandThermostat(iKamandDevice, ClimateEntity):
    """Represents a iKamand thermostat."""
    _enable_turn_on_off_backwards_compatibility = False

    def __init__(self, ikamand, config_entry):
        """Initialize the device."""
        super().__init__(ikamand, config_entry)
        self._ikamand = ikamand

    @property
    def icon(self):
        """Return the icon for this sensor."""
        return "mdi:grill"

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return "iKamand"

    @property
    def unique_id(self):
        """Return the unique ID for this sensor."""
        return f"{self._ikamand.mac_address}#ikamand"

    @property
    def temperature_unit(self):
        """Return the unit of measurement which this thermostat uses."""
        if self.hass.config.units.temperature_unit == UnitOfTemperature.FAHRENHEIT:
            return UnitOfTemperature.FAHRENHEIT
        return UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        if self._ikamand.pit_temp != None:
            if self.hass.config.units.temperature_unit == UnitOfTemperature.FAHRENHEIT:
                return round(TemperatureConverter.convert(self._ikamand.pit_temp, UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT))
            return self._ikamand.pit_temp
        return None

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        if self.hass.config.units.temperature_unit == UnitOfTemperature.FAHRENHEIT:
            return round(TemperatureConverter.convert(self._ikamand.target_pit_temp, UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT))
        return self._ikamand.target_pit_temp

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return 1

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        return HVACMode.HEAT if self._ikamand.cooking else HVACMode.OFF

    @property
    def hvac_modes(self):
        """Return the supported operations."""
        return SUPPORT_HVAC

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the operation mode."""
        if hvac_mode == HVACMode.HEAT:
            await self._ikamand.start_cook(self.target_temperature)
        elif hvac_mode == HVACMode.OFF:
            await self._ikamand.stop_cook()
        else:
            _LOGGER.error("Invalid operation mode provided %s", hvac_mode)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if self.hass.config.units.temperature_unit == UnitOfTemperature.FAHRENHEIT:
            temperature = round(TemperatureConverter.convert(temperature, UnitOfTemperature.FAHRENHEIT, UnitOfTemperature.CELSIUS))
        await self._ikamand.start_cook(temperature)

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        """The iKamand can control between 150°F-500°F (66°C-260°C)"""
        if self.hass.config.units.temperature_unit == UnitOfTemperature.FAHRENHEIT:
            return 150
        return 66

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        """The iKamand can control between 150°F-500°F (66°C-260°C)"""
        if self.hass.config.units.temperature_unit == UnitOfTemperature.FAHRENHEIT:
            return 500
        return 260

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._ikamand.online

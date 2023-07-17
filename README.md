<span align="center">

<a href="https://github.com/plmilord/Hass.io-custom-component-ikamand"><img src="https://raw.githubusercontent.com/plmilord/Hass.io-custom-component-ikamand/master/images/icon.png" width="150"></a>

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/plmilord/Hass.io-custom-component-ikamand.svg)](https://GitHub.com/plmilord/Hass.io-custom-component-ikamand/releases/)
[![HA integration usage](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.ikamand.total)](https://analytics.home-assistant.io/custom_integrations.json)

# Home Assistant custom component - iKamand

</span>

Since the event where Kamado Joe stopped supporting his iKamand service... I tried to find a solution to give a second life to this module and avoid the dump!

**iKamand** is based on similar projects and the work of many people. During installation, all components are created in accordance with the iKamand!

## What you need

- Kamado Joe Kamado Joe iKamand Smart Temperature Control and Monitoring Device

## Installation

You can install this integration via [HACS](#hacs) or [manually](#manual).

### HACS

Search for the iKamand integration and choose install. Reboot Home Assistant and configure the iKamand integration via the integrations page or press the blue button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ikamand)


### Manual

Copy the `custom_components/ikamand` to your custom_components folder. Reboot Home Assistant and configure the iKamand integration via the integrations page or press the blue button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ikamand)


## Preview

<span align="center">

<a href="https://github.com/plmilord/Hass.io-custom-component-ikamand"><img src="https://raw.githubusercontent.com/plmilord/Hass.io-custom-component-ikamand/master/images/preview.png" width="500"></a>

</span>

Entity | Type | Tested | Programmed entity attributes
------ | ---- | ------ | ----------------------------
iKamand | Climate | ✓ | N/A
iKamand Fan | Sensor | ? | N/A
iKamand Pit Probe | Sensor | ? | N/A
iKamand Probe 1 | Sensor | ? | N/A
iKamand Probe 2 | Sensor | ? | N/A
iKamand Probe 3 | Sensor | ? | N/A

✓ = Tested and working  
? = Not working

## Task List

- [ ] Make the sensors work properly
- [ ] Bring the ability to configure this custom component via the entries in configuration.yaml
- [ ] Integrate the main ```ikamand``` program to improve connectivity, better error handling and eliminate dependency

## Inspiration / Credits

- https://github.com/slinkymanbyday/ikamand-ha | Forked project, initial inspiration!
- https://github.com/slinkymanbyday/ikamand | Main program in Python to interface the iKamand module.

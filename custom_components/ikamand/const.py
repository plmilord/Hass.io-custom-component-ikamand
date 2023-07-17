"""Const file for iKamand."""
import logging

_LOGGER = logging.getLogger(__name__)
API = "api"
DATA_LISTENER = "listener"
DOMAIN = "ikamand"
PROBES = {
    "Pit Probe": "pit_temp",
    "Probe 1": "probe_1",
    "Probe 2": "probe_2",
    "Probe 3": "probe_3",
}
IKAMAND = "ikamand"
IKAMAND_COMPONENTS = [
    "climate",
    "sensor",
]
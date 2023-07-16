"""Const file for iKamand."""
import logging

_LOGGER = logging.getLogger(__name__)
API = "api"
DATA_LISTENER = "listener"
DOMAIN = "ikamand"
PROBES = {
    "Pit Probe": "pt",
    "Probe 1": "t1",
    "Probe 2": "t2",
    "Probe 3": "t3",
}
IKAMAND = "ikamand"
IKAMAND_COMPONENTS = [
    "climate",
    "sensor",
]
"""Const file for iKamand."""
import logging

_LOGGER = logging.getLogger(__name__)
API = "api"
DOMAIN = "ikamand"
IKAMAND_COMPONENTS = [
    "climate",
    "sensor",
]
GOOD_HTTP_CODES = [200, 201, 202, 203]
FALSE_TEMPS = ["-400", "400"]

# cgi-bin/data
COOK_END_TIME = "sce"
COOK_ID = "csid"
COOK_START = "acs"
CURRENT_TIME = "ct"
FAN_SPEED = "dc"
FOOD_PROBE = "p"
GRILL_END_TIME = "sge"
GRILL_START = "ag"
PIT_TEMP = "pt"
PROBE_1 = "t1"
PROBE_2 = "t2"
PROBE_3 = "t3"
TARGET_FOOD_TEMP = "tft"
TARGET_PIT_TEMP = "tpt"
UNKNOWN_RECEIVE_VAR1 = "rm"
UNKNOWN_RECEIVE_VAR2 = "cm"
UNKNOWN_SEND_VAR1 = "as"
UPTIME = "time"

# cgi-bin/info
ENV = "env"
FW_VERSION = "fw_version"
MAC_ADDRESS = "MAC"

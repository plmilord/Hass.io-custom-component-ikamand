"""
Python wrapper package for the Ikamand.

This code is released under the terms of the MIT license. See the LICENSE
file for more details.
"""
import aiohttp
import asyncio
import requests
import time

from .const import (
    _LOGGER,
    COOK_END_TIME,
    COOK_ID,
    COOK_START,
    CURRENT_TIME,
    FALSE_TEMPS,
    FAN_SPEED,
    FOOD_PROBE,
    FW_VERSION,
    GOOD_HTTP_CODES,
    GRILL_END_TIME,
    GRILL_START,
    MAC_ADDRESS,
    PIT_TEMP,
    PROBE_1,
    PROBE_2,
    PROBE_3,
    TARGET_FOOD_TEMP,
    TARGET_PIT_TEMP,
    UNKNOWN_SEND_VAR1,
)
from urllib.parse import parse_qs

HTTP_ERRORS = (
    requests.exceptions.ConnectionError,
    requests.exceptions.HTTPError,
)

TIMEOUT = 5


class Ikamand:
    """A class for the iKamand API."""

    def __init__(self, host_ip):
        """Initialize the class."""
        #self._session = requests.session()
        self.base_url = f"http://{host_ip}/cgi-bin/"
        self._data = {}
        self._info = {}
        self._online = False
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ikamand",
        }

    async def get_info(self):
        """Get grill info."""
        url = f"{self.base_url}info"

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: requests.get(url))

        if response.status_code in GOOD_HTTP_CODES:
            result = parse_qs(response.text)
            self._info = result
            self._online = True
        else:
            self._online = False

        #_LOGGER.info("self._info = %s", self._info)

    async def get_data(self):
        """Get grill data."""
        url = f"{self.base_url}data"

        while True:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, lambda: requests.get(url))

            if response.status_code in GOOD_HTTP_CODES:
                result = parse_qs(response.text)
                self._data = result
                self._online = True
            else:
                self._online = False

            #_LOGGER.info("self._data = %s", self._data)

            await asyncio.sleep(5)

    async def start_cook(self, target_pit_temp: int, target_food_temp: int = 0, food_probe: int = 0):
        """Start iKamand Cook."""
        url = f"{self.base_url}cook"
        current_time = int(time.time())
        data = {
            COOK_START: 1,
            COOK_ID: "",
            TARGET_PIT_TEMP: target_pit_temp,
            COOK_END_TIME: current_time + 86400,
            FOOD_PROBE: food_probe,
            TARGET_FOOD_TEMP: target_food_temp,
            UNKNOWN_SEND_VAR1: 0,
            CURRENT_TIME: current_time,
        }

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(url, headers=self.headers, data=data))

        if response.status_code in GOOD_HTTP_CODES:
            self._online = True
        else:
            _LOGGER.error("Error connecting to iKamand, %s", error)
            self._online = False

    async def stop_cook(self):
        """Stop iKamand Cook."""
        url = f"{self.base_url}cook"
        current_time = int(time.time())
        data = {
            COOK_START: 0,
            COOK_ID: "",
            TARGET_PIT_TEMP: 0,
            TARGET_FOOD_TEMP: 0,
            FOOD_PROBE: 0,
            CURRENT_TIME: current_time,
            COOK_END_TIME: 0,
        }

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(url, headers=self.headers, data=data))

        if response.status_code in GOOD_HTTP_CODES:
            self._online = True
        else:
            _LOGGER.error("Error connecting to iKamand, %s", error)
            self._online = False

    async def start_grill(self):
        """Start iKamand Grill mode (10 minutes full speed)."""
        url = f"{self.base_url}cook"
        current_time = int(time.time())
        data = {
            GRILL_START: 1,
            GRILL_END_TIME: current_time + 10 * 60,
            CURRENT_TIME: current_time,
        }

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(url, headers=self.headers, data=data))

        if response.status_code in GOOD_HTTP_CODES:
            self._online = True
        else:
            _LOGGER.error("Error connecting to iKamand, %s", error)
            self._online = False

    async def stop_grill(self):
        """Stop iKamand Grill mode."""
        url = f"{self.base_url}cook"
        current_time = int(time.time())
        data = {
            GRILL_START: 0,
            GRILL_END_TIME: 0,
            CURRENT_TIME: current_time,
        }

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(url, headers=self.headers, data=data))

        if response.status_code in GOOD_HTTP_CODES:
            self._online = True
        else:
            _LOGGER.error("Error connecting to iKamand, %s", error)
            self._online = False

    @property
    def firmware_version(self):
        """Return device firmware version."""
        return self._info.get(FW_VERSION, [0])[0]

    @property
    def mac_address(self):
        """Return device MAC address."""
        return self._info.get(MAC_ADDRESS, [0])[0]

    @property
    def data(self):
        """Return data."""
        return self._data

    @property
    def cooking(self):
        """Return cooking status."""
        return self._data.get(COOK_START, [0])[0] == "1"

    @property
    def grilling(self):
        """Return cooking status."""
        return self._data.get(GRILL_START, [0])[0] == "1"

    @property
    def pit_temp(self):
        """Return current pit temp."""
        return (
            int(self._data.get(PIT_TEMP, ["400"])[0])
            if self._data.get(PIT_TEMP, ["400"])[0] not in FALSE_TEMPS
            else None
        )

    @property
    def target_pit_temp(self):
        """Return target pit temp."""
        return int(self._data.get(TARGET_PIT_TEMP, [0])[0])

    @property
    def probe_1(self):
        """Return current probe 1 temp."""
        return (
            int(self._data.get(PROBE_1, ["400"])[0])
            if self._data.get(PROBE_1, ["400"])[0] not in FALSE_TEMPS
            else None
        )

    @property
    def probe_2(self):
        """Return current probe 2 temp."""
        return (
            int(self._data.get(PROBE_2, ["400"])[0])
            if self._data.get(PROBE_2, ["400"])[0] not in FALSE_TEMPS
            else None
        )

    @property
    def probe_3(self):
        """Return current probe 3 temp."""
        return (
            int(self._data.get(PROBE_3, ["400"])[0])
            if self._data.get(PROBE_3, ["400"])[0] not in FALSE_TEMPS
            else None
        )

    @property
    def fan_speed(self):
        """Return current fan speed %."""
        return int(self._data.get(FAN_SPEED, ["0"])[0])

    @property
    def online(self):
        """Return if reachable."""
        return self._online

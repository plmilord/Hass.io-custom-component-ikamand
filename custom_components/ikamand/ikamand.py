"""iKamand integration."""

import asyncio
import logging
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

urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.CRITICAL)


class Ikamand:
    """A class for the iKamand API."""

    def __init__(self, host_ip):
        """Initialize the class."""
        self.base_url = f"http://{host_ip}/cgi-bin/"
        self._data = {}
        self._data_bck = {'time': ['0'], 'acs': ['0']}
        self._info = {}
        self._online = False
        self._probe_1_target_temperature = 0
        self._probe_2_target_temperature = 0
        self._probe_3_target_temperature = 0
        self._set_fan_duration = 5
        self._starting = False
        self._starting_end_time = 0
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ikamand",
        }

    async def get_info(self):
        """Get iKamand info."""
        url = f"{self.base_url}info"

        loop = asyncio.get_running_loop()

        try:
            response = await loop.run_in_executor(None, lambda: requests.get(url, timeout=10))

            if response.status_code in GOOD_HTTP_CODES:
                result = parse_qs(response.text)
                self._info = result
                self._online = True
                #_LOGGER.info("self._info = %s", self._info)
            else:
                self._online = False

        except (requests.RequestException, asyncio.TimeoutError):
            self._online = False

    async def get_data(self):
        """Get iKamand data."""
        url = f"{self.base_url}data"

        while True:
            loop = asyncio.get_running_loop()

            try:
                response = await loop.run_in_executor(None, lambda: requests.get(url, timeout=10))

                if response.status_code in GOOD_HTTP_CODES:
                    result = parse_qs(response.text)

                    if 'time' in result and int(result['time'][0]) < 40:
                        self._data = {}
                        self._online = False
                    else:
                        if not self._online or abs(int(result['time'][0]) - int(time.time())) > 60:
                            await self.connection_recovery()
                        else:
                            self._data = self._data_bck = result
                            self._online = True
                            #_LOGGER.info("self._data = %s", self._data)
                else:
                    self._data = {}
                    self._online = False

            except (requests.RequestException, asyncio.TimeoutError):
                self._online = False

            if self._starting and int(time.time()) >= self._starting_end_time:
                await self.shut_it_down()

            await asyncio.sleep(5)

    async def post_commands(self, payload):
        """Send commands to iKamand."""
        url = f"{self.base_url}cook"
        loop = asyncio.get_running_loop()

        #_LOGGER.info("post_commands payload = %s", payload)

        try:
            response = await loop.run_in_executor(None, lambda: requests.post(url, headers=self.headers, data=payload, timeout=10))

            if response.status_code in GOOD_HTTP_CODES:
                self._online = True
            else:
                self._online = False

        except (requests.RequestException, asyncio.TimeoutError):
            self._online = False

    async def start_ikamand(self, target_pit_temp: int):
        """Start the iKamand."""
        current_time = int(time.time())
        payload = {
            COOK_START: 1,
            COOK_ID: "",
            TARGET_PIT_TEMP: target_pit_temp,
            COOK_END_TIME: current_time + 86400,
            FOOD_PROBE: 0,
            TARGET_FOOD_TEMP: 0,
            UNKNOWN_SEND_VAR1: 0,
            CURRENT_TIME: current_time,
        }

        await self.post_commands(payload)

    async def stop_ikamand(self):
        """Stop the iKamand."""
        current_time = int(time.time())
        payload = {
            COOK_START: 0,
            COOK_ID: "",
            TARGET_PIT_TEMP: 0,
            COOK_END_TIME: 0,
            FOOD_PROBE: 0,
            TARGET_FOOD_TEMP: 0,
            UNKNOWN_SEND_VAR1: 0,
            CURRENT_TIME: current_time,
        }

        self._starting = False

        await self.post_commands(payload)

    async def start_cooking(self, food_probe: int):
        """Start cooking."""
        current_time = int(time.time())
        payload = {
            COOK_START: 1,
            COOK_ID: food_probe,
            FOOD_PROBE: food_probe,
            TARGET_FOOD_TEMP: getattr(self, f"probe_{food_probe}_target_temperature"),
        }

        if self.cooking:
            await self.post_commands(payload)

    async def fire_it_up(self):
        """Start the iKamand fan at 100% for the selected duration."""
        current_time = int(time.time())
        payload = {
            COOK_START: 1,
            COOK_ID: "",
            TARGET_PIT_TEMP: 260,
            COOK_END_TIME: current_time + self._set_fan_duration * 60,
            FOOD_PROBE: 0,
            TARGET_FOOD_TEMP: 0,
            UNKNOWN_SEND_VAR1: 0,
            CURRENT_TIME: current_time,
        }

        self._starting = True
        self._starting_end_time = payload[COOK_END_TIME]

        await self.post_commands(payload)

    async def shut_it_down(self):
        """Stop the iKamand fan."""
        current_time = int(time.time())
        payload = {
            COOK_START: 0,
            COOK_ID: "",
            TARGET_PIT_TEMP: 0,
            COOK_END_TIME: 0,
            FOOD_PROBE: 0,
            TARGET_FOOD_TEMP: 0,
            UNKNOWN_SEND_VAR1: 0,
            CURRENT_TIME: current_time,
        }

        self._starting = False
        self._starting_end_time = 0

        await self.post_commands(payload)

    async def connection_recovery(self):
        """Restart iKamand Cook."""
        current_time = int(time.time())

        if self._starting:
            cook_end_time = self._starting_end_time
        else:
            cook_end_time = current_time + 86400

        if current_time - int(self._data_bck['time'][0]) < 600 and int(self._data_bck['acs'][0]):
            payload = {
                COOK_START: 1,
                COOK_ID: "",
                TARGET_PIT_TEMP: int(self._data_bck.get(TARGET_PIT_TEMP, [0])[0]),
                COOK_END_TIME: cook_end_time,
                FOOD_PROBE: 0,
                TARGET_FOOD_TEMP: 0,
                UNKNOWN_SEND_VAR1: 0,
                CURRENT_TIME: current_time,
            }
        else:
            payload = {
                COOK_START: 0,
                COOK_ID: "",
                TARGET_PIT_TEMP: 0,
                COOK_END_TIME: 0,
                FOOD_PROBE: 0,
                TARGET_FOOD_TEMP: 0,
                UNKNOWN_SEND_VAR1: 0,
                CURRENT_TIME: current_time,
            }

        await self.post_commands(payload)

    @property
    def cooking(self):
        """Return cooking status."""
        return self._data.get(COOK_START, [0])[0] == "1"

    @property
    def data(self):
        """Return data."""
        return self._data

    @property
    def fan_speed(self):
        """Return current fan speed %."""
        return int(self._data.get(FAN_SPEED, ["0"])[0])

    @property
    def firmware_version(self):
        """Return device firmware version."""
        return self._info.get(FW_VERSION, [0])[0]

    @property
    def mac_address(self):
        """Return device MAC address."""
        return self._info.get(MAC_ADDRESS, [0])[0]

    @property
    def online(self):
        """Return if reachable."""
        return self._online

    @property
    def pit_temp(self):
        """Return current pit temperature."""
        return (
            int(self._data.get(PIT_TEMP, ["400"])[0])
            if self._data.get(PIT_TEMP, ["400"])[0] not in FALSE_TEMPS
            else None
        )

    @property
    def probe_1(self):
        """Return current temperature of probe 1."""
        return (
            int(self._data.get(PROBE_1, ["400"])[0])
            if self._data.get(PROBE_1, ["400"])[0] not in FALSE_TEMPS
            else None
        )

    @property
    def probe_1_target_temperature(self):
        """Return the target temperature for probe 1."""
        return self._probe_1_target_temperature

    @property
    def probe_2(self):
        """Return current temperature of probe 2."""
        return (
            int(self._data.get(PROBE_2, ["400"])[0])
            if self._data.get(PROBE_2, ["400"])[0] not in FALSE_TEMPS
            else None
        )

    @property
    def probe_2_target_temperature(self):
        """Return the target temperature for probe 2."""
        return self._probe_2_target_temperature

    @property
    def probe_3(self):
        """Return current temperature of probe 3."""
        return (
            int(self._data.get(PROBE_3, ["400"])[0])
            if self._data.get(PROBE_3, ["400"])[0] not in FALSE_TEMPS
            else None
        )

    @property
    def probe_3_target_temperature(self):
        """Return the target temperature for probe 3."""
        return self._probe_3_target_temperature

    @property
    def set_fan_duration(self):
        """Return of fan duration."""
        return self._set_fan_duration

    @property
    def starting(self):
        """Return starting status."""
        return self._starting

    @property
    def target_pit_temp(self):
        """Return target pit temperature."""
        return int(self._data.get(TARGET_PIT_TEMP, [0])[0])

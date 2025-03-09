"""Sample API Client."""
import asyncio
import logging
import socket
import hashlib
import json
import time

import aiohttp
import async_timeout

from homeassistant.exceptions import ConfigEntryAuthFailed

TIMEOUT = 30

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {
    "Content-type": "application/json; charset=UTF-8",
    "User-Agent": "Clevast/1.7.16 (iPhone; iOS 18.3.1; Scale/3.00)"
}


class ClevastApiClient:
    def __init__(
        self, username: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session
        self._token = None
        self._last_login_time = None
        self._login_interval = 300 
        self._baseurl = "https://cloud.clevast.com"

    async def login(self) -> None:
        now = time.time()
        if self._token and (now - self._last_login_time < self._login_interval):
            _LOGGER.info("Token still valid, skipping login.")
            return
        url = f"{self._baseurl}/clevast/api/user/login"
        md5_password = hashlib.md5(self._password.encode()).hexdigest()
        login_data = {
            "email": self._username,
            "privacyFlag": False,
            "password": md5_password,
            "phoneVersion":"18.3.1",
            "phoneBrand":"iPhone",
            "phoneModel":"iPhone17,1"
        }
        response = await self.api_wrapper("post", url, data=login_data, headers=HEADERS)
        _LOGGER.info("API Login Response: %s", json.dumps(response, indent=2))
        
        _LOGGER.info(response["message"])
        if "message" not in response and response["message"] != "Success":
            _LOGGER.error("Error authenticating")
            raise ConfigEntryAuthFailed
        _LOGGER.info(response["result"])
        self._token = response["result"]["token"]
        self._last_login_time = time.time()
        HEADERS["Authorization"] = self._token
        _LOGGER.info("Login succesfull, Token acquired.")
    
    
    async def get_devices(self) -> list:
        _LOGGER.info("Start request to get devices")
        await self._ensure_token()
        url = f"{self._baseurl}/clevast/api/user/device"
        response = await self.api_wrapper("get", url, headers=HEADERS)
        _LOGGER.info("GET devices Response: %s", json.dumps(response, indent=2))
        if "result" not in response:
            _LOGGER.error("result not in esponse.")
            return list()
        return response["result"]
    
    async def get_device_info(self, device_id) -> dict:
        url = f"{self._baseurl}/clevast/api/device/info/{device_id}"
        response = await self.api_wrapper("get", url, data={}, headers=HEADERS)
        _LOGGER.info("GET device info Response: %s", json.dumps(response, indent=2))
        if "result" not in response:
            _LOGGER.error("result not in esponse.")
            return dict()
        return response["result"]
    
    async def get_device_data(self, device_id) -> dict:
        url = f"{self._baseurl}/clevast/api/device/manage/sync/get"
        params = {
            "deviceId": device_id,
            "identifier": "sys_all"
        }
        response = await self.api_wrapper("get", url, data=params, headers=HEADERS)
        _LOGGER.info("GET device data Response: %s", json.dumps(response, indent=2))
        if "result" not in response:
            _LOGGER.error("result not in esponse.")
            return list()
        return response["result"]


    async def sync_data(self, device_id, args: str) -> ...:
        """Get data from the API."""
        url = f"{self._baseurl}/clevast/api/device/manage/async/set"
        dev_data = {
            #"args": "{\"state_synch\":1}",
            "args": args,
            "deviceId": device_id
        }
        response =  await self.api_wrapper("post", url, data=dev_data, headers=HEADERS)
        _LOGGER.info("POST sync data Response: %s", json.dumps(response, indent=2))
        if "message" in response and response["message"] != "Success":
            _LOGGER.error(response["message"])


    async def _ensure_token(self):
        """Ensure that the token is valid."""
        if not self._token:
            await self.login()

    async def api_wrapper(
        self, method: str, url: str, data: dict = {}, headers: dict = {}
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                if method == "get":
                    response = await self._session.get(url, params=data, headers=headers, proxy="http://192.168.178.62:8080")
                    #return await response.json()

                elif method == "put":
                    response = await self._session.put(url, headers=headers, json=data)

                elif method == "patch":
                    response = await self._session.patch(url, headers=headers, json=data)

                elif method == "post":
                    response = await self._session.post(url, headers=headers, json=data)
                    #return await response.json()
                return await response.json()
        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)

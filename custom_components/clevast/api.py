"""Sample API Client."""
import asyncio
import logging
import socket
import hashlib
import json
import time

import aiohttp
import async_timeout

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
            #raise aiohttp.web.HTTPUnauthorized
        _LOGGER.info(response["result"])
        self._token = response["result"]["token"]
        self._last_login_time = time.time()
        HEADERS["Authorization"] = self._token
        _LOGGER.info("Login succesfull, Token acquired.")
    
    
    async def get_device(self) -> dict:
        await self._ensure_token()
        url = f"{self._baseurl}/clevast/api/user/device"
        response = await self.api_wrapper("get", url, headers=HEADERS)
        _LOGGER.info("API Login Response: %s", json.dumps(response, indent=2))
        if not "result" in response:
            return dict()
        return response["result"]
    
    
    async def async_get_data(self, device_id) -> dict:
        """Get data from the API."""
        url = f"{self._baseurl}/clevast/api/device/manage/async/set"
        dev_data = {
            "args": "{\"state_synch\":1}",
            "deviceId": device_id
        }
        return await self.api_wrapper("post", url, data=dev_data, headers=HEADERS)

    async def async_set_title(self, value: str) -> None:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        await self.api_wrapper("patch", url, data={"title": value}, headers=HEADERS)

    async def _ensure_token(self):
        """Ensure that the token is valid."""
        if not self._token:
            await self.login()

    async def api_wrapper(
        self, method: str, url: str, data: dict = {}, headers: dict = {}
    ) -> dict:
        """Get information from the API."""
        try:
            _LOGGER.debug("Before async_timeout")
            async with async_timeout.timeout(TIMEOUT):
                _LOGGER.debug("Inside async_timeout")
                if method == "get":
                    _LOGGER.info("Sending GET request")
                    response = await self._session.get(url, headers=headers)
                    #return await response.json()

                elif method == "put":
                    response = await self._session.put(url, headers=headers, json=data)

                elif method == "patch":
                    response = await self._session.patch(url, headers=headers, json=data)

                elif method == "post":
                    _LOGGER.info("Sending POST request")
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

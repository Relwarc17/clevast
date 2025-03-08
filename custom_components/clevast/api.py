"""Sample API Client."""
import asyncio
import logging
import socket
import hashlib
import json
import time

import aiohttp
import async_timeout

TIMEOUT = 10


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
        login_data = {
            "email": self._username,
            "privacyFlag": False,
            "password": hashlib.md5(self._password.encode()),
            "phoneVersion":"18.3.1",
            "phoneBrand":"iPhone",
            "phoneModel":"iPhone17,1"
        }
        response = await self.api_wrapper("post", url, data=login_data, headers=HEADERS)
        _LOGGER.info("API Login Response: %s", json.dumps(response, indent=2))
        if "message" not in response or response["message"] != "Success":
            raise aiohttp.web.HTTPUnauthorized
        self._token = response["data"]["token"]
        self._last_login_time = time.time()
        _LOGGER.info("Login erfolgreich, Token erhalten.")
    
    
    async def get_device(self) -> dict:
        self._ensure_token()
        url = f"{self._baseurl}/clevast/api/user/device"
        response = await self.api_wrapper("get", url)
        _LOGGER.info("API Login Response: %s", json.dumps(response, indent=2))
        return response
    
    
    async def async_get_data(self) -> dict:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        return await self.api_wrapper("get", url)

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
            async with async_timeout.timeout(TIMEOUT, loop=asyncio.get_event_loop()):
                if method == "get":
                    response = await self._session.get(url, headers=headers)
                    #return await response.json()

                elif method == "put":
                    response = await self._session.put(url, headers=headers, json=data)

                elif method == "patch":
                    response = await self._session.patch(url, headers=headers, json=data)

                elif method == "post":
                    await self._session.post(url, headers=headers, json=data)
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

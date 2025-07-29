import base64
import string
import random
import uuid

import aiohttp

from typing import Any, Dict, Literal
from urllib.parse import urljoin
from aiohttp import ClientError

from zafiaonline.structures.packet_data_keys import Endpoints, ZafiaEndpoints
from zafiaonline.utils.logging_config import logger


class Http:
    def __init__(self, proxy):
        self.zafia_url: str = "http://185.188.183.144:5000/zafia/"
        self.mafia_address: str = "dottap.com"
        self.api_mafia_address: str = f"api.mafia.{self.mafia_address}"
        self.mafia_url: str = f"https://{self.mafia_address}/"
        self.api_mafia_url: str = f"https://{self.api_mafia_address}/"
        self.zafia_endpoint: ZafiaEndpoints
        self.proxy: str | None = proxy
        self.zafia_headers: dict = {
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.12.0"
        }
        self.mafia_headers: dict = {
            "HOST": self.mafia_address,
            "User-Agent": self.generate_dalvik_ua(),
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

    @staticmethod
    def generate_dalvik_ua() -> str:
        dalvik_versions = ["1.6.0", "2.1.0"]
        android_versions = ["5.1.1", "6.0", "7.0", "8.1.0", "9", "10", "11", "12"]
        devices = [
            "Pixel 3", "Pixel 4 XL", "Samsung SM-G960F", "OnePlus A6013",
            "Huawei P30", "Xiaomi Mi 9", "Moto G7", "Nexus 5X"
        ]
        builds = [
            "LMY47D", "NRD90M", "OPM1.171019.011", "QP1A.190711.020",
            "RP1A.200720.012", "SP1A.210812.015"
        ]

        dalvik_ver = random.choice(dalvik_versions)
        android_ver = random.choice(android_versions)
        device = random.choice(devices)
        build = random.choice(builds)
        return f"Dalvik/{dalvik_ver} (Linux; U; Android {android_ver}; {device} Build/{build})"

    def generate_agent(self) -> str:
        user_agent: str = self.generate_dalvik_ua() 
        return user_agent

    @staticmethod
    def __generate_random_token(length: int = 32) -> str:
        return ''.join(random.choices(string.hexdigits.lower(), k=length))

    async def mafia_request(self, url: str, method: Literal["get", "post", "put",
                            "delete"], endpoint: Endpoints,
                            params: dict[str,Any] | None = None,
                            headers: Dict[str, str] | None = None,
                            ) -> dict[str, Any] | bytes:
        url = urljoin(url, endpoint.value)
        return await self.send_request(method, url, params, headers)

    def __build_headers(self, user_id:
                        str, headers: dict) -> tuple[str, Dict[str, str]]:
        url, boolean = self.__create_url()
        if boolean is True:
            return url, headers
        headers = self.__create_headers(headers, user_id)
        return url, headers

    def __create_url(self) -> tuple[str, bool] | str:
        url: str = urljoin(self.zafia_url, self.zafia_endpoint.value)
        if self.zafia_endpoint == ZafiaEndpoints.GET_VERIFICATIONS.value:
            return url, True
        return url

    def __create_headers(self, headers: dict, user_id: str) -> Dict:
        token: str = self.__generate_random_token()
        auth_raw: str = f"{user_id}=:={token}"
        auth_token: str = base64.b64encode(auth_raw.encode()).decode()
        headers["Authorization"] = auth_token
        return headers

    def build_zafia_headers(self, endpoint: ZafiaEndpoints, user_id:
    str = str(uuid.uuid4())) -> tuple[str, Dict[str, str]]:
        headers: dict = self.zafia_headers.copy() 
        self.zafia_endpoint = endpoint
        url, headers = self.__build_headers(user_id, headers)
        return url, headers

    def build_mafia_headers(self, user_id:
    str = str(uuid.uuid4())) -> Dict[str, str]:
        headers: dict = self.mafia_headers.copy()
        headers: dict = self.__create_headers(headers, user_id)
        return headers

    def build_api_mafia_headers(self, user_id:
    str = str(uuid.uuid4())) -> Dict[str, str]:
        #TODO: add new headers
        headers: dict = self.mafia_headers.copy()
        headers: dict = self.__create_headers(headers, user_id)
        return headers

    async def send_request(self, method: Literal["get", "post", "put", "delete"],
                           url: str, params: dict[str, Any] | None = None,
                           headers: dict[str, str] | None = None
                           ) -> dict[str, Any] | bytes:
        async with (aiohttp.ClientSession(headers = headers, proxy = self.proxy) as session):
            method = method
            try:
                async with getattr(session, method)(url, params = params
                                                    ) as response:
                    if response.content_type == 'application/json':
                        data: dict = await response.json()
                    else:
                        text = await response.text()
                        logger.warning(f"Response from {url}: {text}")
                        data = {'error': text}
                    return data
            except ClientError as e:
                logger.error(
                    f"Network error during {method.upper()} request to"
                    f" {url}: {e}")
                raise
            except Exception as e:
                logger.error(f"Error {method.upper()} {url}: {e}")
                raise


class HttpWrapper:
    def __init__(self, proxy: str | None = None):
        self.http = Http(proxy = proxy)

    async def zafia_request(self, method:
                            Literal["get", "post", "put", "delete"],
                            endpoint: ZafiaEndpoints, params: dict[str, Any],
                            user_id: str) -> Dict[str, Any] | bytes:
        url, headers = self.http.build_zafia_headers(endpoint, user_id)
        return await self.http.send_request(method = method, url = url,
                                params = params, headers = headers)

    async def mafia_request(self, method: Literal["get", "post", "put",
                            "delete"], endpoint: Endpoints,
                            params: dict[str, Any] | None = None) -> dict[str, str] | bytes:
        headers: Dict[str, str] = self.http.build_mafia_headers()
        return await (self.http.mafia_request(
            self.http.mafia_url, method, endpoint, params, headers))

    async def api_mafia_request(self, method: Literal["get", "post", "put",
                            "delete"], endpoint: Endpoints,
                            params: dict[str, Any] | None = None,) -> dict[str, Any] | bytes:
        headers: Dict[str, str] = self.http.build_api_mafia_headers()
        return await (self.http.mafia_request(
            self.http.api_mafia_url, method, endpoint, params, headers))

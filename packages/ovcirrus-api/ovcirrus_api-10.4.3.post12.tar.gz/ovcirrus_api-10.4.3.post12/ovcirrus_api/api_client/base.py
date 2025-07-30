import logging
from typing import Optional, Dict, Any

import httpx
import backoff

from .auth import Authenticator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class BaseClient:
    def __init__(self, base_url: str, auth: Authenticator):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.client = httpx.AsyncClient()

    def _get_headers(self) -> Dict[str, str]:
        token = self.auth.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    @backoff.on_exception(
        backoff.expo,
        (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError),
        max_tries=2
    )
    async def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        kwargs.setdefault("headers", headers)

        try:
            response = await self.client.request(method, url, **kwargs)

            if response.status_code == 401:
                logger.warning("Received 401. Attempting re-authentication...")
                if self.auth.force_relogin():
                    headers = self._get_headers()
                    kwargs["headers"] = headers
                    response = await self.client.request(method, url, **kwargs)
                else:
                    logger.error("Re-authentication failed. Exiting.")
                    return None

            response.raise_for_status()

            if response.content:
                try:
                    return response.json()
                except Exception as e:
                    logger.warning(f"Failed to decode JSON: {e}")
                    return None
            return None

        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error {e.response.status_code}: {e.response.text}")
            return e.response.json()
        except Exception as e:
            logger.exception(f"Unhandled exception: {e}")
            raise

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        return await self._request("GET", endpoint, params=params)

    async def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        return await self._request("POST", endpoint, json=json)

    async def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        return await self._request("PUT", endpoint, json=json)

    async def delete(self, endpoint: str) -> Optional[Any]:
        return await self._request("DELETE", endpoint)

    async def close(self):
        await self.client.aclose()

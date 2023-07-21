"""Asynchronous Python client for the Worldtides API."""
from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import metadata
from typing import Any, cast

import async_timeout
from aiohttp import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .exceptions import WorldtidesConnectionError, WorldtidesError
from .models import StationResponse


@dataclass
class Worldtides:
    """Main class for handling connections with Worldtides."""

    session: ClientSession | None = None
    request_timeout: int = 10
    api_host: str = "www.worldtides.info"
    timezone = timezone.utc
    _close_session: bool = False
    _credit_usage: dict[datetime, int] = field(default_factory=dict)
    _api_key: str | None = None
    _contributing_user: bool = False

    def authenticate(self, api_key: str) -> None:
        """Authenticate the user."""
        self._api_key = api_key

    async def _request(
        self,
        uri: str,
        *,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle a request to Worldtides.

        A generic method for sending/handling HTTP requests done against
        Worldtides.

        Args:
        ----
            uri: the path to call.
            data: the query parameters to add.

        Returns:
        -------
            A Python dictionary (JSON decoded) with the response from
            the API.

        Raises:
        ------
            WorldtidesConnectionError: An error occurred while communicating with
                the Worldtides API.
            WorldtidesError: Received an unexpected response from the Worldtides API.
        """
        version = metadata.version(__package__)
        url = URL.build(
            scheme="https",
            host=self.api_host,
            port=443,
            path="/api/v3",
        )

        headers = {
            "User-Agent": f"PythonWorldtides/{version}",
            "Accept": "application/json, text/plain, */*",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True
        data.setdefault(uri, "")
        data.setdefault("key", self._api_key)

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    METH_GET,
                    url.with_query(data),
                    headers=headers,
                )
                response.raise_for_status()
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Worldtides API"
            raise WorldtidesConnectionError(msg) from exception
        except (
            ClientError,
            ClientResponseError,
            socket.gaierror,
        ) as exception:
            msg = "Error occurred while communicating with Worldtides API"
            raise WorldtidesConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected response from the Worldtides API"
            raise WorldtidesError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return cast(dict[str, Any], await response.json())

    async def get_stations(
        self,
        latitude: float,
        longitude: float,
        station_distance: int,
    ) -> StationResponse:
        """Retrieve stations for a specific place with radius."""
        data = await self._request(
            "stations",
            data={
                "lat": latitude,
                "lon": longitude,
                "stationDistance": station_distance,
            },
        )

        return StationResponse.parse_obj(data)

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Worldtides:
        """Async enter.

        Returns
        -------
            The Worldtides object.
        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.
        """
        await self.close()

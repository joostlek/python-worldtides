"""Tests for the Worldtides Library."""
import asyncio

import aiohttp
import pytest
from aiohttp import BasicAuth, ClientError
from aiohttp.web_request import BaseRequest
from aresponses import Response, ResponsesMockServer

from python_worldtides import (
    Worldtides, StationResponse,
)
from python_worldtides.exceptions import WorldtidesUnauthenticatedError

from . import load_fixture

WORLDTIDES_URL = "www.worldtides.info"


async def test_stations(
    aresponses: ResponsesMockServer,
) -> None:
    """Test retrieving states."""
    aresponses.add(
        WORLDTIDES_URL,
        "/api/v3?lat=33.768321&lon=-118.195617&stationDistance=50&stations=&key=abc",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("stations.json"),
        ),
        match_querystring=True
    )
    async with aiohttp.ClientSession() as session:
        worldtides = Worldtides(session=session)
        worldtides.authenticate("abc")
        response: StationResponse = await worldtides.get_stations(33.768321, -118.195617, 50)
        assert len(response.stations) == 1

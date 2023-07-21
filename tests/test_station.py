"""Tests for the Worldtides Library."""
import asyncio

import aiohttp
import pytest
from aiohttp import ClientError
from aiohttp.web_request import BaseRequest
from aresponses import Response, ResponsesMockServer

from python_worldtides import (
    StationResponse,
    Worldtides,
    WorldtidesError,
)
from python_worldtides.exceptions import WorldtidesConnectionError

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
        match_querystring=True,
    )
    async with aiohttp.ClientSession() as session:
        worldtides = Worldtides(session=session)
        worldtides.authenticate("abc")
        response: StationResponse = await worldtides.get_stations(
            33.768321,
            -118.195617,
            50,
        )
        assert len(response.stations) == 1


async def test_new_session(
    aresponses: ResponsesMockServer,
) -> None:
    """Test that it creates a new session if not given one."""
    aresponses.add(
        WORLDTIDES_URL,
        "/api/v3",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("stations.json"),
        ),
    )
    async with Worldtides() as worldtides:
        worldtides.authenticate("abc")
        assert not worldtides.session
        await worldtides.get_stations(33.768321, -118.195617, 50)
        assert worldtides.session


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout."""

    # Faking a timeout by sleeping
    async def response_handler(_: BaseRequest) -> Response:
        """Response handler for this test."""
        await asyncio.sleep(2)
        return aresponses.Response(body="Goodmorning!")

    aresponses.add(
        WORLDTIDES_URL,
        "/api/v3",
        "GET",
        response_handler,
    )

    async with aiohttp.ClientSession() as session:
        worldtides = Worldtides(session=session, request_timeout=1)
        worldtides.authenticate("abc")
        with pytest.raises(WorldtidesConnectionError):
            assert await worldtides.get_stations(33.768321, -118.195617, 50)
        await worldtides.close()


async def test_request_error(aresponses: ResponsesMockServer) -> None:
    """Test request error."""

    async def response_handler(_: BaseRequest) -> Response:
        """Response handler for this test."""
        raise ClientError

    aresponses.add(
        WORLDTIDES_URL,
        "/api/v3",
        "GET",
        response_handler,
    )

    async with aiohttp.ClientSession() as session:
        worldtides = Worldtides(session=session)
        worldtides.authenticate("abc")
        with pytest.raises(WorldtidesConnectionError):
            assert await worldtides.get_stations(33.768321, -118.195617, 50)
        await worldtides.close()


async def test_unexpected_server_response(
    aresponses: ResponsesMockServer,
) -> None:
    """Test handling a server error."""
    aresponses.add(
        WORLDTIDES_URL,
        "/api/v3",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "plain/text"},
            text="Yes",
        ),
    )

    async with aiohttp.ClientSession() as session:
        worldtides = Worldtides(session=session)
        worldtides.authenticate("abc")
        with pytest.raises(WorldtidesError):
            assert await worldtides.get_stations(33.768321, -118.195617, 50)
        await worldtides.close()

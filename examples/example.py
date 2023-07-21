"""Asynchronous Python client for the Worldtides API."""

import asyncio

from python_worldtides import StationResponse, Worldtides


async def main() -> None:
    """Show example of fetching tide stations from Worldtides."""
    async with Worldtides() as worldtides:
        states: StationResponse = await worldtides.get_stations(10.0, 10.0, 50)
        print(states)


if __name__ == "__main__":
    asyncio.run(main())

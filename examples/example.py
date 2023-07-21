"""Asynchronous Python client for the Worldtides API."""

import asyncio

from python_worldtides import Worldtides, StationResponse


async def main() -> None:
    """Show example of fetching tide stations from Worldtides."""
    async with Worldtides() as worldtides:
        states: StationResponse = await worldtides.get_stations()
        print(states)


if __name__ == "__main__":
    asyncio.run(main())

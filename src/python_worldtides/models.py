"""Asynchronous Python client for the Worldtides API."""
from __future__ import annotations

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field  # type: ignore


class StationResponse(BaseModel):
    """Represents the station response."""

    status: int = Field(...)
    call_count: int = Field(..., alias="callCount")
    latitude: float = Field(..., alias="requestLat")
    longitude: float = Field(..., alias="requestLon")
    station_distance: int = Field(..., alias="stationDistance")
    stations: list[Station] = Field([])


class Station(BaseModel):
    """Represents the station model."""

    identifier: str = Field(..., alias="id")
    name: str = Field(...)
    latitude: float = Field(..., alias="lat")
    longitude: float = Field(..., alias="lon")
    timezone: str = Field(...)


StationResponse.update_forward_refs()
Station.update_forward_refs()

"""Asynchronous Python client for the Worldtides API."""


class WorldtidesError(Exception):
    """Generic exception."""


class WorldtidesConnectionError(WorldtidesError):
    """Worldtides connection exception."""


class WorldtidesCoordinateError(WorldtidesError):
    """Worldtides coordinate exception."""


class WorldtidesUnauthenticatedError(WorldtidesError):
    """Worldtides unauthenticated exception."""

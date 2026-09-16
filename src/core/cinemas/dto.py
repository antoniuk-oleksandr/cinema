"""Public cinema DTOs."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HallDTO:
    """Public hall summary."""

    name: str
    slug: str
    type: str
    capacity: int
    accessibility: dict[str, Any]


@dataclass(frozen=True)
class CinemaDTO:
    """Public cinema representation."""

    id: int
    name: str
    slug: str
    city: str
    address: str
    timezone: str
    phone: str
    email: str
    status: str
    hall_count: int
    hall_types: tuple[str, ...]
    halls: tuple[HallDTO, ...] = ()

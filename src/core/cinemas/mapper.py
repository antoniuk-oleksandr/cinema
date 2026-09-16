"""Cinema entity-to-DTO mappings."""

from collections.abc import Iterable
from typing import Protocol, cast

from ..models import Cinema, Hall, HallType
from .dto import CinemaDTO, HallDTO


class _HallManager(Protocol):
    """Typed view of the reverse relation used by this mapper."""

    def all(self) -> Iterable[Hall]: ...


def _hall_values(cinema: Cinema) -> Iterable[Hall]:
    """Return halls through Django's reverse relation."""
    return cast(_HallManager, cinema.halls).all()  # pyright: ignore[reportAttributeAccessIssue]


def cinema_to_dto(cinema: Cinema, include_halls: bool = False) -> CinemaDTO:
    """Map a cinema and prefetched halls to a DTO."""
    halls = tuple(
        HallDTO(
            name=cast(str, hall.name),
            slug=cast(str, hall.slug),
            type=cast(str, hall.hall_type),
            capacity=cast(int, hall.capacity),
            accessibility=cast(dict[str, object], hall.accessibility),
        )
        for hall in _hall_values(cinema)
    )
    hall_type_values = {hall.type for hall in halls}
    choices = cast(Iterable[tuple[str, str]], HallType.choices)
    hall_types = tuple(hall_type for hall_type, _ in choices if hall_type in hall_type_values)
    return CinemaDTO(
        id=cast(int, cinema.id),  # pyright: ignore[reportAttributeAccessIssue]
        name=cast(str, cinema.name),
        slug=cast(str, cinema.slug),
        city=cast(str, cinema.city),
        address=cast(str, cinema.address),
        timezone=cast(str, cinema.timezone),
        phone=cast(str, cinema.phone),
        email=cast(str, cinema.email),
        status=cast(str, cinema.status),
        hall_count=cast(int, getattr(cinema, "hall_count", len(halls))),
        hall_types=hall_types,
        halls=halls if include_halls else (),
    )

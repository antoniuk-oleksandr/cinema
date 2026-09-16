"""Cinema application services."""

from collections.abc import Iterable
from typing import cast

from django.db.models import QuerySet

from ..models import Cinema
from .dto import CinemaDTO
from .errors import CinemaNotFoundError, CinemaUnavailableError
from .mapper import cinema_to_dto
from .repository import CinemaRepository


class CinemaService:
    """Coordinate cinema listing and detail retrieval."""

    def __init__(self, repository: CinemaRepository | None = None) -> None:
        self.repository = repository or CinemaRepository()

    def list_cinemas(self, **filters: str) -> list[CinemaDTO]:
        """Return filtered cinema DTOs."""
        cinemas = cast(Iterable[Cinema], self.list_cinema_entities(**filters))
        return [cinema_to_dto(cinema) for cinema in cinemas]

    def list_cinema_entities(self, **filters: str) -> QuerySet[Cinema]:
        """Return filtered cinema entities for database-level pagination."""
        return self.repository.list_public(**filters)

    def get_cinema(self, slug: str) -> CinemaDTO:
        """Return an active cinema or a safe application error."""
        try:
            return cinema_to_dto(self.repository.get_by_slug(slug), include_halls=True)
        except CinemaNotFoundError as error:
            raise CinemaUnavailableError() from error

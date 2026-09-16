"""Movie catalog service boundary."""

from typing import Protocol

from ..models import Movie
from .dto import MovieDTO
from .errors import MovieNotFoundError, MovieUnavailableError
from .mapper import movie_to_dto
from .repository import MovieRepository


class MovieRepositoryProtocol(Protocol):
    """Persistence contract required by the movie service."""

    def get_by_slug(self, slug: str) -> Movie:  # pyright: ignore[reportReturnType]
        """Return a movie by slug or raise a domain error."""


class MovieService:
    """Coordinate movie retrieval."""

    def __init__(self, repository: MovieRepositoryProtocol | None = None) -> None:
        if repository is None:
            repository = MovieRepository()
        self.repository = repository

    def get_movie(self, slug: str) -> MovieDTO:
        """Retrieve a public movie DTO."""
        try:
            return movie_to_dto(self.repository.get_by_slug(slug))
        except MovieNotFoundError as error:
            raise MovieUnavailableError() from error


__all__ = ["MovieService", "MovieUnavailableError"]

"""Movie catalog service boundary."""

from .dto import MovieDTO
from .errors import MovieNotFoundError, MovieUnavailableError
from .mapper import movie_to_dto


class MovieService:
    """Coordinate movie retrieval."""

    def __init__(self, repository=None) -> None:
        self.repository = (
            repository
            or __import__("core.movies.repository", fromlist=["MovieRepository"]).MovieRepository()
        )

    def get_movie(self, slug: str) -> MovieDTO:
        """Retrieve a public movie DTO."""
        try:
            return movie_to_dto(self.repository.get_by_slug(slug))
        except MovieNotFoundError as error:
            raise MovieUnavailableError() from error


__all__ = ["MovieService", "MovieUnavailableError"]

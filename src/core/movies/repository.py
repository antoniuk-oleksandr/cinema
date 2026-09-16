"""Movie catalog repository boundary."""

from django.db.models import QuerySet

from ..models import Movie
from .errors import MovieNotFoundError


class MovieRepository:
    """Load movies with public relations."""

    def get_by_slug(self, slug: str) -> Movie:
        """Find a movie or raise a domain error."""
        movie = self.queryset().filter(slug=slug).first()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        if movie is None:
            raise MovieNotFoundError()
        return movie  # pyright: ignore[reportReturnType, reportUnknownVariableType]

    @staticmethod
    def queryset() -> QuerySet[Movie]:
        """Build the optimized detail query."""
        return Movie.objects.select_related("language").prefetch_related(  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
            "genres", "screenplays", "actors", "studios", "directors", "countries"
        )


__all__ = ["MovieNotFoundError", "MovieRepository"]

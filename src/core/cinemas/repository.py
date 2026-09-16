"""Cinema persistence boundary."""

from typing import Protocol, cast

from django.db.models import Count, Exists, OuterRef, Q, QuerySet

from ..models import Cinema, CinemaStatus, Hall
from .errors import CinemaNotFoundError


class _CinemaQuerySet(Protocol):
    """Typed subset of queryset operations used by the repository."""

    def filter(self, *args: object, **kwargs: object) -> "_CinemaQuerySet": ...
    def annotate(self, **kwargs: object) -> "_CinemaQuerySet": ...
    def prefetch_related(self, *lookups: str) -> "_CinemaQuerySet": ...
    def distinct(self, *field_names: str) -> "_CinemaQuerySet": ...
    def order_by(self, *field_names: str) -> "_CinemaQuerySet": ...
    def first(self) -> Cinema | None: ...


class _CinemaManager(Protocol):
    """Typed subset of Django's dynamically provided model manager."""

    def filter(self, *args: object, **kwargs: object) -> "_CinemaQuerySet": ...
    def prefetch_related(self, *lookups: str) -> "_CinemaQuerySet": ...


class _HallManager(Protocol):
    """Typed subset of the hall model manager."""

    def filter(self, *args: object, **kwargs: object) -> "_CinemaQuerySet": ...


class CinemaRepository:
    """Query cinemas and their halls."""

    def list_public(
        self, query: str = "", city: str = "", hall_type: str = "", status: str = ""
    ) -> QuerySet[Cinema]:
        """Return the filtered public cinema queryset with derived hall data."""
        cinemas = cast(_CinemaManager, Cinema.objects)  # pyright: ignore[reportAttributeAccessIssue]
        queryset = cinemas.filter(status=status or CinemaStatus.ACTIVE)
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(city__icontains=query)  # pyright: ignore[reportOperatorIssue]
                | Q(address__icontains=query)  # pyright: ignore[reportOperatorIssue]
            )
        if city:
            queryset = queryset.filter(city__iexact=city)
        if hall_type:
            halls = cast(_HallManager, Hall.objects)  # pyright: ignore[reportAttributeAccessIssue]
            queryset = queryset.filter(
                Exists(halls.filter(cinema=OuterRef("pk"), hall_type=hall_type))
            )
        return cast(
            QuerySet[Cinema],
            queryset.annotate(hall_count=Count("halls", distinct=True))
            .prefetch_related("halls")
            .distinct()
            .order_by("name", "pk"),
        )

    def get_by_slug(self, slug: str) -> Cinema:
        """Return an active cinema by slug or raise the feature error."""
        cinema = (
            cast(_CinemaManager, Cinema.objects)  # pyright: ignore[reportAttributeAccessIssue]
            .prefetch_related("halls")
            .filter(slug=slug, status="active")
            .first()
        )
        if cinema is None:
            raise CinemaNotFoundError()
        return cinema

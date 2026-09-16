from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from django.db.models import QuerySet

from core.cinemas.dto import CinemaDTO, HallDTO
from core.cinemas.errors import CinemaNotFoundError, CinemaUnavailableError
from core.cinemas.mapper import cinema_to_dto
from core.cinemas.repository import CinemaRepository
from core.cinemas.service import CinemaService
from core.models import Cinema, Hall


@pytest.fixture
def cinema_records() -> tuple[Cinema, Cinema, Cinema]:
    center = Cinema.objects.create(
        name="Cinema Center",
        slug="cinema-center",
        city="Kyiv",
        address="10 Main Street",
        timezone="Europe/Kyiv",
    )
    Hall.objects.create(cinema=center, name="IMAX", slug="imax", capacity=180, hall_type="imax")
    Hall.objects.create(cinema=center, name="VIP", slug="vip", capacity=80, hall_type="vip")
    kyiv = Cinema.objects.create(
        name="Kyiv Standard",
        slug="kyiv-standard",
        city="Kyiv",
        address="Other Street",
        timezone="Europe/Kyiv",
    )
    Hall.objects.create(cinema=kyiv, name="Standard", slug="standard", capacity=100)
    inactive = Cinema.objects.create(
        name="Inactive Center",
        slug="inactive-center",
        city="Lviv",
        address="Old Road",
        timezone="Europe/Kyiv",
        status="inactive",
    )
    Hall.objects.create(cinema=inactive, name="IMAX", slug="imax", capacity=200, hall_type="imax")
    return center, kyiv, inactive


@pytest.mark.django_db
def test_repository_applies_filters_without_duplicate_cinemas(
    cinema_records: tuple[Cinema, Cinema, Cinema],
) -> None:
    results = CinemaRepository().list_public(city="Kyiv", hall_type="imax")

    assert isinstance(results, QuerySet)
    assert list(results.values_list("slug", flat=True)) == ["cinema-center"]
    assert results[0].hall_count == 2


@pytest.mark.django_db
def test_repository_returns_only_active_cinema_for_detail(
    cinema_records: tuple[Cinema, Cinema, Cinema],
) -> None:
    repository = CinemaRepository()

    assert repository.get_by_slug("cinema-center").slug == "cinema-center"
    with pytest.raises(CinemaNotFoundError):
        repository.get_by_slug("inactive-center")
    with pytest.raises(CinemaNotFoundError):
        repository.get_by_slug("missing")


def test_mapper_maps_halls_and_preserves_declared_hall_type_order() -> None:
    halls = [
        SimpleNamespace(
            name="VIP",
            slug="vip",
            hall_type="vip",
            capacity=80,
            accessibility={"wheelchair_accessible": True},
        ),
        SimpleNamespace(name="IMAX", slug="imax", hall_type="imax", capacity=180, accessibility={}),
    ]
    cinema = SimpleNamespace(
        id=7,
        name="Cinema Center",
        slug="cinema-center",
        city="Kyiv",
        address="10 Main Street",
        timezone="Europe/Kyiv",
        phone="",
        email="",
        status="active",
        halls=SimpleNamespace(all=lambda: halls),
    )

    dto = cinema_to_dto(cinema, include_halls=True)

    assert dto == CinemaDTO(
        id=7,
        name="Cinema Center",
        slug="cinema-center",
        city="Kyiv",
        address="10 Main Street",
        timezone="Europe/Kyiv",
        phone="",
        email="",
        status="active",
        hall_count=2,
        hall_types=("imax", "vip"),
        halls=(
            HallDTO("VIP", "vip", "vip", 80, {"wheelchair_accessible": True}),
            HallDTO("IMAX", "imax", "imax", 180, {}),
        ),
    )


def test_service_maps_list_entities_and_translates_not_found() -> None:
    repository = Mock()
    repository.list_public.return_value = []
    repository.get_by_slug.side_effect = CinemaNotFoundError()
    service = CinemaService(repository)

    assert service.list_cinemas(city="Kyiv") == []
    repository.list_public.assert_called_once_with(city="Kyiv")

    with pytest.raises(CinemaUnavailableError, match="Cinema is unavailable"):
        service.get_cinema("missing")
    repository.get_by_slug.assert_called_once_with("missing")


def test_service_returns_entity_queryset_for_database_pagination() -> None:
    queryset = Mock()
    repository = Mock()
    repository.list_public.return_value = queryset

    result = CinemaService(repository).list_cinema_entities(status="inactive")

    assert result is queryset
    repository.list_public.assert_called_once_with(status="inactive")

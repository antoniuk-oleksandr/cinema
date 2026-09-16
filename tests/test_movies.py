from datetime import date

import pytest
from django.test import Client
from django.utils import timezone

from core.languages.dto import LanguageDTO
from core.models import Actor, Country, Director, Genre, Language, Movie, Screenplay, Studio
from core.movies.mapper import movie_to_dto
from core.movies.repository import MovieNotFoundError, MovieRepository
from core.movies.service import MovieService, MovieUnavailableError


@pytest.mark.django_db
def test_movie_detail_returns_public_catalog_metadata() -> None:
    language = Language.objects.create(code="en", name="English")
    movie = Movie.objects.create(
        title="A Film",
        slug="a-film",
        year=2026,
        language=language,
        rating="PG",
        duration_in_minutes=120,
        short_description="Short",
        full_description="Full",
        release_date=date(2026, 5, 1),
        status="draft",
    )
    movie.genres.add(Genre.objects.create(name="Drama"))
    movie.screenplays.add(Screenplay.objects.create(first_name="Jane", surname="Writer"))
    movie.actors.add(Actor.objects.create(first_name="Alex", surname="Actor"))
    movie.studios.add(Studio.objects.create(name="Studio"))
    movie.directors.add(Director.objects.create(first_name="Sam", surname="Director"))
    movie.countries.add(Country.objects.create(name="Ukraine"))

    response = Client().get("/api/v1/movies/a-film/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "A Film"
    assert payload["release_date"] == "2026-05-01"
    assert payload["genres"] == [{"name": "Drama"}]
    assert payload["actors"] == [{"first_name": "Alex", "surname": "Actor"}]
    assert payload["screenplays"] == [{"first_name": "Jane", "surname": "Writer"}]
    assert payload["studios"] == [{"name": "Studio"}]
    assert payload["directors"] == [{"first_name": "Sam", "surname": "Director"}]
    assert payload["countries"] == [{"name": "Ukraine"}]
    assert payload["language"] == {"name": "English"}
    assert "status" not in payload
    assert "created_at" in payload
    assert timezone.is_aware(movie.created_at)


@pytest.mark.django_db
def test_movie_detail_returns_problem_response_when_slug_is_unknown() -> None:
    response = Client().get("/api/v1/movies/missing/")

    assert response.status_code == 404
    assert response["Content-Type"].startswith("application/problem+json")
    assert response.json()["status"] == 404


def test_repository_and_service_boundaries() -> None:
    class MissingRepository:
        def get_by_slug(self, slug: str) -> Movie:
            raise MovieNotFoundError()

    with pytest.raises(MovieNotFoundError):
        MissingRepository().get_by_slug("missing")
    with pytest.raises(MovieUnavailableError):
        MovieService(MissingRepository()).get_movie("missing")


@pytest.mark.django_db
def test_repository_raises_domain_error_for_unknown_slug() -> None:
    with pytest.raises(MovieNotFoundError):
        MovieRepository().get_by_slug("missing")


@pytest.mark.django_db
def test_mapper_does_not_expose_status() -> None:
    language = Language.objects.create(code="fr", name="French")
    movie = Movie.objects.create(
        title="Mapped",
        slug="mapped",
        year=2026,
        language=language,
        rating="G",
        duration_in_minutes=90,
        status="draft",
    )
    dto = movie_to_dto(MovieRepository.queryset().get(pk=movie.pk))
    assert not hasattr(dto, "status")
    assert isinstance(dto.language, LanguageDTO)

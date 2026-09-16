import pytest
from django.test import Client

from core.models import Cinema, Hall


@pytest.fixture
def cinemas() -> tuple[Cinema, Cinema, Cinema]:
    center = Cinema.objects.create(
        name="Cinema Center",
        slug="cinema-center",
        city="Kyiv",
        address="10 Main Street",
        timezone="Europe/Kyiv",
        phone="+380441234567",
        email="center@example.com",
    )
    Hall.objects.create(
        cinema=center,
        name="Hall 1",
        slug="hall-1",
        capacity=180,
        hall_type="imax",
        accessibility={"wheelchair_accessible": True, "audio_description": True},
    )
    Hall.objects.create(
        cinema=center,
        name="Hall 2",
        slug="hall-2",
        capacity=80,
        hall_type="vip",
        accessibility={},
    )
    kyiv_standard = Cinema.objects.create(
        name="Kyiv Standard",
        slug="kyiv-standard",
        city="Kyiv",
        address="Other Street",
        timezone="Europe/Kyiv",
    )
    Hall.objects.create(
        cinema=kyiv_standard,
        name="Standard",
        slug="standard",
        capacity=100,
        hall_type="standard",
    )
    inactive = Cinema.objects.create(
        name="Inactive Center",
        slug="inactive-center",
        city="Lviv",
        address="Old Road",
        timezone="Europe/Kyiv",
        status="inactive",
    )
    Hall.objects.create(
        cinema=inactive,
        name="IMAX",
        slug="imax",
        capacity=200,
        hall_type="imax",
    )
    return center, kyiv_standard, inactive


@pytest.mark.django_db
def test_cinema_list_returns_paginated_public_shape_and_derived_fields(
    cinemas: tuple[Cinema, Cinema, Cinema],
) -> None:
    response = Client().get("/api/v1/cinemas/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    assert payload["results"][0]["name"] == "Cinema Center"
    assert payload["results"][0]["hall_count"] == 2
    assert payload["results"][0]["hall_types"] == ["imax", "vip"]
    assert payload["results"][0]["phone"] == "+380441234567"


@pytest.mark.django_db
def test_cinema_list_filters_use_and_semantics_and_status(
    cinemas: tuple[Cinema, Cinema, Cinema],
) -> None:
    client = Client()

    response = client.get("/api/v1/cinemas/?city=Kyiv&hall_type=imax")
    assert response.status_code == 200
    assert [item["slug"] for item in response.json()["results"]] == ["cinema-center"]
    assert response.json()["results"][0]["hall_count"] == 2
    assert response.json()["results"][0]["hall_types"] == ["imax", "vip"]

    response = client.get("/api/v1/cinemas/?status=inactive")
    assert response.status_code == 200
    assert [item["slug"] for item in response.json()["results"]] == ["inactive-center"]

    response = client.get("/api/v1/cinemas/?query=main")
    assert [item["slug"] for item in response.json()["results"]] == ["cinema-center"]


@pytest.mark.django_db
def test_cinema_detail_contains_hall_summaries(cinemas: tuple[Cinema, Cinema, Cinema]) -> None:
    response = Client().get("/api/v1/cinemas/cinema-center/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["slug"] == "cinema-center"
    assert payload["halls"] == [
        {
            "name": "Hall 1",
            "slug": "hall-1",
            "type": "imax",
            "capacity": 180,
            "accessibility": {"wheelchair_accessible": True, "audio_description": True},
        },
        {"name": "Hall 2", "slug": "hall-2", "type": "vip", "capacity": 80, "accessibility": {}},
    ]


@pytest.mark.django_db
def test_cinema_detail_hides_inactive_and_unknown_cinemas() -> None:
    Cinema.objects.create(
        name="Inactive",
        slug="inactive",
        city="Kyiv",
        address="Road",
        timezone="Europe/Kyiv",
        status="inactive",
    )
    client = Client()
    for slug in ("inactive", "missing"):
        response = client.get(f"/api/v1/cinemas/{slug}/")
        assert response.status_code == 404
        assert response["Content-Type"].startswith("application/problem+json")
        assert response.json()["status"] == 404


@pytest.mark.django_db
def test_cinema_list_rejects_invalid_filters(cinemas: tuple[Cinema, Cinema, Cinema]) -> None:
    response = Client().get("/api/v1/cinemas/?hall_type=unknown&page=0")

    assert response.status_code == 400
    assert response["Content-Type"].startswith("application/problem+json")

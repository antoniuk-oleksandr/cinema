from unittest.mock import MagicMock

import pytest
from django.test import Client

from core.models import Actor, Country, Director, Genre, Language, Movie, Screenplay, Studio


def test_operational_endpoints() -> None:
    client = Client()

    info = client.get("/info")
    assert info.status_code == 200
    assert info.json()["service"] == "cinema-api"

    metrics = client.get("/metrics")
    assert metrics.status_code == 200


def test_operational_endpoints_only_accept_get() -> None:
    response = Client().post("/health/live")
    assert response.status_code == 405


@pytest.mark.django_db
def test_readiness_when_dependencies_are_healthy(monkeypatch) -> None:
    from core import views

    cursor = MagicMock()
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    monkeypatch.setattr(views, "connection", connection)

    redis_client = MagicMock()
    monkeypatch.setattr(views.redis, "Redis", MagicMock(return_value=redis_client))

    broker = MagicMock()
    monkeypatch.setattr(views.pika, "BlockingConnection", MagicMock(return_value=broker))

    response = Client().get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    redis_client.ping.assert_called_once()
    broker.close.assert_called_once()


@pytest.mark.django_db
def test_readiness_when_a_dependency_fails(monkeypatch) -> None:
    from core import views

    monkeypatch.setattr(views.connection, "cursor", MagicMock(side_effect=RuntimeError("db down")))
    monkeypatch.setattr(views.redis, "Redis", MagicMock(side_effect=RuntimeError("redis down")))
    monkeypatch.setattr(
        views.pika, "BlockingConnection", MagicMock(side_effect=RuntimeError("broker down"))
    )

    response = Client().get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


def test_catalog_model_string_representations() -> None:
    assert str(Language(name="English", code="en")) == "English"
    assert str(Genre(name="Drama")) == "Drama"
    assert str(Country(name="Ukraine")) == "Ukraine"
    assert str(Studio(name="Cinema Studio")) == "Cinema Studio"
    assert str(Actor(first_name="Jane", surname="Doe")) == "Jane Doe"
    assert str(Screenplay(first_name="John", surname="Doe")) == "John Doe"
    assert str(Director(first_name="Alex", surname="Doe")) == "Alex Doe"
    assert str(Movie(title="A Film")) == "A Film"


@pytest.mark.django_db
def test_liveness() -> None:
    response = Client().get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

"""Centralized RFC 7807 exception handling."""

from collections.abc import Callable
from typing import Any, cast

from rest_framework.response import Response
from rest_framework.views import exception_handler  # pyright: ignore[reportUnknownVariableType]

from .cinemas.errors import CinemaUnavailableError
from .movies.errors import MovieUnavailableError

# DRF's exception handler accepts dynamically typed exception/context objects.

type JsonValue = str | int | float | bool | list["JsonValue"] | dict[str, "JsonValue"] | None


def problem_exception_handler(exc: Exception, context: dict[str, JsonValue]) -> Response:
    """Convert DRF and application errors into RFC 7807 responses."""
    handler = cast(Callable[[Exception, dict[str, Any]], Response | None], exception_handler)
    response = handler(exc, cast(dict[str, Any], context))
    if isinstance(exc, (MovieUnavailableError, CinemaUnavailableError)):
        response = Response({"detail": str(exc)}, status=404)
    status = response.status_code if response else 500
    raw_data: object = (
        cast(object, response.data)  # pyright: ignore[reportUnknownMemberType]
        if response
        else {"detail": "An unexpected error occurred."}
    )
    data = cast(dict[str, JsonValue], raw_data) if isinstance(raw_data, dict) else {}
    detail = data.get("detail", "Request failed")
    return Response(
        {
            "type": f"https://httpstatuses.com/{status}",
            "title": "Request failed",
            "status": status,
            "detail": str(detail),
            "errors": data,
        },
        status=status,
        content_type="application/problem+json",
    )

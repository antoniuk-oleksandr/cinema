from rest_framework.response import Response
from rest_framework.views import exception_handler

from .movies.errors import MovieUnavailableError

type JsonValue = str | int | float | bool | list["JsonValue"] | dict[str, "JsonValue"] | None


def problem_exception_handler(exc: Exception, context: dict[str, JsonValue]) -> Response:
    """Convert DRF and application errors into RFC 7807 responses."""
    response = exception_handler(exc, context)
    if isinstance(exc, MovieUnavailableError):
        response = Response({"detail": str(exc)}, status=404)
    status = response.status_code if response else 500
    data = response.data if response else {"detail": "An unexpected error occurred."}
    return Response(
        {
            "type": f"https://httpstatuses.com/{status}",
            "title": "Request failed",
            "status": status,
            "detail": str(data.get("detail", "Request failed"))
            if isinstance(data, dict)
            else "Request failed",
            "errors": data,
        },
        status=status,
        content_type="application/problem+json",
    )

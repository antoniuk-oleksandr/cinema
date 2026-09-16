import uuid
from collections.abc import Callable
from contextvars import ContextVar

from django.http import HttpRequest, HttpResponse

request_id = ContextVar("request_id", default="-")


class RequestContextMiddleware:
    """Attach a stable request identifier to inbound and outbound HTTP traffic."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize the middleware with Django's next request handler."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Propagate the request ID through the current HTTP request."""
        value = request.headers.get("X-Request-ID", str(uuid.uuid4()))  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
        request_id.set(value)
        response = self.get_response(request)
        response["X-Request-ID"] = value
        return response

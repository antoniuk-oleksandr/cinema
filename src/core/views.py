import logging
import os

import pika
import redis
from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from django_prometheus.exports import ExportToDjangoView

logger = logging.getLogger(__name__)


@require_GET
def live(request: HttpRequest) -> JsonResponse:
    """Return process liveness without checking external dependencies."""
    return JsonResponse({"status": "ok"})


@require_GET
def ready(request: HttpRequest) -> JsonResponse:
    """Return dependency readiness without exposing dependency details."""
    checks = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["postgres"] = "ok"
    except Exception:  # noqa: BLE001 - readiness must fail closed for any DB error
        checks["postgres"] = "error"
    try:
        redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            socket_connect_timeout=1,
        ).ping()
        checks["redis"] = "ok"
    except Exception:  # noqa: BLE001 - readiness must fail closed for any Redis error
        checks["redis"] = "error"
    try:
        params = pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
            port=int(os.getenv("RABBITMQ_PORT", "5672")),
            credentials=pika.PlainCredentials(
                os.getenv("RABBITMQ_USER", "admin"), os.getenv("RABBITMQ_PASSWORD", "admin")
            ),
            socket_timeout=1,
            blocked_connection_timeout=1,
        )
        broker = pika.BlockingConnection(params)
        broker.close()
        checks["rabbitmq"] = "ok"
    except Exception:  # noqa: BLE001 - readiness must fail closed for any broker error
        checks["rabbitmq"] = "error"
    healthy = all(value == "ok" for value in checks.values())
    if not healthy:
        logger.warning("readiness_check_failed", extra={"readiness_checks": checks})
    return JsonResponse(
        {"status": "ok" if healthy else "unavailable"}, status=200 if healthy else 503
    )


@require_GET
def info(request: HttpRequest) -> JsonResponse:
    """Return safe service metadata for operational inspection."""
    return JsonResponse(
        {
            "service": os.getenv("OTEL_SERVICE_NAME", "cinema-api"),
            "version": os.getenv("APP_VERSION", "0.1.0"),
            "environment": os.getenv("APP_ENV", "local"),
        }
    )


@require_GET
def metrics(request: HttpRequest) -> HttpResponse:
    """Expose application metrics in Prometheus format."""
    return ExportToDjangoView(request)

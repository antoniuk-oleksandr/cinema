"""Settings used by the fast, host-side test suite.

Integration tests are responsible for exercising PostgreSQL, Redis, and
RabbitMQ through Testcontainers. Unit and HTTP tests use isolated local
services so they do not require Docker DNS names such as ``postgres``.
"""

from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "cinema-test-cache",
    }
}

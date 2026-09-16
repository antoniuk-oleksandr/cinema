import os
from pathlib import Path
from typing import Any, cast

from .yaml_config import load_config

BASE_DIR = Path(__file__).resolve().parents[2]
APP_CONFIG: dict[str, Any] = load_config(BASE_DIR)
APP: dict[str, Any] = cast(dict[str, Any], APP_CONFIG.get("app", {}))
DJANGO_CONFIG: dict[str, Any] = cast(dict[str, Any], APP_CONFIG.get("django", {}))
LOGGING_VALUES: dict[str, Any] = cast(dict[str, Any], APP_CONFIG.get("logging", {}))
OBSERVABILITY_CONFIG: dict[str, Any] = cast(dict[str, Any], APP_CONFIG.get("observability", {}))
API_CONFIG: dict[str, Any] = cast(dict[str, Any], APP_CONFIG.get("api", {}))
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "local-only-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", str(DJANGO_CONFIG.get("debug", True))).lower() == "true"  # pyright: ignore[reportAny]
ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    ",".join(DJANGO_CONFIG.get("allowed_hosts", ["localhost", "127.0.0.1"])),  # pyright: ignore[reportAny]
).split(",")
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
INSTALLED_APPS = [
    "django_prometheus",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "health_check",
    "health_check.cache",
    "core",
]
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "core.middleware.RequestContextMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]
TEMPLATES = [  # pyright: ignore[reportUnknownVariableType]
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "admin"),
        "USER": os.getenv("POSTGRES_USER", "admin"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "admin"),
        "HOST": os.getenv("POSTGRES_HOST", "postgres"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}
CACHES = {
    "default": {
        "BACKEND": "django_prometheus.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', '6379')}/1",
    }
}
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
REST_FRAMEWORK = {  # pyright: ignore[reportUnknownVariableType]
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "core.exceptions.problem_exception_handler",
}
from datetime import timedelta

SIMPLE_JWT = {  # pyright: ignore[reportUnknownVariableType]
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
SPECTACULAR_SETTINGS = {  # pyright: ignore[reportUnknownVariableType]
    "TITLE": "Cinema API",
    "DESCRIPTION": "Cinema application API",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
API_DOCS_ENABLED = (
    os.getenv("API_DOCS_ENABLED", str(API_CONFIG.get("docs_enabled", False))).lower() == "true"  # pyright: ignore[reportAny]
)
LOGGING_CONFIG = None
LOGGING = {  # pyright: ignore[reportUnknownVariableType]
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s request_id=%(request_id)s trace_id=%(trace_id)s",
        }
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", LOGGING_VALUES.get("level", "INFO")),  # pyright: ignore[reportAny]
    },
}

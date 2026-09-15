import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from core.telemetry import configure_telemetry

configure_telemetry()
application = get_asgi_application()

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from core.telemetry import configure_telemetry

configure_telemetry()
application = get_wsgi_application()

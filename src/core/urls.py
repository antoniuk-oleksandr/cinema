from django.urls import path

from .views import info, live, metrics, ready

urlpatterns = [
    path("health/live", live),
    path("health/ready", ready),
    path("metrics", metrics),
    path("info", info),
]

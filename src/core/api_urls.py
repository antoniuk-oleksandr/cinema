"""Versioned business API routes.

Feature modules add relative routes here or include their own URL modules.
The project URL configuration applies the ``/api/v1/`` prefix once.
"""

from django.urls import include, path

urlpatterns = [path("", include("core.movies.urls"))]

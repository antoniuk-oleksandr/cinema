"""Versioned business API routes.

Feature modules add relative routes here or include their own URL modules.
The project URL configuration applies the ``/api/v1/`` prefix once.
"""

from django.urls import include, path  # pyright: ignore[reportUnknownVariableType]

# Django's include() factory is dynamically typed in the installed stubs.

urlpatterns = [path("", include("core.movies.urls")), path("", include("core.cinemas.urls"))]

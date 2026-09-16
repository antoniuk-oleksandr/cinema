"""URL routes for the cinema feature."""

from django.urls import path

from .controller import CinemaDetailView, CinemaListView

# Django's class-based view factory is dynamically typed in the installed stubs.

urlpatterns = [
    path("cinemas/", CinemaListView.as_view(), name="cinema-list"),  # pyright: ignore[reportUnknownMemberType]
    path("cinemas/<slug:slug>/", CinemaDetailView.as_view(), name="cinema-detail"),  # pyright: ignore[reportUnknownMemberType]
]

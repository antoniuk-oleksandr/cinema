"""URL routes for the movie catalog feature."""

from django.urls import path

from .controller import MovieDetailView

# Django's class-based view factory is dynamically typed in the installed stubs.

urlpatterns = [path("movies/<slug:slug>/", MovieDetailView.as_view(), name="movie-detail")]  # pyright: ignore[reportUnknownMemberType]

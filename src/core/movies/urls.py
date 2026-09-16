"""URL routes for the movie catalog feature."""

from django.urls import path

from .controller import MovieDetailView

urlpatterns = [path("movies/<slug:slug>/", MovieDetailView.as_view(), name="movie-detail")]

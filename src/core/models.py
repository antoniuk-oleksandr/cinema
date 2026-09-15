# Ruff's RUF012 rule does not understand Django's declarative Meta API.
# Django intentionally reads these list values as model metadata.
# ruff: noqa: RUF012

from django.db import models


class Language(models.Model):
    """A spoken language associated with one or more movies."""

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"], name="language_name_idx")]

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    """A movie genre used for catalog classification."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Country(models.Model):
    """A country associated with a movie's production or setting."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Studio(models.Model):
    """A production studio associated with a movie."""

    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"], name="studio_name_idx")]

    def __str__(self) -> str:
        return self.name


class Actor(models.Model):
    """An actor who can be associated with multiple movies."""

    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

    class Meta:
        ordering = ["surname", "first_name"]
        indexes = [models.Index(fields=["surname", "first_name"], name="actor_name_idx")]

    def __str__(self) -> str:
        return f"{self.first_name} {self.surname}"


class Screenplay(models.Model):
    """A screenplay author associated with one or more movies."""

    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

    class Meta:
        ordering = ["surname", "first_name"]
        indexes = [models.Index(fields=["surname", "first_name"], name="screenplay_name_idx")]

    def __str__(self) -> str:
        return f"{self.first_name} {self.surname}"


class Director(models.Model):
    """A director associated with one or more movies."""

    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

    class Meta:
        ordering = ["surname", "first_name"]
        indexes = [models.Index(fields=["surname", "first_name"], name="director_name_idx")]

    def __str__(self) -> str:
        return f"{self.first_name} {self.surname}"


class MovieRating(models.TextChoices):
    """Supported movie content ratings."""

    G = "G", "G"
    PG = "PG", "PG"
    PG_13 = "PG-13", "PG-13"
    R = "R", "R"
    NC_17 = "NC-17", "NC-17"


class Movie(models.Model):
    """A catalog movie and its related creative and classification metadata."""

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    year = models.PositiveSmallIntegerField()
    language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name="movies")
    rating = models.CharField(max_length=5, choices=MovieRating.choices)
    duration_in_minutes = models.PositiveSmallIntegerField()
    actors = models.ManyToManyField(Actor, related_name="movies", blank=True)
    screenplays = models.ManyToManyField(Screenplay, related_name="movies", blank=True)
    genres = models.ManyToManyField(Genre, related_name="movies", blank=True)
    countries = models.ManyToManyField(Country, related_name="movies", blank=True)
    studios = models.ManyToManyField(Studio, related_name="movies", blank=True)
    directors = models.ManyToManyField(Director, related_name="movies", blank=True)

    class Meta:
        ordering = ["-year", "title"]
        indexes = [
            models.Index(fields=["title"], name="movie_title_idx"),
            models.Index(fields=["year"], name="movie_year_idx"),
            models.Index(fields=["rating"], name="movie_rating_idx"),
            models.Index(fields=["language", "year"], name="movie_language_year_idx"),
        ]

    def __str__(self) -> str:
        return self.title

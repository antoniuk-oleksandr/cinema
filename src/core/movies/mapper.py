"""Movie catalog mapper boundary."""

from collections.abc import Iterable

from core.actors.dto import ActorDTO
from core.countries.dto import CountryDTO
from core.directors.dto import DirectorDTO
from core.genres.dto import GenreDTO
from core.languages.dto import LanguageDTO
from core.screenplays.dto import ScreenplayDTO
from core.studios.dto import StudioDTO

from ..models import Actor, Country, Director, Genre, Language, Movie, Screenplay, Studio
from .dto import MovieDTO


def _to_person(value: Actor | Director | Screenplay) -> ActorDTO | DirectorDTO | ScreenplayDTO:
    """Map a person entity to its public DTO."""
    return {Actor: ActorDTO, Director: DirectorDTO, Screenplay: ScreenplayDTO}[type(value)](
        first_name=value.first_name, surname=value.surname
    )


def _to_name(
    value: Country | Genre | Language | Studio,
) -> CountryDTO | GenreDTO | LanguageDTO | StudioDTO:
    """Map a named entity to its public DTO."""
    return {Country: CountryDTO, Genre: GenreDTO, Language: LanguageDTO, Studio: StudioDTO}[
        type(value)
    ](name=value.name)


def _actors(values: Iterable[Actor]) -> tuple[ActorDTO, ...]:
    """Map actors to actor DTOs."""
    return tuple(_to_person(value) for value in values)  # type: ignore[return-value]


def _directors(values: Iterable[Director]) -> tuple[DirectorDTO, ...]:
    """Map directors to director DTOs."""
    return tuple(_to_person(value) for value in values)  # type: ignore[return-value]


def _screenplays(values: Iterable[Screenplay]) -> tuple[ScreenplayDTO, ...]:
    """Map screenplays to screenplay DTOs."""
    return tuple(_to_person(value) for value in values)  # type: ignore[return-value]


def _actors_named(values: Iterable[Actor]) -> tuple[ActorDTO, ...]:
    """Map actors to actor DTOs."""
    return _actors(values)


def _genres(values: Iterable[Genre]) -> tuple[GenreDTO, ...]:
    """Map genres to genre DTOs."""
    return tuple(_to_name(value) for value in values)  # type: ignore[return-value]


def _studios(values: Iterable[Studio]) -> tuple[StudioDTO, ...]:
    """Map studios to studio DTOs."""
    return tuple(_to_name(value) for value in values)  # type: ignore[return-value]


def _countries(values: Iterable[Country]) -> tuple[CountryDTO, ...]:
    """Map countries to country DTOs."""
    return tuple(_to_name(value) for value in values)  # type: ignore[return-value]


def movie_to_dto(movie: Movie) -> MovieDTO:
    """Map a movie entity and its prefetched relations to the public DTO."""
    return MovieDTO(
        title=movie.title,
        slug=movie.slug,
        year=movie.year,
        rating=movie.rating,
        duration_in_minutes=movie.duration_in_minutes,
        short_description=movie.short_description,
        full_description=movie.full_description,
        created_at=movie.created_at,
        updated_at=movie.updated_at,
        release_date=movie.release_date,
        language=LanguageDTO(name=movie.language.name),
        genres=_genres(movie.genres.all()),
        screenplays=_screenplays(movie.screenplays.all()),
        actors=_actors_named(movie.actors.all()),
        studios=_studios(movie.studios.all()),
        directors=_directors(movie.directors.all()),
        countries=_countries(movie.countries.all()),
    )


__all__ = ["movie_to_dto"]

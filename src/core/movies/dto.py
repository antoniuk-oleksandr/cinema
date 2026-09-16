"""Public movie catalog DTOs."""

from dataclasses import dataclass
from datetime import date, datetime

from core.actors.dto import ActorDTO
from core.countries.dto import CountryDTO
from core.directors.dto import DirectorDTO
from core.genres.dto import GenreDTO
from core.languages.dto import LanguageDTO
from core.screenplays.dto import ScreenplayDTO
from core.studios.dto import StudioDTO


@dataclass(frozen=True)
class MovieDTO:
    """Public movie representation without internal status."""

    title: str
    slug: str
    year: int
    rating: str
    duration_in_minutes: int
    short_description: str
    full_description: str
    created_at: datetime
    updated_at: datetime
    release_date: date | None
    language: LanguageDTO
    genres: tuple[GenreDTO, ...]
    screenplays: tuple[ScreenplayDTO, ...]
    actors: tuple[ActorDTO, ...]
    studios: tuple[StudioDTO, ...]
    directors: tuple[DirectorDTO, ...]
    countries: tuple[CountryDTO, ...]

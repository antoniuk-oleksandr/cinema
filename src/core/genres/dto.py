"""Genre DTOs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GenreDTO:
    """Public genre representation."""

    name: str

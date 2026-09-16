"""Country DTOs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CountryDTO:
    """Public country representation."""

    name: str

"""Screenplay DTOs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScreenplayDTO:
    """Public screenplay representation."""

    first_name: str
    surname: str

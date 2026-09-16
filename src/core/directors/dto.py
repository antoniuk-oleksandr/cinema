"""Director DTOs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DirectorDTO:
    """Public director representation."""

    first_name: str
    surname: str

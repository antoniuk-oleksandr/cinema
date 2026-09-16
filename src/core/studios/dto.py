"""Studio DTOs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StudioDTO:
    """Public studio representation."""

    name: str

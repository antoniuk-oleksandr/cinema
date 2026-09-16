"""Language DTOs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageDTO:
    """Public language representation."""

    name: str

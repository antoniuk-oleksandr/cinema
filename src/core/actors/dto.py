"""Actor DTOs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ActorDTO:
    """Public actor representation."""

    first_name: str
    surname: str

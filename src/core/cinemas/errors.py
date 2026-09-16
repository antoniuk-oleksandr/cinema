"""Cinema feature exceptions."""


class CinemaNotFoundError(Exception):
    """Raised when a cinema slug does not exist."""

    def __init__(self) -> None:
        super().__init__("Cinema not found.")


class CinemaUnavailableError(Exception):
    """Raised when the cinema use case cannot provide a cinema."""

    def __init__(self) -> None:
        super().__init__("Cinema is unavailable.")

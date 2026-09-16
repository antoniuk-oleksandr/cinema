"""Domain and application errors for the movie catalog."""


class MovieNotFoundError(Exception):
    """Raised when a movie slug is absent from the catalog."""

    def __init__(self) -> None:
        super().__init__("Movie not found.")


class MovieUnavailableError(Exception):
    """Raised when the movie use case cannot provide the requested movie."""

    def __init__(self) -> None:
        super().__init__("Movie is unavailable.")

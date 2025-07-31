class AbstractException(Exception):
    """Base class for all exceptions in the Versum package."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.message}')"

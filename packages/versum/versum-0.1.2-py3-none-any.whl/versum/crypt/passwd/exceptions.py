from versum.exceptions import AbstractException


class OutdatedPasswordHashException(AbstractException):
    """Exception raised when a password hash is outdated and needs to be updated."""

    def __init__(
        self,
        message: str = "Password hash needs to be updated due to changed parameters.",
    ):
        super().__init__(message)
        self.message = message

class AydieException(Exception):
    """
    Base exception class for the aydie_genai library.

    All custom exceptions raised by this library should inherit from this class.
    This allows users to catch all library-specific errors with a single
    `except AydieException:` block.

    Attributes:
        message (str): The error message associated with the exception.
    """

    def __init__(self, message: str):
        """
        Initializes the AydieException.

        Args:
            message (str): The detailed error message.
        """
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        Returns the string representation of the exception.
        """
        return f"AydieException: {self.message}"
    

class APIKeyNotFoundError(AydieException):
    """
    Raised when a required API key is not found in the environment variables.
    """
    def __init__(self, provider_name: str, key_variable: str):
        message = (
            f"API key for '{provider_name}' not found. "
            f"Please set the '{key_variable}' environment variable."
        )
        super().__init__(message)

class ModelNotSupportedError(AydieException):
    """
    Raised when the specified model name is not supported by the library.
    """
    def __init__(self, model_name: str):
        message = f"The model '{model_name}' is not recognized or supported."
        super().__init__(message)
"""Custom exceptions for the Firestore Gateway."""

class GatewayError(Exception):
    """Base class for gateway-related errors."""
    pass

class DocumentAlreadyExistsError(GatewayError):
    """Raised when trying to create a document that already exists."""
    def __init__(self, path: str):
        super().__init__(f"Document at path '{path}' already exists.")
        self.path = path

class DocumentNotFoundError(GatewayError):
    """Raised when a required document is not found."""
    def __init__(self, path: str):
        super().__init__(f"Document at path '{path}' was not found.")
        self.path = path

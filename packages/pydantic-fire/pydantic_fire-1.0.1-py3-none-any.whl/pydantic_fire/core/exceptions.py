class SchemaError(Exception):
    """Base exception for all errors in the firestore-schema package."""
    pass

class ValidationError(SchemaError):
    """Raised when data fails validation against the schema."""
    pass

class FieldDefinitionError(SchemaError):
    """Raised when a Field is defined incorrectly."""
    pass

class TransactionError(SchemaError):
    """Raised when a transaction operation fails."""
    pass

class TransactionConflictError(TransactionError):
    """Raised specifically when a transaction fails due to a conflict (contention)."""
    pass

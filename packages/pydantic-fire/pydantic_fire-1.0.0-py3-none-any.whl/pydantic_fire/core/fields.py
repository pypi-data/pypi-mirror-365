from __future__ import annotations
from typing import Any, Callable, Optional, Type, Dict, TypeVar
from datetime import datetime
from pydantic import Field as PydanticField

from .exceptions import FieldDefinitionError
from .types import (
    DocumentData, GeoPoint, Timestamp, ArrayUnion, ArrayRemove, 
    DocumentReference, SERVER_TIMESTAMP, DELETE_FIELD, Vector,
    FirestoreFieldType, T
)

__all__ = ["Field", "PydanticField"]

class Field:
    """
    A descriptor that holds the configuration for a Pydantic field,
    to be used within a Document's `Fields` inner class.
    
    Enhanced with metadata support for permissions, UI hints, and aliases.
    """
    def __init__(
        self,
        field_type: Type[FirestoreFieldType],
        required: bool = False,
        default: Any = None,
        default_factory: Optional[Callable[[], Any]] = None,
        auto_now_add: bool = False,
        **kwargs: Any,
    ) -> None:
        self.field_type = field_type
        self.required = required
        self.default = default
        self.default_factory = default_factory
        self.auto_now_add = auto_now_add
        self.kwargs = kwargs
        
        # Validate field configuration
        self._validate_field_config()

        # For auto_now_add, we create a default_factory for Pydantic
        if self.auto_now_add:
            if self.field_type is not datetime:
                raise TypeError("'auto_now_add' is only supported for datetime fields.")
            self.default_factory = datetime.utcnow
        elif self.default_factory is None:
            self.default_factory = None
    
    def _validate_field_config(self) -> None:
        """
        Validate field configuration for consistency.
        """
        # No validation needed for basic field configuration
        pass
    
    @property
    def read_only(self) -> bool:
        """Check if field is read-only."""
        return self.kwargs.get('read_only', False)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert field configuration to dictionary for introspection.
        
        Returns:
            Dictionary representation of field configuration
        """
        # Safely get field type name
        try:
            field_type_name = getattr(self.field_type, '__name__', str(self.field_type))
        except Exception:
            field_type_name = str(self.field_type)
        
        return {
            'field_type': field_type_name,
            'required': self.required,
            'default': self.default,
            'auto_now_add': self.auto_now_add,
            'kwargs': self.kwargs,
        }

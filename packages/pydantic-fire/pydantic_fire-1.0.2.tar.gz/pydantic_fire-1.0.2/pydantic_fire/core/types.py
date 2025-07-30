"""
Firestore type definitions and type aliases.

This module provides comprehensive type hints for all Firestore native types,
to be used for schema definition and validation in CRUD operations.

Supported Firestore Types:
- Basic: str, int, float, bool, bytes
- Complex: Dict (Map), List (Array) 
- Temporal: datetime (Timestamp)
- Geospatial: GeoPoint
- References: DocumentReference
- Special: ArrayUnion, ArrayRemove, SERVER_TIMESTAMP
- Advanced: Vector (for embeddings)
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

# Type variable for generic type hints
T = TypeVar('T')

# Import Firestore types with fallbacks
HAS_FIRESTORE = False

try:
    from google.cloud import firestore
    from google.cloud.firestore_v1.base_document import DocumentSnapshot
    from google.cloud.firestore_v1.document import DocumentReference
    from google.cloud.firestore_v1.types.write import WriteResult
    from google.cloud.firestore_v1.transforms import ArrayUnion, ArrayRemove, SERVER_TIMESTAMP
    
    GeoPoint = firestore.GeoPoint
    HAS_FIRESTORE = True
    
except ImportError:
    # Type stubs when Firestore is not available
    from typing import Any
    
    DocumentSnapshot = Any
    DocumentReference = Any
    WriteResult = Any
    ArrayUnion = Any
    ArrayRemove = Any
    SERVER_TIMESTAMP = Any
    GeoPoint = Any

# Core Firestore type aliases
Timestamp = datetime
DocumentData = Dict[str, Any]
CollectionPath = str
DocumentPath = str

# Comprehensive Firestore field value types (recursive)
FirestoreValue = Union[
    None,                           # Null
    bool,                          # Boolean
    int,                           # Integer
    float,                         # Double/Float
    str,                           # String
    bytes,                         # Bytes
    datetime,                      # Timestamp
    GeoPoint,                      # Geographical point
    DocumentReference,             # Document reference
    List['FirestoreValue'],        # Array (recursive)
    Dict[str, 'FirestoreValue'],   # Map (recursive)
    ArrayUnion,                    # Array union operation
    ArrayRemove,                   # Array remove operation
]

# Vector type for embeddings
Vector = List[float]

# Query and operation types
FilterValue = Union[str, int, float, bool, datetime, GeoPoint, DocumentReference, None]
OrderDirection = Union[str, int]  # 'ASCENDING', 'DESCENDING' or Query constants

# Sentinel values for field operations
class SentinelValue:
    """Base class for Firestore sentinel values."""
    pass

class DeleteField(SentinelValue):
    """Sentinel value to delete a field."""
    def __repr__(self):
        return "DELETE_FIELD"

# Singleton instances
DELETE_FIELD = DeleteField()

# Type unions for field definitions
BasicFirestoreType = Union[str, int, float, bool, bytes, datetime, None]
ComplexFirestoreType = Union[List[Any], Dict[str, Any], GeoPoint, DocumentReference, Vector]
FirestoreFieldType = Union[BasicFirestoreType, ComplexFirestoreType, ArrayUnion, ArrayRemove]

# Export all necessary types
__all__ = [
    'HAS_FIRESTORE',
    'T',
    
    # Firestore native types
    'DocumentSnapshot',
    'DocumentReference', 
    'WriteResult',
    'ArrayUnion',
    'ArrayRemove',
    'SERVER_TIMESTAMP',
    'GeoPoint',
    
    # Type aliases
    'Timestamp',
    'DocumentData',
    'CollectionPath',
    'DocumentPath',
    'FirestoreValue',
    'Vector',
    'FilterValue',
    'OrderDirection',
    
    # Sentinel values
    'SentinelValue',
    'DeleteField',
    'DELETE_FIELD',
    
    # Type unions for field definitions
    'BasicFirestoreType',
    'ComplexFirestoreType', 
    'FirestoreFieldType',
]
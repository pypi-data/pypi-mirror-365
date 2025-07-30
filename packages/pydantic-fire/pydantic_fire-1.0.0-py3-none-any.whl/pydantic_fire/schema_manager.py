from __future__ import annotations
from typing import Dict, Type, TYPE_CHECKING, cast, Any
from .core.exceptions import SchemaError

if TYPE_CHECKING:
    from .core.base import Collection, Document, DocumentType, FirestoreNode
else:
    # Forward references for runtime
    Document = 'Document'
    DocumentType = 'DocumentType'
    FirestoreNode = 'FirestoreNode'

class _FirestoreSchemaManager:
    """
    A singleton class that manages the registration and access
    of the entire Firestore schema.
    """
    def __init__(self):
        self._registry: Dict[str, Type[Collection]] = {}

    def register(self, collection_class: Type[Collection]) -> None:
        """
        Registers a top-level collection class to the global schema.

        Args:
            collection_class: The class (not an instance) of the collection to register.
        """
        collection_name = collection_class.template()
        if not collection_name or '{' in collection_name:
            raise SchemaError(f"Cannot register '{collection_class.__name__}': Top-level collections must have a static path template.")

        self._registry[collection_name] = collection_class

    def collection(self, collection_name: str, **kwargs: str) -> Collection:
        """
        Retrieves an instance of a registered top-level collection.

        Args:
            collection_name: The name (path) of the collection.
            **kwargs: Any dynamic path parameters for the collection (should be none for top-level).

        Returns:
            An instance of the requested Collection class.
        """
        if collection_name not in self._registry:
            raise SchemaError(f"Collection '{collection_name}' is not registered in the schema.")
        
        collection_class = self._registry[collection_name]
        return collection_class(**kwargs)

    def doc(self, collection_name: str, doc_id: str, **kwargs: str) -> 'Document':
        """
        A shortcut to retrieve a document directly from a top-level collection.

        Args:
            collection_name: The name (path) of the collection.
            doc_id: The ID of the document to access.
            **kwargs: Any dynamic path parameters for the document.

        Returns:
            An instance of the document.
        """
        # Get the collection instance
        collection = self.collection(collection_name)
        
        # Get the first document type from the collection
        if not hasattr(collection, '_document_types'):
            raise SchemaError(f"Collection {collection_name} is not properly initialized with document types")
            
        if not collection._document_types:
            if not hasattr(collection, '_default_document_class') or not collection._default_document_class:
                raise SchemaError(f"No document types defined for collection {collection_name}")
            
            # Fallback to default document class if no document types are defined
            doc_type = DocumentType(collection._default_document_class, is_static=False)
        else:
            # Use the first document type
            doc_type = next(iter(collection._document_types.values()))
        
        # Create and return the document instance
        return doc_type.create_instance(collection.instance_path, doc_id, **kwargs)

    def subcollection(self, document_path: str, subcollection_name: str, **kwargs: str) -> 'Collection':
        """
        A shortcut to access a subcollection from a document path.

        Args:
            document_path: The full path to the parent document (e.g., 'users/123')
            subcollection_name: The name of the subcollection to access
            **kwargs: Any additional path parameters for the subcollection

        Returns:
            An instance of the subcollection

        Example:
            # Access a user's posts subcollection
            posts = FirestoreSchema.subcollection('users/123', 'posts')
        """
        # Split the document path into collection and document ID
        parts = document_path.split('/')
        if len(parts) % 2 != 0:
            raise ValueError(f"Invalid document path: {document_path}. Expected format: 'collection/document-id'")
        
        # Get the parent document's collection
        collection_name = parts[-2]
        doc_id = parts[-1]
        
        # Get the parent document to access its subcollections
        parent = self.doc(collection_name, doc_id, **kwargs)
        
        # Get the subcollection from the parent document
        if not hasattr(parent, subcollection_name.upper()):
            raise SchemaError(f"Subcollection '{subcollection_name}' not found on document {document_path}")
        
        subcollection = getattr(parent, subcollection_name.upper())
        return subcollection

# Create a single, global instance of the schema manager.
# All interactions with the schema should go through this instance.
FirestoreSchema = _FirestoreSchemaManager()

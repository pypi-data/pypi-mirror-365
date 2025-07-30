"""
Async base classes for Firestore schema management.

This module provides an async version of the core Document class,
enabling high-performance async/await validation operations with Firestore.
""" 

import asyncio
from datetime import datetime
from typing import Any, Dict, Type, cast

from pydantic import BaseModel

from ..core.base import Collection as SyncCollection, Document as SyncDocument
from ..core.exceptions import SchemaError
from ..core.exceptions import ValidationError as SchemaValidationError
from ..schema_manager import _FirestoreSchemaManager


class AsyncDocument(SyncDocument):
    """
    Async version of Document class with async validation and operations.

    Provides async methods for validation, serialization, and Firestore operations
    while maintaining compatibility with the sync version.
    """

    @classmethod
    async def async_validate_create(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Async validation for document creation.

        Args:
            data: Document data to validate

        Returns:
            Validated document data

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Run validation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()

            def _validate():
                # Validate data and return all fields (not just set ones)
                validated_model = cls.validate(data)
                return validated_model.model_dump()

            return await loop.run_in_executor(None, _validate)
        except Exception as e:
            raise SchemaValidationError(f"Async validation failed: {e}")

    @classmethod
    async def async_validate_partial(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Async validation for partial document updates.

        Args:
            data: Partial document data to validate

        Returns:
            Validated partial document data

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Run partial validation in thread pool
            loop = asyncio.get_event_loop()

            def _validate_partial():
                # validate_partial already returns Dict[str, Any]
                return cls.validate_partial(data)

            return await loop.run_in_executor(None, _validate_partial)
        except Exception as e:
            raise SchemaValidationError(f"Async partial validation failed: {e}")

    @classmethod
    async def async_parse(cls, data: Dict[str, Any]) -> BaseModel:
        """
        Async parsing of document data into Pydantic model.

        Args:
            data: Raw document data from Firestore

        Returns:
            Validated Pydantic model instance

        Raises:
            ValidationError: If parsing fails
        """
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, cls.parse, data)
        except Exception as e:
            raise SchemaValidationError(f"Async parsing failed: {e}")

    @classmethod
    async def async_serialize(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Async serialization of document data for Firestore storage.

        Args:
            data: Document data to serialize

        Returns:
            Serialized data ready for Firestore

        Raises:
            ValidationError: If serialization fails
        """
        try:
            loop = asyncio.get_event_loop()

            def _serialize():
                return cls.serialize(data)

            return await loop.run_in_executor(None, _serialize)
        except Exception as e:
            raise SchemaValidationError(f"Async serialization failed: {e}")


class AsyncCollection(SyncCollection):
    """
    Async version of the Collection class.

    This class is intended for type hinting and to be used with AsyncDocuments.
    It inherits all functionality from the synchronous Collection class.
    """
    pass


class _AsyncFirestoreSchemaManager(_FirestoreSchemaManager):
    """
    A singleton class that manages the registration and access
    of the entire async Firestore schema.
    """

    def register(self, collection_class: Type[AsyncCollection]) -> None:
        """
        Registers a top-level async collection class to the global schema.
        """
        super().register(collection_class)

    def collection(self, collection_name: str, **kwargs: str) -> AsyncCollection:
        """
        Retrieves an instance of a registered top-level async collection.
        """
        coll = super().collection(collection_name, **kwargs)
        return cast(AsyncCollection, coll)

    def doc(self, collection_name: str, doc_id: str, **kwargs: str) -> AsyncDocument:
        """
        A shortcut to retrieve an async document directly from a top-level collection.
        """
        doc = super().doc(collection_name, doc_id, **kwargs)
        return cast(AsyncDocument, doc)


# Create a single, global instance of the async schema manager.
AsyncFirestoreSchema = _AsyncFirestoreSchemaManager()


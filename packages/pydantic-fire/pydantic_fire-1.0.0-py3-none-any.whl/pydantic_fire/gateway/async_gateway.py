from __future__ import annotations
import logging
from typing import Any, Callable, Dict, List, Optional, Type, Union

from pydantic import BaseModel

from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.base_document import DocumentSnapshot

from .base_gateway import _BaseGateway, _BaseQueryBuilder
from ..core.base import T_Document, Collection, Document
from google.cloud.firestore_v1.async_batch import AsyncWriteBatch
from google.cloud.firestore_v1.async_aggregation import AsyncAggregationQuery
from google.cloud.firestore_v1.async_query import AsyncQuery
from google.cloud.firestore_v1.async_collection import AsyncCollectionReference

from ..async_operations.async_base import AsyncDocument

from ..async_operations.async_transactions import (
    AsyncBatchBuilder,
    AsyncTransactionContext,
    create_async_batch_builder,
    get_async_transaction_manager,
)
from ..async_operations.async_decorators import async_transactional
from ..core.exceptions import TransactionError
from .exceptions import DocumentAlreadyExistsError, DocumentNotFoundError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class AsyncQueryBuilder(_BaseQueryBuilder[T_Document, AsyncQuery, AsyncAggregationQuery, AsyncCollectionReference]):
    """A concrete implementation of the fluent query builder for asynchronous operations."""

    def _to_model(self, snapshot) -> T_Document:
        """Converts a Firestore snapshot to a Document instance."""
        if not self._model:
            raise TypeError("Cannot convert to a typed document without a model.")
        assert isinstance(snapshot, DocumentSnapshot), "Snapshot must be a DocumentSnapshot"
        data = snapshot.to_dict()
        return self._model.model_validate(data)

    def _create_aggregation_query(self) -> AsyncAggregationQuery:
        """Creates a new async aggregation query instance."""
        return AsyncAggregationQuery(self._query)

    async def get(self) -> Union[List[T_Document], Dict[str, Union[int, float]]]:
        """Executes the query and returns the results."""
        if self._aggregation_query:
            # The `get()` method on an AsyncAggregationQuery returns a list of lists of AggregationResult.
            # e.g., [[<AggregationResult alias=total, value=3>]]
            results_iterator = self._aggregation_query.stream()
            result_list = [item async for item in results_iterator]

            # If the aggregation yields no results, return a dict with default zero values.
            if not result_list or not result_list[0]:
                return {alias: 0 for alias in self._aliases}

            # Otherwise, return the dictionary of aggregation results.
            return {agg.alias: agg.value for agg in result_list[0]}

        # Standard query execution
        snapshots = await self._query.get()
        if self._model:
            return [self._to_model(snapshot) for snapshot in snapshots if snapshot.exists]

        # If no model, return raw dicts
        return [snapshot.to_dict() for snapshot in snapshots if snapshot.exists]  # type: ignore

    async def get_one(self) -> Optional[T_Document]:
        """Executes the query and returns the first result, or None if not found."""
        query_result = await self._query.limit(1).get()
        if not query_result:
            return None
        return self._to_model(query_result[0])

class AsyncFirestoreGateway(_BaseGateway[T_Document, AsyncClient, AsyncTransactionContext, AsyncWriteBatch, AsyncQueryBuilder]):
    """Provides a schema-aware interface for asynchronous Firestore operations."""

    def __init__(self, client: Optional[AsyncClient] = None):
        super().__init__(client)
        self._transaction_manager = get_async_transaction_manager()
        if self._transaction_manager and self.client:
            self._transaction_manager.set_client(self.client)

    @async_transactional()
    async def get(
        self, doc_path: str, model_class: Type[T_Document], transaction: Optional[AsyncTransactionContext] = None
    ) -> Optional[T_Document]:
        """
        Fetches a single document transactionally and validates it against the schema.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class to validate the data against.
            transaction: The transaction context (injected by @async_transactional).

        Returns:
            A validated Pydantic model instance if the document exists, otherwise None.
        """
        assert transaction is not None, "Transaction context not found."
        doc_ref = self.client.document(doc_path)
        data = await transaction.get(doc_ref)
        if data:
            return model_class.model_validate(data)
        return None

    async def get_direct(self, doc_path: str, model_class: Type[T_Document]) -> Optional[T_Document]:
        """
        Fetches a single document directly, bypassing transactions.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class to validate the data against.

        Returns:
            A validated Pydantic model instance if the document exists, otherwise None.
        """
        doc_ref = self.client.document(doc_path)
        snapshot = await doc_ref.get()
        if not snapshot.exists:
            return None
        data = snapshot.to_dict()
        return model_class.model_validate(data) if data else None

    @async_transactional()
    async def exists(
        self, doc_path: str, model_class: Type[T_Document], transaction: Optional[AsyncTransactionContext] = None
    ) -> bool:
        """
        Checks if a document exists within a transaction.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class (for interface consistency).
            transaction: The transaction context (injected by @async_transactional).

        Returns:
            True if the document exists, False otherwise.
        """
        assert transaction is not None, "Transaction context not found."
        doc_ref = self.client.document(doc_path)
        doc_data = await transaction.get(doc_ref)
        return doc_data is not None

    async def exists_direct(self, doc_path: str) -> bool:
        """
        Checks if a document exists directly, bypassing transactions.

        Args:
            doc_path: The full path to the document.

        Returns:
            True if the document exists, False otherwise.
        """
        snapshot = await self.client.document(doc_path).get()
        return snapshot.exists

    @async_transactional()
    async def create(
        self,
        doc_path: str,
        model_class: Type[T_Document],
        data: Union[Dict[str, Any], BaseModel],
        transaction: Optional[AsyncTransactionContext] = None,
    ) -> T_Document:
        assert transaction is not None, "Transaction context not found."
        if await self.exists(doc_path, model_class, transaction=transaction):
            raise DocumentAlreadyExistsError(doc_path)

        doc_ref = self.client.document(doc_path)
        data_dict = data.model_dump(by_alias=True) if isinstance(data, BaseModel) else data
        assert issubclass(model_class, AsyncDocument), "model_class must be a subclass of AsyncDocument"
        validated_data = await model_class.async_validate_create(data_dict)

        await transaction.create(doc_ref, validated_data)
        return model_class.model_validate(validated_data)

    @async_transactional()
    async def set(
        self,
        doc_path: str,
        model_class: Type[T_Document],
        data: Union[Dict[str, Any], BaseModel],
        merge: bool = False,
        transaction: Optional[AsyncTransactionContext] = None,
    ) -> T_Document:
        assert transaction is not None, "Transaction context not found."
        doc_ref = self.client.document(doc_path)
        data_dict = data.model_dump(by_alias=True) if isinstance(data, BaseModel) else data

        final_data = data_dict
        if merge:
            existing_model = await self.get(doc_path, model_class, transaction=transaction)
            if existing_model:
                existing_data = existing_model.model_dump(by_alias=True)
                assert issubclass(model_class, AsyncDocument), "model_class must be a subclass of AsyncDocument"
                validated_partial_data = await model_class.async_validate_partial(data_dict)
                final_data = {**existing_data, **validated_partial_data}

        assert issubclass(model_class, AsyncDocument), "model_class must be a subclass of AsyncDocument"
        validated_data = await model_class.async_validate_create(final_data)

        await transaction.set(doc_ref, validated_data, merge=False)  # Always overwrite
        return model_class.model_validate(validated_data)

    @async_transactional()
    async def update(
        self,
        doc_path: str,
        model_class: Type[T_Document],
        data: Dict[str, Any],
        transaction: Optional[AsyncTransactionContext] = None,
    ) -> T_Document:
        assert transaction is not None, "Transaction context not found."
        existing_model = await self.get(doc_path, model_class, transaction=transaction)
        if not existing_model:
            raise DocumentNotFoundError(doc_path)

        assert issubclass(model_class, AsyncDocument), "model_class must be a subclass of AsyncDocument"
        validated_updates = await model_class.async_validate_partial(data)

        doc_ref = self.client.document(doc_path)
        await transaction.update(doc_ref, validated_updates)

        existing_data = existing_model.model_dump(by_alias=True)
        merged_data = {**existing_data, **validated_updates}
        return model_class.model_validate(merged_data)

    @async_transactional()
    async def delete(self, doc_path: str, model_class: Type[T_Document], transaction: Optional[AsyncTransactionContext] = None) -> None:
        assert transaction is not None, "Transaction context not found."
        if not await self.exists(doc_path, model_class, transaction=transaction):
            raise DocumentNotFoundError(doc_path)

        doc_ref = self.client.document(doc_path)
        await transaction.delete(doc_ref)

    def query(self, coll_schema: Collection) -> AsyncQueryBuilder:
        coll_ref = self.client.collection(coll_schema.instance_path)
        return AsyncQueryBuilder(coll_ref, model=coll_schema.model)

    async def run_in_transaction(self, callable_func: Callable[..., Any], *args, **kwargs) -> Any:
        if not self._transaction_manager:
            raise TransactionError("AsyncTransactionManager not initialized.")
        async with self._transaction_manager.transaction_context() as transaction_context:
            return await callable_func(transaction_context, *args, **kwargs)

    async def get_all(self, coll_schema: Collection) -> List[T_Document]:
        if not coll_schema.model:
            raise TypeError("A model must be provided in the collection schema to use get_all.")
        coll_ref = self.client.collection(coll_schema.instance_path)
        docs = await coll_ref.get()
        return [coll_schema.model.model_validate(doc.to_dict()) for doc in docs if doc.exists]

    def batch(self) -> AsyncBatchBuilder:
        """
        Creates a new batch builder using the global transaction manager.

        Note: This returns an AsyncBatchBuilder, which is not a direct subclass of
        the base gateway's WriteBatch_T (AsyncWriteBatch). This is a deliberate
        design choice to centralize batch logic in the transaction manager.
        The type is ignored to satisfy the linter while maintaining a consistent
        internal architecture.
        """
        return create_async_batch_builder()

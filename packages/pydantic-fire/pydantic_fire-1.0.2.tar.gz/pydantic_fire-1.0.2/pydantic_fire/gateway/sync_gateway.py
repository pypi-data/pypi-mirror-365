"""
Implementation of the synchronous FirestoreGateway.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, Optional, Type, Union, List, Callable

from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.query import Query
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.aggregation import AggregationQuery
from google.cloud.firestore_v1.transaction import Transaction
from google.cloud.firestore_v1.batch import WriteBatch
from pydantic import BaseModel

from ..core.base import Document, Collection, T_Document
from ..sync_operations.transactions import (
    get_transaction_manager,
    TransactionContext,
    create_batch_builder,
)
from ..sync_operations.decorators import transactional
from .exceptions import DocumentAlreadyExistsError, DocumentNotFoundError
from .base_gateway import _BaseGateway, _BaseQueryBuilder, _BaseBatchWriter


class QueryBuilder(_BaseQueryBuilder[T_Document, Query, AggregationQuery, CollectionReference]):
    """A concrete implementation of the fluent query builder for synchronous operations."""

    def count(self, alias: str) -> "QueryBuilder[T_Document]":
        """Adds a count aggregation to the query."""
        if not self._aggregation_query:
            self._aggregation_query = self._create_aggregation_query()
        self._aggregation_query.count(alias=alias)
        self._aliases.append(alias)
        return self

    def sum(self, field_path: str, alias: str) -> "QueryBuilder[T_Document]":
        """Adds a sum aggregation to the query."""
        if not self._aggregation_query:
            self._aggregation_query = self._create_aggregation_query()
        self._aggregation_query.sum(field_path, alias=alias)
        self._aliases.append(alias)
        return self

    def avg(self, field_path: str, alias: str) -> "QueryBuilder[T_Document]":
        """Adds an average aggregation to the query."""
        if not self._aggregation_query:
            self._aggregation_query = self._create_aggregation_query()
        self._aggregation_query.avg(field_path, alias=alias)
        self._aliases.append(alias)
        return self

    def _to_model(self, snapshot) -> T_Document:
        """Converts a Firestore snapshot to a Pydantic model instance."""
        if not self._model:
            raise TypeError("Cannot convert to a typed document without a model.")
        return self._model.model_validate(snapshot.to_dict())

    def _create_aggregation_query(self) -> AggregationQuery:
        """Creates a new sync aggregation query instance."""
        return AggregationQuery(self._query)

    def get(self) -> Union[List[T_Document], Dict[str, Union[int, float]]]:
        """
        Executes the query and returns the results.

        If an aggregation is performed, returns a dictionary with the results.
        If the aggregation yields no results, returns a dictionary with default
        zero values for each alias.
        Otherwise, returns a list of document model instances.
        """
        if self._aggregation_query:
            logging.info("Executing aggregation query.")
            results_iterator = self._aggregation_query.stream()
            result_list = next(results_iterator, [])
            if not result_list:
                return {alias: 0 for alias in self._aliases}
            return {agg.alias: agg.value for agg in result_list}

        logging.info("Executing standard query stream.")
        snapshots = self._query.stream()
        if self._model:
            return [self._model.model_validate(snapshot.to_dict()) for snapshot in snapshots if snapshot.exists]
        # If no model, return raw dicts
        return [snapshot.to_dict() for snapshot in snapshots if snapshot.exists]  # type: ignore

    def get_one(self) -> Optional[T_Document]:
        """Executes the query and returns the first result or None."""
        if not self._model:
            raise TypeError("Cannot get a typed document without a model. Use get() for raw data.")
        snapshots = self._query.limit(1).stream()
        for snapshot in snapshots:
            if snapshot.exists:
                return self._model.model_validate(snapshot.to_dict())
        return None


class FirestoreGateway(_BaseGateway[T_Document, Client, Transaction, WriteBatch, "QueryBuilder"]):
    """A centralized, schema-aware gateway for all synchronous Firestore operations."""

    def __init__(self, client: Client):
        """
        Initializes the FirestoreGateway.

        Args:
            client: An initialized `google.cloud.firestore_v1.client.Client` instance.
        """
        super().__init__(client)
        # Set the client for the global transaction manager
        get_transaction_manager().set_client(self.client)

    def _ensure_client(self) -> None:
        """Ensures the client is set, raising an error if not."""
        if self._client is None:
            raise ValueError(
                "Firestore client has not been set. "
                "Please initialize the gateway with a client or set it using 'set_client'."
            )

    @transactional()
    def get(self, doc_path: str, model_class: Type[T_Document], transaction: Optional[TransactionContext] = None) -> Optional[T_Document]:
        """
        Fetches a single document transactionally and validates it against the schema.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class to validate the data against.
            transaction: The transaction context (injected by @transactional).

        Returns:
            A validated Pydantic model instance if the document exists, otherwise None.
        """
        assert transaction is not None, "Transaction context not found."
        self._ensure_client()
        doc_ref = self.client.document(doc_path)

        snapshot = transaction.get(doc_ref)

        if not snapshot.exists:
            return None

        data = snapshot.to_dict()
        return model_class.model_validate(data) if data else None

    def get_direct(self, doc_path: str, model_class: Type[T_Document]) -> Optional[T_Document]:
        """
        Fetches a single document directly, bypassing transactions.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class to validate the data against.

        Returns:
            A validated Pydantic model instance if the document exists, otherwise None.
        """
        self._ensure_client()
        doc_ref = self.client.document(doc_path)
        snapshot = doc_ref.get()

        if not snapshot.exists:
            return None

        data = snapshot.to_dict()
        return model_class.model_validate(data) if data else None

    @transactional()
    def exists(self, doc_path: str, model_class: Type[T_Document], transaction: Optional[TransactionContext] = None) -> bool:
        """
        Checks if a document exists within a transaction.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class (for interface consistency).
            transaction: The transaction context (injected by @transactional).

        Returns:
            True if the document exists, False otherwise.
        """
        assert transaction is not None, "Transaction context not found."
        self._ensure_client()
        doc_ref = self.client.document(doc_path)
        snapshot = transaction.get(doc_ref)
        return snapshot.exists

    def exists_direct(self, doc_path: str) -> bool:
        """
        Checks if a document exists directly, bypassing transactions.

        Args:
            doc_path: The full path to the document.

        Returns:
            True if the document exists, False otherwise.
        """
        self._ensure_client()
        doc_ref = self.client.document(doc_path)
        snapshot = doc_ref.get()
        return snapshot.exists

    @transactional()
    def create(self, doc_path: str, model_class: Type[T_Document], data: Union[Dict[str, Any], BaseModel], transaction: Optional[TransactionContext] = None) -> T_Document:
        """
        Creates a new document in a transaction. Fails if the document already exists.

        Args:
            doc_schema: The document schema instance defining the target path.
            data: The data for the new document (dict or pydantic model).
            transaction: The transaction context (injected by @transactional).

        Returns:
            The validated Pydantic model instance of the created document.

        Raises:
            DocumentAlreadyExistsError: If a document at the path already exists.
        """
        assert transaction is not None, "Transaction context not found."
        self._ensure_client()

        if self.exists(doc_path, model_class):
            raise DocumentAlreadyExistsError(doc_path)

        doc_ref = self.client.document(doc_path)
        data_dict = data.model_dump() if isinstance(data, BaseModel) else data
        validated_model = model_class.validate(data_dict)
        transaction.set(doc_ref, validated_model.model_dump(by_alias=True))
        return validated_model

    @transactional()
    def set(self, doc_path: str, model_class: Type[T_Document], data: Union[Dict[str, Any], BaseModel], merge: bool = False, transaction: Optional[TransactionContext] = None) -> T_Document:
        """
        Creates or overwrites a document in a transaction.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class to validate the data against.
            data: The data for the document (dict or pydantic model).
            merge: If True, merges the data with an existing document. If False, overwrites.
            transaction: The transaction context (injected by @transactional).

        Returns:
            The validated Pydantic model instance of the set document.
        """
        assert transaction is not None, "Transaction context not found."
        self._ensure_client()
        doc_ref = self.client.document(doc_path)
        data_dict = data.model_dump(by_alias=True) if isinstance(data, BaseModel) else data

        final_data = data_dict
        if merge:
            existing_model = self.get(doc_path, model_class)
            if existing_model:
                existing_data = existing_model.model_dump(by_alias=True)
                # Partially validate the new data before merging
                assert issubclass(model_class, Document), "model_class must be a subclass of Document to use validate_partial"
                validated_partial_data = model_class.validate_partial(data_dict)
                # Merge new data into existing data
                final_data = {**existing_data, **validated_partial_data}

        # Validate the final, complete data object
        validated_model = model_class.validate(final_data)

        # Always overwrite with the final model. If merging, the merge has already been handled manually.
        transaction.set(doc_ref, validated_model.model_dump(by_alias=True), merge=False)

        return validated_model

    @transactional()
    def update(self, doc_path: str, model_class: Type[T_Document], data: Dict[str, Any], transaction: Optional[TransactionContext] = None) -> T_Document:
        """
        Updates an existing document in a transaction. Fails if the document does not exist.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class for validation.
            data: The fields to update.
            transaction: The transaction context (injected by @transactional).

        Returns:
            The validated Pydantic model instance of the updated document.

        Raises:
            DocumentNotFoundError: If the document does not exist.
        """
        assert transaction is not None, "Transaction context not found."
        self._ensure_client()

        # Get the existing document transactionally
        existing_model = self.get(doc_path, model_class)
        if not existing_model:
            raise DocumentNotFoundError(doc_path)

        # Validate the partial updates
        assert issubclass(model_class, Document), "model_class must be a subclass of Document to use validate_partial"
        validated_updates = model_class.validate_partial(data)

        # Perform the update within the transaction
        doc_ref = self.client.document(doc_path)
        transaction.update(doc_ref, validated_updates)

        # To return the full, updated document, merge the updates and re-validate
        existing_data = existing_model.model_dump(by_alias=True)
        merged_data = {**existing_data, **validated_updates}
        return model_class.validate(merged_data)

    @transactional()
    def delete(self, doc_path: str, model_class: Type[T_Document], transaction: Optional[TransactionContext] = None) -> None:
        """
        Deletes a document in a transaction.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class (for interface consistency).
            transaction: The transaction context (injected by @transactional).

        Raises:
            DocumentNotFoundError: If the document to be deleted does not exist.
        """
        assert transaction is not None, "Transaction context not found."
        self._ensure_client()
        doc_ref = self.client.document(doc_path)
        snapshot = transaction.get(doc_ref)

        if not snapshot.exists:
            raise DocumentNotFoundError(doc_path)

        transaction.delete(doc_ref)

    def query(self, collection_path: str, model_class: Optional[Type[T_Document]] = None) -> "QueryBuilder[T_Document]":
        """
        Starts a query against a collection.

        Args:
            collection_path: The path to the collection.
            model_class: The Pydantic model class for the documents.

        Returns:
            A QueryBuilder instance to chain query conditions.
        """
        coll_ref = self.client.collection(collection_path)
        return QueryBuilder(coll_ref, model=model_class)

    def run_in_transaction(self, callable_func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Runs a callable function within a single Firestore transaction.

        The callable will receive a transactional gateway instance as its first argument,
        followed by any additional *args and **kwargs.

        Args:
            callable_func: The function to execute transactionally.
            *args: Positional arguments to pass to the callable.
            **kwargs: Keyword arguments to pass to the callable.

        Returns:
            The result of the callable function.
        """
        transaction_manager = get_transaction_manager()

        def transaction_wrapper(transaction: TransactionContext):
            # This function will be executed within a transaction by the manager.
            # It receives the transaction context, which we can then use to ensure
            # all operations by the user's callable are part of this single transaction.

            # The user's callable expects a gateway instance.
            # We pass `self` here because its methods (`create`, `set`, etc.) are already
            # decorated with `@transactional`, which will automatically pick up
            # the active transaction context provided by the transaction manager.
            return callable_func(self, *args, **kwargs)

        return transaction_manager.run(transaction_wrapper)

    def get_all(self, coll_schema: Collection) -> List[T_Document]:
        """
        Fetches all documents from a collection and validates them.

        Args:
            coll_schema: The collection schema instance defining the target path.

        Returns:
            A list of validated Pydantic model instances.
        """
        if not coll_schema.model:
            raise TypeError("A model must be provided in the collection schema to use get_all.")
        coll_ref = self.client.collection(coll_schema.instance_path)
        docs = coll_ref.stream()
        return [coll_schema.model.model_validate(doc.to_dict()) for doc in docs if doc.exists]

    def batch(self) -> 'BatchWriter':
        """
        Creates a new batch writer for performing multiple write operations atomically.
            A BatchWriter instance.
        """
        self._ensure_client()
        return BatchWriter(client=self.client)


class BatchWriter(_BaseBatchWriter[Client, WriteBatch]):
    """A schema-aware writer for Firestore batch operations."""

    def __init__(self, client: Client):
        super().__init__(client)
        self._builder = create_batch_builder()
        self._transaction_manager = get_transaction_manager()

    def create(self, doc_path: str, model_class: Type[Document], data: Union[Dict[str, Any], BaseModel]):
        """
        Adds a 'create' operation to the batch. The document must not exist.
        Note: Firestore batches do not enforce existence checks atomically. This check
        is not performed.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class for validation.
            data: The data for the new document (dict or pydantic model).
        """
        doc_ref = self._client.document(doc_path)
        data_dict = data.model_dump(by_alias=True) if isinstance(data, BaseModel) else data
        validated_model = model_class.validate(data_dict)
        self._builder.set(doc_ref, validated_model.model_dump(by_alias=True))

    def set(self, doc_path: str, model_class: Type[Document], data: Union[Dict[str, Any], BaseModel], merge: bool = False):
        """
        Adds a 'set' operation (create or overwrite) to the batch.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class for validation.
            data: The data for the document (dict or pydantic model).
            merge: If True, merges the data with an existing document.
        """
        doc_ref = self._client.document(doc_path)
        data_dict = data.model_dump(by_alias=True) if isinstance(data, BaseModel) else data
        validated_model = model_class.validate(data_dict)
        self._builder.set(doc_ref, validated_model.model_dump(by_alias=True), merge=merge)

    def update(self, doc_path: str, model_class: Type[Document], data: Dict[str, Any]):
        """
        Adds an 'update' operation to the batch. The document must exist.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class for validation.
            data: The fields to update.
        """
        assert issubclass(model_class, Document), "model_class must be a subclass of Document"
        doc_ref = self._client.document(doc_path)
        validated_updates = model_class.validate_partial(data)
        self._builder.update(doc_ref, validated_updates)

    def delete(self, doc_path: str, model_class: Type[Document]):
        """
        Adds a 'delete' operation to the batch.

        Args:
            doc_path: The full path to the document.
            model_class: The Pydantic model class (for interface consistency).
        """
        doc_ref = self._client.document(doc_path)
        self._builder.delete(doc_ref)

    def commit(self):
        """Commits all the operations in the batch."""
        return self._builder.execute(self._transaction_manager)

    def __enter__(self) -> "BatchWriter":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()

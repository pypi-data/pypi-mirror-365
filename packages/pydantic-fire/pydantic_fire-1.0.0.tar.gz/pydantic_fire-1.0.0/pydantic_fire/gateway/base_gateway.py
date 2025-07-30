from __future__ import annotations

import abc
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

from google.cloud.firestore_v1.aggregation import AggregationQuery
from google.cloud.firestore_v1.base_batch import BaseWriteBatch as WriteBatch
from google.cloud.firestore_v1.base_client import BaseClient as Client
from google.cloud.firestore_v1.base_collection import (
    BaseCollectionReference as CollectionReference,
)
from google.cloud.firestore_v1.base_query import BaseQuery as Query
from google.cloud.firestore_v1.base_transaction import BaseTransaction as Transaction
from pydantic import BaseModel

from ..core.base import Collection, Document, T_Document

# Generic type variables for concrete implementations
Client_T = TypeVar("Client_T", bound=Client)
Query_T = TypeVar("Query_T")  # Was bound to sync Query
AggregationQuery_T = TypeVar("AggregationQuery_T")  # Was bound to sync AggregationQuery
CollectionReference_T = TypeVar("CollectionReference_T")  # Was bound to sync CollectionReference
Transaction_T = TypeVar("Transaction_T", bound=Transaction)
WriteBatch_T = TypeVar("WriteBatch_T", bound=WriteBatch)
Builder = TypeVar("Builder", bound="_BaseQueryBuilder")


class _BaseQueryBuilder(
    Generic[T_Document, Query_T, AggregationQuery_T, CollectionReference_T],
    abc.ABC,
):
    """
    An abstract, schema-aware, fluent builder for Firestore queries.
    """

    def __init__(
        self,
        query: Union[CollectionReference_T, Query_T],
        model: Optional[Type[T_Document]] = None,
    ):
        self._query: Union[CollectionReference_T, Query_T] = query
        self._aggregation_query: Optional[AggregationQuery_T] = None
        self._aliases: List[str] = []
        self._model = model

    @abc.abstractmethod
    def _create_aggregation_query(self) -> AggregationQuery_T:
        """Creates a new aggregation query instance for the specific client (sync/async)."""
        raise NotImplementedError

    def where(self: Builder, *args, **kwargs) -> Builder:
        """Adds a where clause to the query."""
        self._query = self._query.where(*args, **kwargs)  # type: ignore
        return self  # type: ignore

    def order_by(self: Builder, *args, **kwargs) -> Builder:
        """Adds an order_by clause to the query."""
        self._query = self._query.order_by(*args, **kwargs)  # type: ignore
        return self  # type: ignore

    def limit(self: Builder, limit: int) -> Builder:
        """Adds a limit to the query."""
        self._query = self._query.limit(limit)  # type: ignore
        return self  # type: ignore

    def start_at(self: Builder, doc_or_fields) -> Builder:
        """Adds a start_at cursor to the query."""
        self._query = self._query.start_at(doc_or_fields)  # type: ignore
        return self  # type: ignore

    def start_after(self: Builder, doc_or_fields) -> Builder:
        """Adds a start_after cursor to the query."""
        self._query = self._query.start_after(doc_or_fields)  # type: ignore
        return self  # type: ignore

    def end_before(self: Builder, doc_or_fields) -> Builder:
        """Adds an end_before cursor to the query."""
        self._query = self._query.end_before(doc_or_fields)  # type: ignore
        return self  # type: ignore

    def end_at(self: Builder, doc_or_fields) -> Builder:
        """Adds an end_at cursor to the query."""
        self._query = self._query.end_at(doc_or_fields)  # type: ignore
        return self  # type: ignore

    def count(self: Builder, alias: str) -> Builder:
        """Adds a count aggregation to the query."""
        self._aliases.append(alias)
        if self._aggregation_query is None:
            self._aggregation_query = self._create_aggregation_query()
        self._aggregation_query.count(alias=alias)  # type: ignore
        return self  # type: ignore

    def sum(self: Builder, field: str, alias: str) -> Builder:
        """Adds a sum aggregation to the query."""
        self._aliases.append(alias)
        if self._aggregation_query is None:
            self._aggregation_query = self._create_aggregation_query()
        self._aggregation_query.sum(field, alias=alias)  # type: ignore
        return self  # type: ignore

    def avg(self: Builder, field: str, alias: str) -> Builder:
        """Adds an average aggregation to the query."""
        self._aliases.append(alias)
        if self._aggregation_query is None:
            self._aggregation_query = self._create_aggregation_query()
        self._aggregation_query.avg(field, alias=alias)  # type: ignore
        return self  # type: ignore

    @abc.abstractmethod
    def _to_model(self, snapshot) -> T_Document:
        """Converts a Firestore snapshot to a Pydantic model instance."""
        raise NotImplementedError

    @abc.abstractmethod
    def get(self) -> Union[List[T_Document], Dict[str, Union[int, float]]]:
        """Executes the query and returns the results."""
        raise NotImplementedError


class _BaseGateway(
    Generic[T_Document, Client_T, Transaction_T, WriteBatch_T, Builder], abc.ABC
):
    """
    An abstract, centralized, schema-aware gateway for all Firestore operations.
    """

    def __init__(self, client: Optional[Client_T] = None):
        self._client = client

    def _ensure_client(self) -> None:
        """Ensures the client is set, raising an error if not."""
        if self._client is None:
            raise ValueError(
                "Firestore client has not been set. "
                "Please initialize the gateway with a client or set it using 'set_client'."
            )

    @property
    def client(self) -> Client_T:
        """Returns the underlying Firestore client."""
        self._ensure_client()
        return self._client  # type: ignore

    @abc.abstractmethod
    def get(
        self, doc_path: str, model_class: Type[T_Document], transaction: Optional[Transaction_T] = None
    ) -> Optional[T_Document]:
        """Fetches a single document."""
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, doc_path: str, model_class: Type[T_Document]) -> bool:
        """Checks if a document exists."""
        raise NotImplementedError

    @abc.abstractmethod
    def create(
        self,
        doc_path: str,
        model_class: Type[T_Document],
        data: Union[Dict[str, Any], BaseModel],
        transaction: Optional[Transaction_T] = None,
    ) -> T_Document:
        """Creates a new document."""
        raise NotImplementedError

    @abc.abstractmethod
    def set(
        self,
        doc_path: str,
        model_class: Type[T_Document],
        data: Union[Dict[str, Any], BaseModel],
        merge: bool = False,
        transaction: Optional[Transaction_T] = None,
    ) -> T_Document:
        """Creates or overwrites a document."""
        raise NotImplementedError

    @abc.abstractmethod
    def update(
        self,
        doc_path: str,
        model_class: Type[T_Document],
        data: Dict[str, Any],
        transaction: Optional[Transaction_T] = None,
    ) -> T_Document:
        """Updates an existing document."""
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, doc_path: str, model_class: Type[T_Document], transaction: Optional[Transaction_T] = None) -> None:
        """Deletes a document."""
        raise NotImplementedError

    @abc.abstractmethod
    def query(self, coll_schema: Collection) -> Builder:
        """Starts a query against a collection."""
        raise NotImplementedError

    @abc.abstractmethod
    def run_in_transaction(
        self, callable_func: Callable[..., Any], *args, **kwargs
    ) -> Any:
        """Runs a callable function within a single Firestore transaction."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_all(self, coll_schema: Collection) -> List[T_Document]:
        """Fetches all documents from a collection."""
        raise NotImplementedError

    @abc.abstractmethod
    def batch(self) -> WriteBatch_T:
        """Creates a new batch writer."""
        raise NotImplementedError


class _BaseBatchWriter(Generic[Client_T, WriteBatch_T], abc.ABC):
    """An abstract, schema-aware writer for Firestore batch operations."""

    def __init__(self, client: Client_T, batch: Optional[WriteBatch_T] = None):
        self._client = client
        self._batch = batch or client.batch()  # type: ignore

    @abc.abstractmethod
    def create(self, doc_path: str, model_class: Type[Document], data: Union[Dict[str, Any], BaseModel]):
        """Adds a create operation to the batch."""
        raise NotImplementedError

    @abc.abstractmethod
    def set(
        self, doc_path: str, model_class: Type[Document], data: Union[Dict[str, Any], BaseModel], merge: bool = False
    ):
        """Adds a set operation to the batch."""
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, doc_path: str, model_class: Type[Document], data: Dict[str, Any]):
        """Adds an update operation to the batch."""
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, doc_path: str, model_class: Type[Document]):
        """Adds a delete operation to the batch."""
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self) -> list:
        """Commits the batch."""
        raise NotImplementedError

    def __enter__(self) -> _BaseBatchWriter:
        return self

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

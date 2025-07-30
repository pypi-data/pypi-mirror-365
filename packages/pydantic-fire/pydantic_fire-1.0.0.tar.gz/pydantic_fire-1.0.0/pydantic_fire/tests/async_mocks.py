"""
Async mock implementations for Firestore operations.

This module provides async mock implementations of Firestore client, collections,
documents, and queries for comprehensive unit testing without requiring a real
Firestore instance or emulator.
"""

import asyncio
import copy
import uuid
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
from datetime import datetime, timezone
from collections import defaultdict

from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.async_query import AsyncQuery
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.async_collection import AsyncCollectionReference
from google.cloud.firestore_v1.async_document import AsyncDocumentReference
from google.api_core.exceptions import Conflict


class AsyncMockDocumentSnapshot(DocumentSnapshot):
    """Async mock implementation of Firestore DocumentSnapshot."""

    def __init__(self, reference: 'AsyncMockDocumentReference', data: Optional[Dict[str, Any]] = None, exists: bool = True):
        now = datetime.now(timezone.utc)
        super().__init__(
            reference=reference,
            data=data or {},
            exists=exists,
            read_time=now,
            create_time=now,
            update_time=now,
        )

    @property
    def exists(self) -> bool:
        return self._exists

    def to_dict(self) -> Optional[Dict[str, Any]]:
        if self._exists:
            return copy.deepcopy(self._data)
        return None

    def get(self, field_path: str) -> Any:
        if not self._exists:
            return None
        keys = field_path.split('.')
        value = self._data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value


class AsyncMockDocumentReference(AsyncDocumentReference):
    """Async mock implementation of Firestore DocumentReference."""
    _collection_class = 'AsyncMockCollectionReference'

    def __init__(self, *path, client: 'AsyncMockFirestoreClient'):
        super().__init__(*path, client=client)
        # This assignment is for our mock's internal use, shadowing the base property.
        self._mock_client = client

    async def get(self) -> 'AsyncMockDocumentSnapshot':
        """Get document snapshot."""
        await asyncio.sleep(0.001)
        collection_data = self._mock_client._data.get(self.parent.id, {})
        doc_data = collection_data.get(self.id)
        exists = doc_data is not None
        return AsyncMockDocumentSnapshot(self, data=doc_data, exists=exists)

    async def set(self, document_data: Dict[str, Any], merge: bool = False) -> None:
        """Set document data."""
        await asyncio.sleep(0.001)
        if self.parent.id not in self._mock_client._data:
            self._mock_client._data[self.parent.id] = {}
        
        if merge and self.id in self._mock_client._data[self.parent.id]:
            existing_data = self._mock_client._data[self.parent.id][self.id]
            merged_data = {**existing_data, **document_data}
            self._mock_client._data[self.parent.id][self.id] = merged_data
        else:
            self._mock_client._data[self.parent.id][self.id] = copy.deepcopy(document_data)

    async def update(self, field_updates: Dict[str, Any]) -> None:
        """Update document fields."""
        await asyncio.sleep(0.001)
        if self.parent.id not in self._mock_client._data:
            self._mock_client._data[self.parent.id] = {}
        
        if self.id not in self._mock_client._data[self.parent.id]:
            self._mock_client._data[self.parent.id][self.id] = copy.deepcopy(field_updates)
        else:
            existing_data = self._mock_client._data[self.parent.id][self.id]
            for field_path, value in field_updates.items():
                keys = field_path.split('.')
                current = existing_data
                for key in keys[:-1]:
                    current = current.setdefault(key, {})
                current[keys[-1]] = value

    async def delete(self) -> None:
        """Delete document."""
        await asyncio.sleep(0.001)
        if self.parent.id in self._mock_client._data and self.id in self._mock_client._data[self.parent.id]:
            del self._mock_client._data[self.parent.id][self.id]

    def collection(self, collection_id: str) -> 'AsyncMockCollectionReference':
        """Get subcollection reference."""
        return AsyncMockCollectionReference(*self._path, collection_id, client=self._mock_client)


class AsyncMockQuery(AsyncQuery):
    """Async mock implementation of Firestore Query."""
    _parent: Union["AsyncMockCollectionReference", "AsyncMockQuery"]

    def __init__(self, parent: Union['AsyncMockCollectionReference', 'AsyncMockQuery'], 
                 filters=None, orders=None, limit=None, offset=0):
        self._parent = parent
        self._mock_client = parent._mock_client
        self._filters = filters or []
        self._orders = orders or []
        self._limit = limit
        self._offset = offset

    @property
    def _collection_ref(self) -> "AsyncMockCollectionReference":
        parent = self._parent
        while isinstance(parent, AsyncMockQuery):
            parent = parent._parent
        return parent

    @property
    def id(self):
        """The ID of the collection being queried."""
        return self._parent.id

    def document(self, document_id: str) -> 'AsyncMockDocumentReference':
        """Delegates document creation to the parent."""
        return self._parent.document(document_id)

    def _clone(self, **kwargs) -> 'AsyncMockQuery':
        """Create a new query with updated properties."""
        current_kwargs = {
            "_filters": self._filters,
            "_orders": self._orders,
            "limit": self._limit,
            "offset": self._offset,
        }
        current_kwargs.update(kwargs)
        return self.__class__(self._parent, **current_kwargs)

    def where(self, field_path: str, op_string: str, value: Any) -> 'AsyncMockQuery':
        """Adds a filter to the query."""
        new_filters = self._filters + [(field_path, op_string, value)]
        return AsyncMockQuery(self, filters=new_filters, orders=self._orders, limit=self._limit, offset=self._offset)

    def order_by(self, field_path: str, direction: str = 'ASCENDING') -> 'AsyncMockQuery':
        """Adds an ordering to the query."""
        new_orders = self._orders + [(field_path, direction)]
        return AsyncMockQuery(self, filters=self._filters, orders=new_orders, limit=self._limit, offset=self._offset)

    def limit(self, limit_to: int) -> 'AsyncMockQuery':
        """Adds a limit to the query."""
        return AsyncMockQuery(self, filters=self._filters, orders=self._orders, limit=limit_to, offset=self._offset)

    def offset(self, offset: int) -> 'AsyncMockQuery':
        """Adds an offset to the query."""
        return AsyncMockQuery(self, filters=self._filters, orders=self._orders, limit=self._limit, offset=offset)

    def _get_field_value(self, doc_data: Dict[str, Any], field_path: str) -> Any:
        keys = field_path.split('.')
        value = doc_data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    def _evaluate_filter(self, doc_value: Any, op_string: str, filter_value: Any) -> bool:
        op_map = {
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '<': lambda a, b: a is not None and b is not None and a < b,
            '<=': lambda a, b: a is not None and b is not None and a <= b,
            '>': lambda a, b: a is not None and b is not None and a > b,
            '>=': lambda a, b: a is not None and b is not None and a >= b,
            'in': lambda a, b: a in b,
            'not-in': lambda a, b: a not in b,
            'array-contains': lambda a, b: isinstance(a, list) and b in a,
            'array-contains-any': lambda a, b: isinstance(a, list) and any(v in a for v in b)
        }
        return op_map.get(op_string, lambda a, b: True)(doc_value, filter_value)

    def _apply_filters(self, documents: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        if not self._filters:
            return documents
        filtered_docs = {}
        for doc_id, doc_data in documents.items():
            if all(self._evaluate_filter(self._get_field_value(doc_data, fp), op, v) for fp, op, v in self._filters):
                filtered_docs[doc_id] = doc_data
        return filtered_docs

    def _apply_ordering(self, documents: List[tuple]) -> List[tuple]:
        if not self._orders:
            return documents
        # Simplified multi-field sort
        for field, direction in reversed(self._orders):
            documents.sort(
                key=lambda doc: self._get_field_value(doc[1], field),
                reverse=direction.upper() == 'DESCENDING'
            )
        return documents

    async def get(self) -> List['AsyncMockDocumentSnapshot']:
        """Executes the query and returns a list of document snapshots."""
        results = []
        async for snapshot in self.stream():
            results.append(snapshot)
        return results

    async def stream(self) -> AsyncGenerator['AsyncMockDocumentSnapshot', None]:
        """Executes the query and returns an async generator of document snapshots."""
        await asyncio.sleep(0.001)
        
        # Get collection ID from the parent
        collection_id = None
        if hasattr(self._parent, 'id'):
            collection_id = str(self._parent.id)
            # Remove leading slash if present
            if collection_id.startswith('/'):
                collection_id = collection_id[1:]
        else:
            # For AsyncMockCollectionReference, use the last part of the path
            collection_id = str(self._parent).split('/')[-1]
            # Remove leading slash if present
            if collection_id.startswith('/'):
                collection_id = collection_id[1:]
        
        collection_data = self._mock_client._data.get(collection_id, {})

        # Apply filters
        filtered_docs = self._apply_filters(collection_data)

        # Apply ordering
        docs_list = list(filtered_docs.items())
        ordered_docs = self._apply_ordering(docs_list)

        # Apply offset and limit
        start = self._offset
        end = (start + self._limit) if self._limit is not None else None
        sliced_docs = ordered_docs[start:end]

        for doc_id, doc_data in sliced_docs:
            doc_ref = self.document(doc_id)
            yield AsyncMockDocumentSnapshot(doc_ref, data=doc_data, exists=True)


from google.cloud.firestore_v1.async_aggregation import AsyncAggregationQuery


class MockAsyncAggregationResult:
    """Mock for the internal AggregationResult."""
    def __init__(self, alias, value):
        self.alias = alias
        self.value = value

class MockAsyncAggregationQuery:
    """Mock Firestore async aggregation query."""

    def __init__(self, query: "AsyncMockQuery"):
        self._query = query
        self._aggregations = []

    def count(self, alias: str) -> "MockAsyncAggregationQuery":
        self._aggregations.append({'type': 'count', 'alias': alias})
        return self

    def sum(self, field_ref: str, alias: str) -> "MockAsyncAggregationQuery":
        self._aggregations.append({'type': 'sum', 'field': field_ref, 'alias': alias})
        return self

    def avg(self, field_ref: str, alias: str) -> "MockAsyncAggregationQuery":
        self._aggregations.append({'type': 'avg', 'field': field_ref, 'alias': alias})
        return self

    async def stream(self) -> AsyncGenerator[List[MockAsyncAggregationResult], None]:
        """
        Stream aggregation results.
        """
        # Get documents from underlying query
        docs = []
        async for doc in self._query.stream():
            docs.append(doc)
        
        # Calculate aggregations based on documents
        results = []
        
        for agg in self._aggregations:
            if agg['type'] == 'count':
                value = len(docs)
                results.append(MockAsyncAggregationResult(agg['alias'], value))
            elif agg['type'] == 'sum':
                field = agg['field']
                value = sum(doc.to_dict().get(field, 0) for doc in docs)
                results.append(MockAsyncAggregationResult(agg['alias'], value))
            elif agg['type'] == 'avg':
                field = agg['field']
                values = [doc.to_dict().get(field, 0) for doc in docs]
                value = sum(values) / len(docs) if docs else 0
                results.append(MockAsyncAggregationResult(agg['alias'], value))
            else:
                continue
            print(f"DEBUG: Aggregation {agg['type']} for {agg['alias']} = {value}")
            results.append(MockAsyncAggregationResult(alias=agg['alias'], value=value))
        
        print(f"DEBUG: Mock aggregation returning {results}")
        # The real client yields a list containing one list of results.
        yield results





class AsyncMockCollectionReference(AsyncCollectionReference):
    """Async mock implementation of Firestore CollectionReference."""
    _document_class = AsyncMockDocumentReference

    def __init__(self, *path, client: 'AsyncMockFirestoreClient'):
        """
        Initialize async mock collection reference.
        
        Args:
            path: Collection path parts
            client: Mock Firestore client
        """
        super().__init__(*path, client=client)
        self._mock_client = client

    @property
    def path(self) -> str:
        """Return the full path of the collection."""
        return "/".join(self._path)

    def document(self, document_id: Optional[str] = None) -> 'AsyncMockDocumentReference':
        """Create a document reference."""
        doc_id = document_id or str(uuid.uuid4())
        return self._document_class(*self._path, doc_id, client=self._mock_client)
    
    def where(self, field_path: str, op_string: str, value: Any) -> 'AsyncMockQuery':
        """
        Create query with where filter.
        
        Args:
            field_path: Field path to filter on
            op_string: Comparison operator
            value: Value to compare against
            
        Returns:
            AsyncMockQuery with filter applied
        """
        return AsyncMockQuery(self, filters=[(field_path, op_string, value)])
    
    def order_by(self, field_path: str, direction: str = 'ASCENDING') -> 'AsyncMockQuery':
        """
        Create query with ordering.
        
        Args:
            field_path: Field path to order by
            direction: Sort direction
            
        Returns:
            AsyncMockQuery with ordering applied
        """
        return AsyncMockQuery(self, orders=[(field_path, direction)])
    
    def limit(self, count: int) -> 'AsyncMockQuery':
        """
        Create query with limit.
        
        Args:
            count: Maximum number of results
            
        Returns:
            AsyncMockQuery with limit applied
        """
        return AsyncMockQuery(self, limit=count)
    
    def offset(self, num_to_skip: int) -> 'AsyncMockQuery':
        """
        Create query with offset.
        
        Args:
            num_to_skip: Number of results to skip
            
        Returns:
            AsyncMockQuery with offset applied
        """
        return AsyncMockQuery(self, offset=num_to_skip)
    
    async def get(self) -> List['AsyncMockDocumentSnapshot']:
        """
        Get all documents in collection.
        
        Returns:
            List of AsyncMockDocumentSnapshot
        """
        query = AsyncMockQuery(self)
        return await query.get()
    
    async def stream(self) -> AsyncGenerator['AsyncMockDocumentSnapshot', None]:
        """
        Stream all documents in collection.
        
        Yields:
            AsyncMockDocumentSnapshot instances
        """
        query = AsyncMockQuery(self)
        async for snapshot in query.stream():
            yield snapshot
    
    async def add(self, document_data: Dict[str, Any]) -> 'AsyncMockDocumentReference':
        """
        Add document to collection with auto-generated ID.
        
        Args:
            document_data: Document data to add
            
        Returns:
            AsyncMockDocumentReference for created document
        """
        doc_ref = self.document()  # Auto-generate ID
        await doc_ref.set(document_data)
        return doc_ref

class AsyncMockTransaction:
    """Async mock implementation of Firestore Transaction."""
    
    def __init__(self, client):
        """
        Initialize async mock transaction.
        
        Args:
            client: Mock Firestore client
        """
        self._client = client
        self._operations: List[Dict[str, Any]] = []
        self._committed = False
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
    
    async def get(self, doc_ref: AsyncMockDocumentReference) -> 'AsyncMockDocumentSnapshot':
        """
        Get document in transaction.

        Args:
            doc_ref: Document reference to get

        Returns:
            Document snapshot with transaction-aware data
        """
        # First, check for pending operations on this document in this transaction
        # to ensure we have the most up-to-date view.
        # Get the current state from the mock client's data store
        collection_data = doc_ref._mock_client._data.get(doc_ref.parent.id, {})
        doc_data = collection_data.get(doc_ref.id)
        
        # Apply pending operations in order to get the transaction-local view
        current_data = doc_data
        for op in self._operations:
            if op['ref'].path == doc_ref.path:
                op_type = op.get('type')
                if op_type == 'set':
                    current_data = copy.deepcopy(op['data'])
                elif op_type == 'update':
                    if current_data is not None:
                        current_data.update(op['data'])
                elif op_type == 'delete':
                    current_data = None
        
        final_doc_data = current_data

        # Create a mock document snapshot with the final data
        return AsyncMockDocumentSnapshot(
            reference=doc_ref,
            data=final_doc_data,
            exists=(final_doc_data is not None)
        )

    def create(self, doc_ref: 'AsyncMockDocumentReference', document_data: Dict[str, Any]) -> None:
        """
        Create document in transaction.
        
        Args:
            doc_ref: Document reference to create
            document_data: Document data
        """
        # In a transaction, get() sees the current state including prior operations in the same transaction.
        # Note: This is synchronous for the mock
        self._operations.append({
            'type': 'create',
            'ref': doc_ref,
            'data': document_data
        })
    
    def set(self, doc_ref: AsyncMockDocumentReference, document_data: Dict[str, Any], merge: bool = False) -> None:
        """
        Set document in transaction.
        
        Args:
            doc_ref: Document reference to set
            document_data: Document data
            merge: Whether to merge with existing data
        """
        self._operations.append({
            'type': 'set',
            'ref': doc_ref,
            'data': document_data,
            'merge': merge
        })
    
    def update(self, doc_ref: AsyncMockDocumentReference, field_updates: Dict[str, Any]) -> None:
        """
        Update document in transaction.
        
        Args:
            doc_ref: Document reference to update
            field_updates: Fields to update
        """
        self._operations.append({
            'type': 'update',
            'ref': doc_ref,
            'data': field_updates
        })
    
    def delete(self, doc_ref: AsyncMockDocumentReference) -> None:
        """
        Delete document in transaction.
        
        Args:
            doc_ref: Document reference to delete
        """
        self._operations.append({
            'type': 'delete',
            'ref': doc_ref,
            'data': {}
        })
    
    async def commit(self) -> None:
        """Commit transaction operations."""
        if self._committed:
            raise ValueError("Transaction already committed")
        
        # Execute all operations
        for operation in self._operations:
            op_type = operation['type']
            doc_ref = operation['ref']
            data = operation['data']
            
            if op_type == 'create':
                await doc_ref.set(data, merge=False)
            elif op_type == 'set':
                merge = operation.get('merge', False)
                await doc_ref.set(data, merge=merge)
            elif op_type == 'update':
                await doc_ref.update(data)
            elif op_type == 'delete':
                await doc_ref.delete()
        
        self._committed = True


class AsyncMockBatch:
    """Async mock implementation of Firestore WriteBatch."""
    
    def __init__(self, client):
        """
        Initialize async mock batch.
        
        Args:
            client: Mock Firestore client
        """
        self._client = client
        self._operations: List[Dict[str, Any]] = []
    
    def set(self, doc_ref: AsyncMockDocumentReference, document_data: Dict[str, Any], merge: bool = False) -> 'AsyncMockBatch':
        """
        Add set operation to batch.
        
        Args:
            doc_ref: Document reference to set
            document_data: Document data
            merge: Whether to merge with existing data
            
        Returns:
            Self for method chaining
        """
        self._operations.append({
            'type': 'set',
            'ref': doc_ref,
            'data': document_data,
            'merge': merge
        })
        return self
    
    def update(self, doc_ref: AsyncMockDocumentReference, field_updates: Dict[str, Any]) -> 'AsyncMockBatch':
        """
        Add update operation to batch.
        
        Args:
            doc_ref: Document reference to update
            field_updates: Fields to update
            
        Returns:
            Self for method chaining
        """
        self._operations.append({
            'type': 'update',
            'ref': doc_ref,
            'data': field_updates
        })
        return self
    
    def delete(self, doc_ref: AsyncMockDocumentReference) -> 'AsyncMockBatch':
        """
        Add delete operation to batch.
        
        Args:
            doc_ref: Document reference to delete
            
        Returns:
            Self for method chaining
        """
        self._operations.append({
            'type': 'delete',
            'ref': doc_ref,
            'data': {}
        })
        return self
    
    async def commit(self) -> None:
        """Commit batch operations."""
        # Execute all operations
        for operation in self._operations:
            op_type = operation['type']
            doc_ref = operation['ref']
            data = operation['data']
            
            if op_type == 'create':
                await doc_ref.set(data, merge=False)
            elif op_type == 'set':
                merge = operation.get('merge', False)
                await doc_ref.set(data, merge=merge)
            elif op_type == 'update':
                await doc_ref.update(data)
            elif op_type == 'delete':
                await doc_ref.delete()


class AsyncMockFirestoreClient(AsyncClient):
    """Async mock implementation of Firestore Client."""
    def __init__(self, project: str = "test-project", credentials=None, database: str = "(default)"):
        """
        Initialize async mock Firestore client.
        
        Args:
            project: GCP project ID
            credentials: Mock credentials
            database: Firestore database name
        """
        self._project = project
        self._database = database
        self._credentials = credentials
        self._data = defaultdict(dict)  # In-memory data store
        self._transactions = []
        self._batches = []
    
    def begin_transaction(self, transaction):
        self._transactions.append(transaction)

    def end_transaction(self):
        if self._transactions:
            self._transactions.pop()
    
    def collection(self, collection_id: str) -> AsyncMockCollectionReference:
        """
        Get collection reference.
        
        Args:
            collection_id: Collection ID
            
        Returns:
            AsyncMockCollectionReference
        """
        return AsyncMockCollectionReference(collection_id, client=self)
    
    def document(self, *document_path_parts: str) -> AsyncMockDocumentReference:
        """
        Get document reference.
        
        Args:
            document_path: Document path
            
        Returns:
            AsyncMockDocumentReference
        """
        path_parts = []
        if len(document_path_parts) == 1 and "/" in document_path_parts[0]:
            path_parts = document_path_parts[0].split("/")
        else:
            path_parts = list(document_path_parts)

        if len(path_parts) == 0 or len(path_parts) % 2 != 0:
            raise ValueError(f"Invalid document path: {'/'.join(path_parts)}")

        return AsyncMockDocumentReference(*path_parts, client=self)
    
    def transaction(self) -> AsyncMockTransaction:
        """
        Create transaction.
        
        Returns:
            AsyncMockTransaction
        """
        return AsyncMockTransaction(self)
    
    def batch(self) -> AsyncMockBatch:
        """
        Create batch.
        
        Returns:
            AsyncMockBatch
        """
        return AsyncMockBatch(self)
    
    def clear_data(self):
        """Clear all data from the mock client."""
        self._data.clear()
    
    def get_data(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get all mock data."""
        return dict(self._data)
    
    def set_data(self, data: Dict[str, Dict[str, Dict[str, Any]]]) -> None:
        """Set mock data."""
        self._data.clear()
        self._data.update(data)
    
    async def _get_document_data(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get document data by path.

        Args:
            path: Document path (e.g., 'users/user1')

        Returns:
            Document data or None
        """
        try:
            collection_id, document_id = path.split('/')
            data = self._data.get(collection_id, {}).get(document_id)
            return copy.deepcopy(data) if data else None
        except (ValueError, KeyError):
            return None
    
    async def close(self) -> None:
        """Close mock client."""
        self._closed = True
    
    @property
    def closed(self) -> bool:
        """Check if client is closed."""
        return self._closed

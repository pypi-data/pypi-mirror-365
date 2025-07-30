"""
Mock implementations for Firestore schema testing.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional, Type, Union, Callable, Iterator
from datetime import datetime
import copy
import json
from unittest.mock import Mock, MagicMock


from ..core.base import Document, Collection
from ..schema_manager import FirestoreSchema
from ..core.exceptions import ValidationError, SchemaError
from google.cloud.firestore_v1.types import Value


class MockFirestoreClient:
    """
    Comprehensive mock Firestore client for testing.
    """
    
    def __init__(self, project_id: str = "test-project", **kwargs):
        """
        Initialize mock client.
        
        Args:
            project_id: Project ID for the mock client
        """
        # Do not call super().__init__() to avoid real database connection
        self.project_id = project_id
        self._data = {}
        self._transaction_data = {}
        self._listeners = {}
        self._call_history = []
        self._firestore_api = self._create_mock_firestore_api()
        self._client = self  # For compatibility with google-cloud-firestore's internal checks
        self._rpc_metadata = []  # For compatibility with aggregation queries

    def _parent_info(self) -> tuple[str, str]:
        """
        Helper to get parent path and prefix for aggregation queries.
        This mimics the behavior of the real client.
        """
        # This path should be the root for all documents in the database.
        path = f"projects/{self.project_id}/databases/(default)/documents"
        return path, path
    
    def collection(self, collection_id: str) -> "MockCollectionReference":
        """
        Get mock collection reference.
        
        Args:
            collection_id: Collection identifier
        
        Returns:
            Mock collection reference
        """
        self._record_call('collection', collection_id=collection_id)
        
        if collection_id not in self._data:
            self._data[collection_id] = {}
        
        return MockCollectionReference(self, collection_id)
    
    def document(self, document_path: str) -> "MockDocumentReference":
        """
        Get mock document reference by path.
        
        Args:
            document_path: Full document path (e.g., 'users/123')
        
        Returns:
            Mock document reference
        """
        self._record_call('document', document_path=document_path)
        
        path_parts = document_path.split('/')
        if len(path_parts) % 2 != 0:
            raise ValueError("Document path must have even number of segments")
        
        collection_id = path_parts[-2]
        document_id = path_parts[-1]
        
        return self.collection(collection_id).document(document_id)
    
    def transaction(self) -> "MockTransaction":
        """
        Create mock transaction.
        
        Returns:
            Mock transaction instance
        """
        self._record_call('transaction')
        return MockTransaction(self)
    
    def batch(self) -> "MockWriteBatch":
        """
        Create mock write batch.
        
        Returns:
            Mock write batch instance
        """
        self._record_call('batch')
        return MockWriteBatch(self)
    
    def _record_call(self, method: str, **kwargs) -> None:
        """Record method call for testing verification."""
        self._call_history.append({
            'method': method,
            'timestamp': datetime.now(),
            'args': kwargs
        })
    
    def get_call_history(self) -> List[Dict[str, Any]]:
        """Get history of all method calls."""
        return self._call_history.copy()
    
    def clear_call_history(self) -> None:
        """Clear call history."""
        self._call_history.clear()
    
    def clear_data(self) -> None:
        """Clear all stored data."""
        self._data.clear()
        self._transaction_data.clear()
    
    def get_data_snapshot(self) -> Dict[str, Any]:
        """Get snapshot of current data state."""
        return copy.deepcopy(self._data)
    
    def load_data_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Load data from snapshot."""
        self._data = copy.deepcopy(snapshot)

    def _create_mock_firestore_api(self):
        """Creates a mock for the internal _firestore_api."""
        api = MagicMock()

        def encode_value(value: Any) -> Value:
            if isinstance(value, str):
                return Value(string_value=value)
            if isinstance(value, bool):
                return Value(boolean_value=value)
            if isinstance(value, int):
                return Value(integer_value=value)
            if isinstance(value, float):
                return Value(double_value=value)
            if value is None:
                return Value(null_value="NULL_VALUE")
            # Add other types as needed for tests
            return Value(string_value=str(value)) # Fallback

        api.encode_value.side_effect = encode_value
        return api


from google.cloud.firestore_v1.types import StructuredQuery
from google.cloud.firestore_v1.aggregation import AggregationQuery

class MockCollectionReference:
    """Mock Firestore collection reference."""
    
    def __init__(self, client: MockFirestoreClient, collection_id: str, parent: Optional["MockDocumentReference"] = None):
        """
        Initialize mock collection reference.
        
        Args:
            client: Parent mock client
            collection_id: Collection identifier
            parent: Parent document reference (if a subcollection)
        """
        self._client = client
        self._collection_id = collection_id
        self._parent = parent or client  # The parent is the client for top-level collections
        self._path = f"{parent.path}/{collection_id}" if parent else collection_id
    
    @property
    def id(self) -> str:
        """Get collection ID."""
        return self._collection_id
    
    @property
    def path(self) -> str:
        """Get collection path."""
        return self._path
    
    def document(self, document_id: Optional[str] = None) -> "MockDocumentReference":
        """
        Get mock document reference.
        
        Args:
            document_id: Document identifier (auto-generated if None)
        
        Returns:
            Mock document reference
        """
        if document_id is None:
            document_id = f"auto_{int(datetime.now().timestamp() * 1000)}"
        
        self._client._record_call('collection.document', 
                                collection_id=self._collection_id,
                                document_id=document_id)
        
        return MockDocumentReference(self._client, self._collection_id, document_id)
    
    def add(self, document_data: Dict[str, Any]) -> "MockDocumentReference":
        """
        Add document with auto-generated ID.
        
        Args:
            document_data: Document data to add
        
        Returns:
            Mock document reference for the added document
        """
        doc_ref = self.document()  # Auto-generate ID
        doc_ref.set(document_data)
        return doc_ref
    
    def stream(self) -> Iterator[MockDocumentSnapshot]:
        """
        Stream all documents in collection.
        
        Yields:
            Mock document snapshots
        """
        self._client._record_call('collection.stream', collection_id=self._collection_id)
        
        collection_data = self._client._data.get(self._collection_id, {})
        
        for doc_id, doc_data in collection_data.items():
            yield MockDocumentSnapshot(self._collection_id, doc_id, doc_data, exists=True)
    
    def get(self) -> List["MockDocumentSnapshot"]:
        """
        Get all documents in collection.
        
        Returns:
            List of mock document snapshots
        """
        return list(self.stream())
    
    def where(self, field_path: str, op_string: str, value: Any) -> "MockQuery":
        """
        Create mock query with where clause.
        
        Args:
            field_path: Field to filter on
            op_string: Comparison operator
            value: Value to compare against
        
        Returns:
            Mock query instance
        """
        self._client._record_call('collection.where',
                                collection_id=self._collection_id,
                                field_path=field_path,
                                op_string=op_string,
                                value=value)
        
        return MockQuery(self._client, self._collection_id, [(field_path, op_string, value)], [])
    
    def order_by(self, field_path: str, direction: str = 'ASCENDING') -> "MockQuery":
        """
        Create mock query with order by clause.
        
        Args:
            field_path: Field to order by
            direction: Sort direction
        
        Returns:
            Mock query instance
        """
        return MockQuery(self._client, self._collection_id, [], [(field_path, direction)])
    
    def limit(self, count: int) -> "MockQuery":
        """
        Create mock query with limit.
        
        Args:
            count: Maximum number of results
        
        Returns:
            Mock query instance
        """
        return MockQuery(self._client, self._collection_id, [], [], count)

    def _to_protobuf(self) -> StructuredQuery:
        """Serializes the collection reference to a protobuf for queries."""
        return StructuredQuery(
            from_=[StructuredQuery.CollectionSelector(collection_id=self._collection_id)]
        )


class MockDocumentReference:
    """Mock Firestore document reference."""
    
    def __init__(self, client: MockFirestoreClient, collection_id: str, document_id: str):
        """
        Initialize mock document reference.
        
        Args:
            client: Parent mock client
            collection_id: Collection identifier
            document_id: Document identifier
        """
        self._client = client
        self._collection_id = collection_id
        self._document_id = document_id
        self._path = f"{collection_id}/{document_id}"
    
    @property
    def id(self) -> str:
        """Get document ID."""
        return self._document_id
    
    @property
    def path(self) -> str:
        """Get document path."""
        return self._path
    
    @property
    def parent(self) -> "MockCollectionReference":
        """Get parent collection reference."""
        return MockCollectionReference(self._client, self._collection_id)
    
    def get(self) -> "MockDocumentSnapshot":
        """
        Get document snapshot.
        
        Returns:
            Mock document snapshot
        """
        self._client._record_call('document.get',
                                collection_id=self._collection_id,
                                document_id=self._document_id)
        
        collection_data = self._client._data.get(self._collection_id, {})
        doc_data = collection_data.get(self._document_id, {})
        exists = self._document_id in collection_data
        
        return MockDocumentSnapshot(self._collection_id, self._document_id, doc_data, exists)
    
    def set(self, document_data: Dict[str, Any], merge: bool = False) -> None:
        """
        Set document data.
        
        Args:
            document_data: Data to set
            merge: Whether to merge with existing data
        """
        self._client._record_call('document.set',
                                collection_id=self._collection_id,
                                document_id=self._document_id,
                                merge=merge)
        
        if self._collection_id not in self._client._data:
            self._client._data[self._collection_id] = {}
        
        if merge and self._document_id in self._client._data[self._collection_id]:
            # Merge with existing data
            existing_data = self._client._data[self._collection_id][self._document_id]
            merged_data = existing_data.copy()
            merged_data.update(document_data)
            self._client._data[self._collection_id][self._document_id] = merged_data
        else:
            # Replace data
            self._client._data[self._collection_id][self._document_id] = document_data.copy()
    
    def update(self, field_updates: Dict[str, Any]) -> None:
        """
        Update specific fields in document.
        
        Args:
            field_updates: Fields to update
        """
        from google.cloud.exceptions import NotFound

        self._client._record_call('document.update',
                                collection_id=self._collection_id,
                                document_id=self._document_id)
        
        collection_data = self._client._data.get(self._collection_id, {})
        if self._document_id not in collection_data:
            raise NotFound(f"Document {self.path} not found.")
        
        # Update specific fields
        doc_data = collection_data[self._document_id]
        doc_data.update(field_updates)
    
    def delete(self) -> None:
        """Delete document."""
        from google.cloud.exceptions import NotFound

        self._client._record_call('document.delete',
                                collection_id=self._collection_id,
                                document_id=self._document_id)

        collection_data = self._client._data.get(self._collection_id, {})

        if self._document_id in collection_data:
            del collection_data[self._document_id]
        else:
            # Raise NotFound if the document does not exist, to match real Firestore behavior.
            raise NotFound(f"Document {self.path} not found.")

    def collection(self, collection_id: str) -> "MockCollectionReference":
        """
        Get subcollection reference.

        Args:
            collection_id: Subcollection identifier

        Returns:
            Mock subcollection reference
        """
        return MockCollectionReference(self._client, collection_id, parent=self)


from google.cloud.firestore_v1.base_document import DocumentSnapshot

class MockDocumentSnapshot(Mock):
    """Mock Firestore document snapshot that passes isinstance checks."""
    
    def __init__(self, collection_id: str, document_id: str, data: Dict[str, Any], exists: bool = True, **kwargs):
        """
        Initialize mock document snapshot.
        
        Args:
            collection_id: Collection identifier
            document_id: Document identifier
            data: Document data
            exists: Whether document exists
        """
        super().__init__(spec=DocumentSnapshot, **kwargs)
        self._collection_id = collection_id
        self._document_id = document_id
        self._data = data.copy()
        self.exists = exists
        
        # Create a mock client for the reference
        mock_client = MockFirestoreClient()
        self.reference = MockDocumentReference(mock_client, collection_id, document_id)

    @property
    def id(self) -> str:
        """Get document ID."""
        return self._document_id

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Document data as dictionary
        """
        return self._data.copy()

    def get(self, field_path: str) -> Any:
        """
        Get specific field value.
        
        Args:
            field_path: Field path (supports dot notation)
        
        Returns:
            Field value
        """
        keys = field_path.split('.')
        value = self._data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value


class MockQuery:
    """Mock Firestore query."""

    def _to_protobuf(self) -> StructuredQuery:
        """Serializes the query to a protobuf."""
        from_selector = StructuredQuery.CollectionSelector(collection_id=self._collection_id)
        where_filter = None
        if self._where_clauses:
            # This is a simplified mock. For multiple clauses, you'd need composite filters.
            field_path, op_string, value = self._where_clauses[0]
            op_map = {
                '==': StructuredQuery.FieldFilter.Operator.EQUAL,
                '<': StructuredQuery.FieldFilter.Operator.LESS_THAN,
                '>': StructuredQuery.FieldFilter.Operator.GREATER_THAN,
                # Add other operators as needed
            }
            where_filter = StructuredQuery.Filter(
                field_filter=StructuredQuery.FieldFilter(
                    field=StructuredQuery.FieldReference(field_path=field_path),
                    op=op_map.get(op_string, StructuredQuery.FieldFilter.Operator.OPERATOR_UNSPECIFIED),
                    value=self._client._firestore_api.encode_value(value)
                )
            )

        return StructuredQuery(
            from_=[from_selector],
            where=where_filter,
            # Order by and limit can be added here if needed for more complex tests
        )
    
    def __init__(self, 
                 client: MockFirestoreClient,
                 collection_id: str,
                 where_clauses: Optional[List] = None,
                 order_clauses: Optional[List] = None,
                 limit_count: Optional[int] = None):
        """
        Initialize mock query.
        
        Args:
            client: Parent mock client
            collection_id: Collection identifier
            where_clauses: List of where conditions
            order_clauses: List of order by conditions
            limit_count: Limit count
        """
        self._client = client
        self._collection_id = collection_id
        self._where_clauses = where_clauses or []
        self._order_clauses = order_clauses or []
        self._limit_count = limit_count
    
    def where(self, field_path: str, op_string: str, value: Any) -> "MockQuery":
        """Add where clause to query."""
        new_where_clauses = self._where_clauses + [(field_path, op_string, value)]
        return MockQuery(self._client, self._collection_id, new_where_clauses, 
                        self._order_clauses, self._limit_count)
    
    def order_by(self, field_path: str, direction: str = 'ASCENDING') -> "MockQuery":
        """Add order by clause to query."""
        new_order_clauses = self._order_clauses + [(field_path, direction)]
        return MockQuery(self._client, self._collection_id, self._where_clauses,
                        new_order_clauses, self._limit_count)
    
    def limit(self, count: int) -> "MockQuery":
        """Add limit to query."""
        return MockQuery(self._client, self._collection_id, self._where_clauses,
                        self._order_clauses, count)
    
    def stream(self) -> Iterator[MockDocumentSnapshot]:
        """
        Stream query results.
        
        Yields:
            Mock document snapshots matching query
        """
        collection_data = self._client._data.get(self._collection_id, {})
        results = []
        
        # Apply where clauses
        for doc_id, doc_data in collection_data.items():
            if self._matches_where_clauses(doc_data):
                results.append(MockDocumentSnapshot(self._collection_id, doc_id, doc_data))
        
        # Apply order by clauses
        for field_path, direction in self._order_clauses:
            reverse = direction == 'DESCENDING'
            results.sort(key=lambda doc: doc.get(field_path) or '', reverse=reverse)
        
        # Apply limit
        if self._limit_count:
            results = results[:self._limit_count]
        
        for result in results:
            yield result
    
    def get(self) -> List["MockDocumentSnapshot"]:
        """Get query results as list."""
        return list(self.stream())
    
    def _matches_where_clauses(self, doc_data: Dict[str, Any]) -> bool:
        """Check if document matches all where clauses."""
        for field_path, op_string, value in self._where_clauses:
            doc_value = self._get_field_value(doc_data, field_path)
            
            if not self._evaluate_condition(doc_value, op_string, value):
                return False
        
        return True
    
    def _get_field_value(self, doc_data: Dict[str, Any], field_path: str) -> Any:
        """Get field value from document data."""
        keys = field_path.split('.')
        value = doc_data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _evaluate_condition(self, doc_value: Any, op_string: str, query_value: Any) -> bool:
        """Evaluate a single where condition."""
        if op_string == '==':
            return doc_value == query_value
        elif op_string == '!=':
            return doc_value != query_value
        elif op_string == '<':
            return doc_value is not None and doc_value < query_value
        elif op_string == '<=':
            return doc_value is not None and doc_value <= query_value
        elif op_string == '>':
            return doc_value is not None and doc_value > query_value
        elif op_string == '>=':
            return doc_value is not None and doc_value >= query_value
        elif op_string == 'in':
            return doc_value in query_value
        elif op_string == 'not-in':
            return doc_value not in query_value
        elif op_string == 'array-contains':
            return isinstance(doc_value, list) and query_value in doc_value
        elif op_string == 'array-contains-any':
            return isinstance(doc_value, list) and any(v in doc_value for v in query_value)
        else:
            return False

    def aggregate(self, aggregations: List[Any]) -> "MockAggregationQuery":
        """
        Create a mock aggregation query.

        Args:
            aggregations: A list of aggregations to perform (we will mock this).

        Returns:
            A mock aggregation query instance.
        """
        return MockAggregationQuery(self)


class MockAggregationResult:
    """Mock for the internal AggregationResult."""
    def __init__(self, alias, value):
        self.alias = alias
        self.value = value

class MockAggregationQuery:
    """Mock Firestore aggregation query."""

    def __init__(self, query: "MockQuery"):
        """
        Initialize mock aggregation query.
        
        Args:
            query: The parent mock query to aggregate.
        """
        self._query = query
        self._aggregations = []

    def count(self, alias: Optional[str] = None) -> "MockAggregationQuery":
        """
        Add a count aggregation.
        
        Args:
            alias: The alias for the count result.
        
        Returns:
            The aggregation query instance.
        """
        if not alias:
            alias = "count"  # Default alias if not provided
        self._aggregations.append({'type': 'count', 'alias': alias})
        return self

    def sum(self, field_path: str, alias: Optional[str] = None) -> "MockAggregationQuery":
        """Add a sum aggregation."""
        if not alias:
            alias = f"sum_of_{field_path}"
        self._aggregations.append({'type': 'sum', 'field': field_path, 'alias': alias})
        return self

    def avg(self, field_path: str, alias: Optional[str] = None) -> "MockAggregationQuery":
        """Add an average aggregation."""
        if not alias:
            alias = f"avg_of_{field_path}"
        self._aggregations.append({'type': 'avg', 'field': field_path, 'alias': alias})
        return self

    def stream(self) -> Iterator[List[MockAggregationResult]]:
        """
        Stream aggregation results.
        
        Yields:
            A list containing mock aggregation results.
        """
        results = []
        docs = list(self._query.stream())
        for agg in self._aggregations:
            if agg['type'] == 'count':
                value = len(docs)
            elif agg['type'] == 'sum':
                value = sum(doc.get(agg['field']) for doc in docs if doc.get(agg['field']) is not None)
            elif agg['type'] == 'avg':
                values = [doc.get(agg['field']) for doc in docs if doc.get(agg['field']) is not None]
                value = sum(values) / len(values) if values else 0
            else:
                continue
            results.append(MockAggregationResult(alias=agg['alias'], value=value))
        
        yield results


class MockTransaction:
    """Mock Firestore transaction."""
    
    def __init__(self, client: MockFirestoreClient):
        """
        Initialize mock transaction.
        
        Args:
            client: Parent mock client
        """
        self._client = client
        self._operations = []
        self._committed = False
    
    def get(self, doc_ref: MockDocumentReference) -> "MockDocumentSnapshot":
        """Get document within transaction."""
        return doc_ref.get()
    
    def set(self, doc_ref: MockDocumentReference, document_data: Dict[str, Any], merge: bool = False) -> None:
        """Add set operation to transaction."""
        self._operations.append(('set', doc_ref, document_data, {'merge': merge}))
    
    def update(self, doc_ref: MockDocumentReference, field_updates: Dict[str, Any]) -> None:
        """Add update operation to transaction."""
        self._operations.append(('update', doc_ref, field_updates, {}))
    
    def delete(self, doc_ref: MockDocumentReference) -> None:
        """Add delete operation to transaction."""
        self._operations.append(('delete', doc_ref, None, {}))
    
    def commit(self) -> None:
        """Commit transaction operations."""
        if self._committed:
            raise ValueError("Transaction already committed")
        
        # Execute all operations atomically
        for operation, doc_ref, data, options in self._operations:
            if operation == 'set':
                doc_ref.set(data, merge=options.get('merge', False))
            elif operation == 'update':
                doc_ref.update(data)
            elif operation == 'delete':
                doc_ref.delete()
        
        self._committed = True
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with auto-commit."""
        if not self._committed:
            self.commit()


class MockWriteBatch:
    """Mock Firestore write batch."""
    
    def __init__(self, client: MockFirestoreClient):
        """
        Initialize mock write batch.
        
        Args:
            client: Parent mock client
        """
        self._client = client
        self._operations = []
        self._committed = False
    
    def set(self, doc_ref: MockDocumentReference, document_data: Dict[str, Any], merge: bool = False) -> "MockWriteBatch":
        """Add set operation to batch."""
        self._operations.append(('set', doc_ref, document_data, {'merge': merge}))
        return self
    
    def update(self, doc_ref: MockDocumentReference, field_updates: Dict[str, Any]) -> "MockWriteBatch":
        """Add update operation to batch."""
        self._operations.append(('update', doc_ref, field_updates, {}))
        return self
    
    def delete(self, doc_ref: MockDocumentReference) -> "MockWriteBatch":
        """Add delete operation to batch."""
        self._operations.append(('delete', doc_ref, None, {}))
        return self
    
    def commit(self) -> None:
        """Commit batch operations."""
        if self._committed:
            raise ValueError("Batch already committed")
        
        # Execute all operations
        for operation, doc_ref, data, options in self._operations:
            if operation == 'set':
                doc_ref.set(data, merge=options.get('merge', False))
            elif operation == 'update':
                doc_ref.update(data)
            elif operation == 'delete':
                doc_ref.delete()
        
        self._committed = True


def create_mock_client(project_id: str = "test-project") -> MockFirestoreClient:
    """
    Factory function to create a mock Firestore client.
    
    Args:
        project_id: Project ID for the mock client
    
    Returns:
        Configured MockFirestoreClient instance
    """
    return MockFirestoreClient(project_id=project_id)


def create_mock_document_data(document_class: Type[Document], **overrides) -> Dict[str, Any]:
    """
    Create mock document data based on document class field definitions.
    
    Args:
        document_class: Document class to create data for
        **overrides: Field value overrides
    
    Returns:
        Mock document data dictionary
    """
    if not hasattr(document_class, '_field_definitions'):
        raise SchemaError(f"Document class {document_class.__name__} has no field definitions")
    
    mock_data = {}
    
    for field_name, field_obj in document_class._field_definitions.items():
        if field_name in overrides:
            mock_data[field_name] = overrides[field_name]
            continue
        
        # Generate mock value based on field type
        field_type = field_obj.field_type
        
        if field_type == str:
            mock_data[field_name] = f"mock_{field_name}"
        elif field_type == int:
            mock_data[field_name] = 42
        elif field_type == float:
            mock_data[field_name] = 3.14
        elif field_type == bool:
            mock_data[field_name] = True
        elif field_type == datetime:
            mock_data[field_name] = datetime.now()
        elif field_type == list:
            mock_data[field_name] = ["item1", "item2"]
        elif field_type == dict:
            mock_data[field_name] = {"key": "value"}
        else:
            mock_data[field_name] = f"mock_{field_name}_value"
    
    return mock_data

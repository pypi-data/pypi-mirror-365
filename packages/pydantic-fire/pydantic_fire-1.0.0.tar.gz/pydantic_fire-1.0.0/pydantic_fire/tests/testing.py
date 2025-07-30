"""
Testing utilities for Firestore schema with emulator support.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional, Type, Union, Callable
from datetime import datetime
import json
import os
import subprocess
import time
import threading
from contextlib import contextmanager

from ..core.base import Document, Collection
from ..schema_manager import FirestoreSchema
from ..core.exceptions import SchemaError


class FirestoreTestClient:
    """
    Test client for Firestore with emulator support and mock capabilities.
    """
    
    def __init__(self, 
                 use_emulator: bool = True,
                 project_id: str = "test-project",
                 emulator_host: str = "localhost",
                 emulator_port: int = 8080):
        """
        Initialize test client with emulator support.
        
        Args:
            use_emulator: Whether to use Firestore emulator
            project_id: Firebase project ID for testing
            emulator_host: Emulator host address
            emulator_port: Emulator port number
        """
        self.use_emulator = use_emulator
        self.project_id = project_id
        self.emulator_host = emulator_host
        self.emulator_port = emulator_port
        self._client = None
        self._emulator_process = None
        
        if use_emulator:
            self._setup_emulator()
        else:
            self._setup_mock_client()
    
    def _setup_emulator(self) -> None:
        """Setup Firestore emulator for testing."""
        try:
            # Set environment variables for emulator
            os.environ["FIRESTORE_EMULATOR_HOST"] = f"{self.emulator_host}:{self.emulator_port}"
            os.environ["GCLOUD_PROJECT"] = self.project_id
            
            # Try to import firebase_admin
            try:
                import firebase_admin
                from firebase_admin import firestore, credentials
                
                # Initialize Firebase app with emulator
                if not firebase_admin._apps:
                    cred = credentials.Certificate({
                        "type": "service_account",
                        "project_id": self.project_id,
                        "private_key_id": "test",
                        "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
                        "client_email": f"test@{self.project_id}.iam.gserviceaccount.com",
                        "client_id": "test",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    })
                    firebase_admin.initialize_app(cred)
                
                self._client = firestore.client()
                
            except ImportError:
                # Fallback to google-cloud-firestore
                from google.cloud import firestore
                self._client = firestore.Client(project=self.project_id)
                
        except ImportError as e:
            raise SchemaError(f"Firebase/Firestore client not available: {e}")
    
    def _setup_mock_client(self) -> None:
        """Setup mock Firestore client for testing without emulator."""
        self._client = MockFirestoreClient()
    
    def start_emulator(self) -> None:
        """Start Firestore emulator process."""
        if not self.use_emulator:
            return
        
        try:
            # Start emulator in background
            cmd = [
                "firebase", "emulators:start",
                "--only", "firestore",
                "--project", self.project_id,
                f"--port={self.emulator_port}"
            ]
            
            self._emulator_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for emulator to start
            time.sleep(3)
            
        except FileNotFoundError:
            print("Warning: Firebase CLI not found. Using mock client instead.")
            self._setup_mock_client()
            self.use_emulator = False
    
    def stop_emulator(self) -> None:
        """Stop Firestore emulator process."""
        if self._emulator_process:
            self._emulator_process.terminate()
            self._emulator_process.wait()
            self._emulator_process = None
    
    def setup_test_data(self, schema_definitions: Dict[str, Any]) -> None:
        """
        Setup test data from schema definitions.
        
        Args:
            schema_definitions: Dictionary mapping collection names to test data
        """
        for collection_name, test_data in schema_definitions.items():
            if not isinstance(test_data, list):
                test_data = [test_data]
            
            for doc_data in test_data:
                doc_id = doc_data.get('id', f"test_{int(time.time() * 1000)}")
                if 'id' in doc_data:
                    del doc_data['id']
                
                if self._client:
                    self._client.collection(collection_name).document(doc_id).set(doc_data)
    
    def clear_test_data(self, collection_names: Optional[List[str]] = None) -> None:
        """
        Clear test data from specified collections.
        
        Args:
            collection_names: List of collection names to clear (if None, clear all)
        """
        if collection_names is None:
            # Get all registered collections
            collection_names = list(FirestoreSchema._registry.keys())
        
        for collection_name in collection_names:
            # Delete all documents in collection
            if self._client:
                docs = self._client.collection(collection_name).stream()
            else:
                docs = []
            for doc in docs:
                doc.reference.delete()
    
    def generate_test_data(self, 
                          document_class: Type[Document], 
                          count: int = 5,
                          **field_overrides) -> List[Dict[str, Any]]:
        """
        Generate test data for a document class based on its field definitions.
        
        Args:
            document_class: Document class to generate data for
            count: Number of test documents to generate
            **field_overrides: Override values for specific fields
        
        Returns:
            List of generated test data dictionaries
        """
        if not hasattr(document_class, '_field_definitions'):
            raise SchemaError(f"Document class {document_class.__name__} has no field definitions")
        
        test_data = []
        
        for i in range(count):
            doc_data = {}
            
            for field_name, field_obj in document_class._field_definitions.items():
                if field_name in field_overrides:
                    doc_data[field_name] = field_overrides[field_name]
                    continue
                
                # Generate test value based on field type
                test_value = self._generate_field_value(field_obj, i)
                if test_value is not None:
                    doc_data[field_name] = test_value
            
            test_data.append(doc_data)
        
        return test_data
    
    def _generate_field_value(self, field_obj: Any, index: int) -> Any:
        """Generate a test value for a field based on its type."""
        field_type = field_obj.field_type
        
        if field_type == str:
            return f"test_string_{index}"
        elif field_type == int:
            return index + 1
        elif field_type == float:
            return float(index + 1.5)
        elif field_type == bool:
            return index % 2 == 0
        elif field_type == datetime:
            return datetime.now()
        elif field_type == list:
            return [f"item_{index}_1", f"item_{index}_2"]
        elif field_type == dict:
            return {"key": f"value_{index}"}
        else:
            return f"test_value_{index}"
    
    @contextmanager
    def test_transaction(self):
        """Context manager for test transactions."""
        if self._client and hasattr(self._client, 'transaction'):
            transaction = self._client.transaction()
            try:
                yield transaction
            finally:
                pass  # Transaction cleanup handled by client
        else:
            # Mock transaction
            yield MockTransaction()
    
    def get_client(self):
        """Get the underlying Firestore client."""
        return self._client
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.stop_emulator()


class MockFirestoreClient:
    """
    Mock Firestore client for testing without emulator.
    """
    
    def __init__(self):
        """Initialize mock client with in-memory storage."""
        self._data = {}
    
    def collection(self, collection_id: str):
        """Get mock collection reference."""
        return MockCollectionReference(self._data, collection_id)
    
    def transaction(self):
        """Get mock transaction."""
        return MockTransaction()


class MockCollectionReference:
    """Mock Firestore collection reference."""
    
    def __init__(self, data_store: Dict, collection_id: str):
        self._data = data_store
        self._collection_id = collection_id
        
        if collection_id not in self._data:
            self._data[collection_id] = {}
    
    def document(self, document_id: str):
        """Get mock document reference."""
        return MockDocumentReference(self._data, self._collection_id, document_id)
    
    def stream(self):
        """Stream all documents in collection."""
        for doc_id, doc_data in self._data[self._collection_id].items():
            yield MockDocumentSnapshot(self._collection_id, doc_id, doc_data)


class MockDocumentReference:
    """Mock Firestore document reference."""
    
    def __init__(self, data_store: Dict, collection_id: str, document_id: str):
        self._data = data_store
        self._collection_id = collection_id
        self._document_id = document_id
    
    def set(self, data: Dict[str, Any]) -> None:
        """Set document data."""
        self._data[self._collection_id][self._document_id] = data.copy()
    
    def get(self):
        """Get document snapshot."""
        doc_data = self._data[self._collection_id].get(self._document_id, {})
        return MockDocumentSnapshot(self._collection_id, self._document_id, doc_data)
    
    def delete(self) -> None:
        """Delete document."""
        if self._document_id in self._data[self._collection_id]:
            del self._data[self._collection_id][self._document_id]


class MockDocumentSnapshot:
    """Mock Firestore document snapshot."""
    
    def __init__(self, collection_id: str, document_id: str, data: Dict[str, Any]):
        self._collection_id = collection_id
        self._document_id = document_id
        self._data = data
        self.reference = MockDocumentReference({collection_id: {document_id: data}}, collection_id, document_id)
    
    @property
    def id(self) -> str:
        """Get document ID."""
        return self._document_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self._data.copy()
    
    def exists(self) -> bool:
        """Check if document exists."""
        return bool(self._data)


class MockTransaction:
    """Mock Firestore transaction."""
    
    def __init__(self):
        self._operations = []
    
    def set(self, doc_ref, data: Dict[str, Any]) -> None:
        """Add set operation to transaction."""
        self._operations.append(('set', doc_ref, data))
    
    def update(self, doc_ref, data: Dict[str, Any]) -> None:
        """Add update operation to transaction."""
        self._operations.append(('update', doc_ref, data))
    
    def delete(self, doc_ref) -> None:
        """Add delete operation to transaction."""
        self._operations.append(('delete', doc_ref, None))


def create_test_client(use_emulator: bool = True, **kwargs) -> FirestoreTestClient:
    """
    Factory function to create a test client.
    
    Args:
        use_emulator: Whether to use Firestore emulator
        **kwargs: Additional arguments for FirestoreTestClient
    
    Returns:
        Configured FirestoreTestClient instance
    """
    return FirestoreTestClient(use_emulator=use_emulator, **kwargs)


def setup_test_environment(collections_data: Optional[Dict[str, Any]] = None) -> FirestoreTestClient:
    """
    Setup complete test environment with data.
    
    Args:
        collections_data: Dictionary mapping collection names to test data
    
    Returns:
        Configured test client with data loaded
    """
    client = create_test_client()
    
    if collections_data:
        client.setup_test_data(collections_data)
    
    return client

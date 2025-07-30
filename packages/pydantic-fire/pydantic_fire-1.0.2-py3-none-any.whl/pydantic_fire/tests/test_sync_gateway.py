"""
Tests for the synchronous Firestore Gateway.
"""

import pytest
from pydantic import BaseModel
from typing import Optional, Dict, Any, cast, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from ..core.base import Document
from ..gateway.sync_gateway import FirestoreGateway
from ..gateway.exceptions import DocumentNotFoundError, DocumentAlreadyExistsError
from .mocks import MockFirestoreClient, create_mock_document_data, MockAggregationQuery
from ..core.fields import Field

class UserDocument(Document):
    name: str
    age: int
    email: Optional[str]

    class Fields:
        name = Field(str)
        age = Field(int)
        email = Field(str, required=False)

# 2. Pytest Fixture for the Gateway
@pytest.fixture
def mock_client() -> MockFirestoreClient:
    """Provides a mock Firestore client for testing."""
    return MockFirestoreClient()

@pytest.fixture
def gateway(mock_client: MockFirestoreClient) -> FirestoreGateway:
    """Provides a FirestoreGateway instance initialized with a mock client."""
    return FirestoreGateway(client=mock_client)  # type: ignore

@pytest.fixture
def mock_aggregation(monkeypatch):
    """Fixture to mock the real AggregationQuery with our mock version."""
    # The target is the full path to the class *as it is imported and used* in the module under test.
    monkeypatch.setattr(
        'firestore_schema.gateway.sync_gateway.AggregationQuery',
        MockAggregationQuery
    )  # type: ignore

# 3. Test Cases

def test_get_document_found(gateway: FirestoreGateway, mock_client: MockFirestoreClient):
    """Test that `get` returns a validated model when a document is found."""
    logging.info("Starting test: test_get_document_found")
    # Arrange: Add data to the mock Firestore
    doc_path = "users/test_user"
    doc_data = {"name": "Test User", "age": 30}
    mock_client.collection("users").document("test_user").set(doc_data)

    # Act: Call the get method
    user = gateway.get(doc_path, UserDocument)

    # Assert: Check that the returned object is a valid UserDocument instance
    assert user is not None
    assert isinstance(user, UserDocument._pydantic_model)
    user_model = cast(UserDocument._pydantic_model, user)  # type: ignore
    assert user_model.name == "Test User"
    assert user_model.age == 30

def test_get_document_not_found(gateway: FirestoreGateway):
    """Test that `get` returns None when a document is not found."""
    logging.info("Starting test: test_get_document_not_found")
    # Arrange: The document does not exist
    doc_path = "users/non_existent_user"

    # Act: Call the get method
    user = gateway.get(doc_path, UserDocument)

    # Assert: Check that the result is None
    assert user is None

def test_document_exists(gateway: FirestoreGateway, mock_client: MockFirestoreClient):
    """Test that `exists` returns True for a document that exists."""
    logging.info("Starting test: test_document_exists")
    # Arrange: Add data to the mock Firestore
    doc_path = "users/test_user"
    doc_data = {"name": "Test User", "age": 30}
    mock_client.collection("users").document("test_user").set(doc_data)

    # Act: Call the exists method
    result = gateway.exists(doc_path, model_class=UserDocument)

    # Assert: Check that the result is True
    assert result is True

def test_document_does_not_exist(gateway: FirestoreGateway):
    """Test that `exists` returns False for a document that does not exist."""
    logging.info("Starting test: test_document_does_not_exist")
    # Arrange: The document does not exist
    doc_path = "users/non_existent_user"

    # Act: Call the exists method
    result = gateway.exists(doc_path, model_class=UserDocument)

    # Assert: Check that the result is False
    assert result is False


# 4. Tests for Transactional CRUD Methods

def test_create_success(gateway: FirestoreGateway, mock_client: MockFirestoreClient):
    """Test successful document creation."""
    logging.info("Starting test: test_create_success")
    # Arrange
    doc_path = "users/new_user"
    user_data = {"name": "New User", "age": 25}

    # Act
    created_user = gateway.create(doc_path, UserDocument, user_data)

    # Assert
    assert isinstance(created_user, UserDocument._pydantic_model)
    created_user_model = cast(UserDocument._pydantic_model, created_user)  # type: ignore
    assert created_user_model.name == "New User"
    # Verify data in mock client
    stored_data = mock_client.collection("users").document("new_user").get().to_dict()
    assert stored_data is not None
    assert stored_data["name"] == "New User"

def test_create_document_already_exists(gateway: FirestoreGateway, mock_client: MockFirestoreClient):
    """Test that create raises DocumentAlreadyExistsError if the document exists."""
    logging.info("Starting test: test_create_document_already_exists")
    # Arrange
    doc_path = "users/existing_user"
    mock_client.collection("users").document("existing_user").set({"name": "Exists", "age": 99})

    # Act & Assert
    with pytest.raises(DocumentAlreadyExistsError):
        gateway.create(doc_path, UserDocument, {"name": "New", "age": 1})

def test_set_new_document(gateway: FirestoreGateway, mock_client: MockFirestoreClient):
    """Test that `set` creates a new document."""
    logging.info("Starting test: test_set_new_document")
    # Arrange
    doc_path = "users/set_user"
    user_data = {"name": "Set User", "age": 40}

    # Act
    gateway.set(doc_path, UserDocument, user_data)

    # Assert
    stored_data = mock_client.collection("users").document("set_user").get().to_dict()
    assert stored_data is not None
    assert stored_data["age"] == 40

def test_set_overwrite_document(gateway: FirestoreGateway, mock_client: MockFirestoreClient):
    """Test that `set` overwrites an existing document."""
    logging.info("Starting test: test_set_overwrite_document")
    # Arrange
    doc_path = "users/overwrite_user"
    mock_client.collection("users").document("overwrite_user").set({"name": "Original", "age": 50})
    new_data = {"name": "Overwritten", "age": 51}

    # Act
    gateway.set(doc_path, UserDocument, new_data)

    # Assert
    stored_data = mock_client.collection("users").document("overwrite_user").get().to_dict()
    assert stored_data is not None
    assert stored_data["name"] == "Overwritten"
    assert stored_data["age"] == 51

def test_set_merge_document(gateway: FirestoreGateway, mock_client: MockFirestoreClient):
    """Test that `set` with merge=True updates fields."""
    logging.info("Starting test: test_set_merge_document")
    # Arrange
    doc_path = "users/merge_user"
    mock_client.collection("users").document("merge_user").set({"name": "Original", "age": 60, "email": "original@test.com"})
    new_data = {"age": 61, "email": "merged@test.com"}

    # Act
    gateway.set(doc_path, UserDocument, new_data, merge=True)

    # Assert
    stored_data = mock_client.collection("users").document("merge_user").get().to_dict()
    assert stored_data is not None
    assert stored_data["name"] == "Original"  # Should not be changed
    assert stored_data["age"] == 61
    assert stored_data["email"] == "merged@test.com"

def test_update_success(gateway: FirestoreGateway, mock_client: MockFirestoreClient):
    """Test successful document update."""
    logging.info("Starting test: test_update_success")
    # Arrange
    doc_path = "users/update_user"
    mock_client.collection("users").document("update_user").set({"name": "Initial", "age": 70})
    update_data = {"age": 71, "email": "updated@test.com"}

    # Act
    updated_model = gateway.update(doc_path, UserDocument, update_data)

    # Assert
    assert isinstance(updated_model, UserDocument._pydantic_model)
    updated_model_cast = cast(UserDocument._pydantic_model, updated_model)  # type: ignore
    assert updated_model_cast.age == 71
    assert updated_model_cast.email == "updated@test.com"
    stored_data = mock_client.collection("users").document("update_user").get().to_dict()
    assert stored_data is not None
    assert stored_data["age"] == 71

def test_update_document_not_found(gateway: FirestoreGateway):
    """Test that update raises DocumentNotFoundError if the document does not exist."""
    logging.info("Starting test: test_update_document_not_found")
    # Arrange
    doc_path = "users/non_existent_for_update"

    # Act & Assert
    with pytest.raises(DocumentNotFoundError):
        gateway.update(doc_path, UserDocument, {"age": 1})

def test_delete_success(gateway: FirestoreGateway, mock_client: MockFirestoreClient):
    """Test successful document deletion."""
    logging.info("Starting test: test_delete_success")
    # Arrange
    doc_path = "users/delete_user"
    mock_client.collection("users").document("delete_user").set({"name": "Delete Me", "age": 99})

    # Act
    gateway.delete(doc_path, model_class=UserDocument)

    # Assert
    snapshot = mock_client.collection("users").document("delete_user").get()
    assert not snapshot.exists

def test_delete_document_not_found(gateway: FirestoreGateway):
    """Test that delete raises DocumentNotFoundError if the document does not exist."""
    logging.info("Starting test: test_delete_document_not_found")
    # Arrange
    doc_path = "users/non_existent_for_delete"

    # Act & Assert
    with pytest.raises(DocumentNotFoundError):
        gateway.delete(doc_path, model_class=UserDocument)


# 5. Tests for Batch Writer

def test_batch_writer_success(gateway: FirestoreGateway, mock_client: MockFirestoreClient):
    """Test that the batch writer successfully commits all operations."""
    logging.info("Starting test: test_batch_writer_success")
    # Arrange: Prepare existing data
    mock_client.collection("users").document("update_me").set({"name": "Initial", "age": 10})
    mock_client.collection("users").document("delete_me").set({"name": "Delete", "age": 20})

    # Act: Perform batch operations
    with gateway.batch() as batch:
        batch.create("users/create_me", UserDocument, {"name": "Created", "age": 30})
        batch.update("users/update_me", UserDocument, {"age": 11})
        batch.delete("users/delete_me", UserDocument)

    # Assert: Verify the results
    created_doc = mock_client.collection("users").document("create_me").get()
    assert created_doc.exists
    assert created_doc.to_dict()["age"] == 30

    updated_doc = mock_client.collection("users").document("update_me").get()
    assert updated_doc.exists
    assert updated_doc.to_dict()["age"] == 11

    deleted_doc = mock_client.collection("users").document("delete_me").get()
    assert not deleted_doc.exists

def test_batch_writer_failure_rolls_back(gateway: FirestoreGateway, mock_client: MockFirestoreClient):
    """Test that the batch writer rolls back operations on failure."""
    logging.info("Starting test: test_batch_writer_failure_rolls_back")
    # Arrange: Prepare existing data
    mock_client.collection("users").document("dont_update").set({"name": "Initial", "age": 50})

    # Act & Assert: An exception within the 'with' block should prevent any commits
    with pytest.raises(ValueError, match="Test error"):
        with gateway.batch() as batch:
            batch.create("users/dont_create", UserDocument, {"name": "Created", "age": 60})
            batch.update("users/dont_update", UserDocument, {"age": 51})
            raise ValueError("Test error")

    # Assert: Verify that no changes were committed
    created_doc = mock_client.collection("users").document("dont_create").get()
    assert not created_doc.exists

    updated_doc = mock_client.collection("users").document("dont_update").get()
    assert updated_doc.to_dict()["age"] == 50  # Age should remain unchanged


# 6. Tests for Query Builder

@pytest.fixture
def setup_query_data(mock_client: MockFirestoreClient):
    """Populates the mock client with data for querying."""
    mock_client.collection("users").document("user1").set({"name": "Alice", "age": 25, "email": "alice@test.com"})
    mock_client.collection("users").document("user2").set({"name": "Bob", "age": 30, "email": "bob@test.com"})
    mock_client.collection("users").document("user3").set({"name": "Charlie", "age": 30, "email": "charlie@test.com"})
    mock_client.collection("users").document("user4").set({"name": "Diana", "age": 35, "email": "diana@test.com"})

def test_query_where(gateway: FirestoreGateway, setup_query_data):
    """Test querying with a 'where' clause."""
    logging.info("Starting test: test_query_where")
    # Act
    results_raw = gateway.query("users", UserDocument).where("age", "==", 30).get()
    assert isinstance(results_raw, list)
    results = cast(List[UserDocument], results_raw)

    # Assert
    assert len(results) == 2
    assert {user.name for user in results} == {"Bob", "Charlie"}

def test_query_order_by(gateway: FirestoreGateway, setup_query_data):
    """Test querying with an 'order_by' clause."""
    logging.info("Starting test: test_query_order_by")
    # Act
    results_raw = gateway.query("users", UserDocument).order_by("age", direction="DESCENDING").get()
    assert isinstance(results_raw, list)
    results = cast(List[UserDocument], results_raw)

    # Assert
    assert len(results) == 4
    assert [user.age for user in results] == [35, 30, 30, 25]

def test_query_limit(gateway: FirestoreGateway, setup_query_data):
    """Test querying with a 'limit' clause."""
    logging.info("Starting test: test_query_limit")
    # Act
    results_raw = gateway.query("users", UserDocument).order_by("name").limit(2).get()
    assert isinstance(results_raw, list)
    results = cast(List[UserDocument], results_raw)

    # Assert
    assert len(results) == 2
    assert [user.name for user in results] == ["Alice", "Bob"]

def test_query_get_one_found(gateway: FirestoreGateway, setup_query_data):
    """Test get_one() when a document is found."""
    logging.info("Starting test: test_query_get_one_found")
    # Act
    result = gateway.query("users", UserDocument).where("name", "==", "Diana").get_one()

    # Assert
    assert result is not None
    assert result.name == "Diana"
    assert result.age == 35

def test_query_get_one_not_found(gateway: FirestoreGateway, setup_query_data):
    """Test get_one() when no document is found."""
    logging.info("Starting test: test_query_get_one_not_found")
    # Act
    result = gateway.query("users", UserDocument).where("name", "==", "Eve").get_one()

    # Assert
    assert result is None

def test_query_aggregation_count(gateway: FirestoreGateway, setup_query_data, mock_aggregation):
    """Test aggregation query with count."""
    logging.info("Starting test: test_query_aggregation_count")
    # Act
    result = gateway.query("users").count(alias="total_users").get()

    # Assert
    assert result == {"total_users": 4}

def test_query_aggregation_sum_and_avg(gateway: FirestoreGateway, setup_query_data, mock_aggregation):
    """Test aggregation query with sum and avg."""
    logging.info("Starting test: test_query_aggregation_sum_and_avg")
    # Act
    result = gateway.query("users").sum("age", alias="total_age").avg("age", alias="avg_age").get()

    # Assert
    assert isinstance(result, dict)  # Fix for type checker
    assert result["total_age"] == 25 + 30 + 30 + 35
    assert result["avg_age"] == (25 + 30 + 30 + 35) / 4

def test_query_chaining(gateway: FirestoreGateway, setup_query_data):
    """Test chaining multiple query conditions."""
    logging.info("Starting test: test_query_chaining")
    # Act
    results_raw = gateway.query("users", UserDocument).where("age", ">", 25).order_by("name").limit(2).get()
    assert isinstance(results_raw, list)
    results = cast(List[UserDocument], results_raw)

    # Assert
    assert len(results) == 2
    assert [user.name for user in results] == ["Bob", "Charlie"]

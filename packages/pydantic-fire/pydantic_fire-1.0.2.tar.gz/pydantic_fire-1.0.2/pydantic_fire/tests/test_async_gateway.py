"""
Tests for the asynchronous Firestore Gateway.
"""

import pytest
import pytest_asyncio
from pydantic import BaseModel
from typing import Optional, cast, Union, AsyncGenerator
from ..gateway.async_gateway import AsyncFirestoreGateway
from ..async_operations.async_base import AsyncDocument
from ..core.base import Collection
from ..core.fields import Field
from google.cloud.firestore_v1.async_client import AsyncClient

from ..async_operations.async_transactions import (
    initialize_async_transaction_manager,
    clear_global_async_transaction_manager,
)
from ..gateway.exceptions import DocumentNotFoundError, DocumentAlreadyExistsError
from ..tests.async_mocks import (
    AsyncMockFirestoreClient,
    MockAsyncAggregationQuery,
)

# 1. Test Schema Definition
class AsyncUserDocument(AsyncDocument):
    class Fields:
        name = Field(str, required=True)
        age = Field(int, required=True)
        email = Field(str, required=False)

class UsersCollection(Collection):
    _path_template = "users"
    _document_class = AsyncUserDocument

users_collection = UsersCollection(base_path="")

# 2. Pytest Fixture for the Async Gateway
@pytest_asyncio.fixture
async def mock_client() -> AsyncMockFirestoreClient:
    """Provides a mock async Firestore client for testing."""
    return AsyncMockFirestoreClient()

@pytest_asyncio.fixture
async def gateway(
    mock_client: AsyncMockFirestoreClient,
) -> AsyncGenerator[AsyncFirestoreGateway, None]:
    """Provides an AsyncFirestoreGateway instance with a configured global client."""
    # Initialize the global manager for transactional operations
    initialize_async_transaction_manager(cast(AsyncClient, mock_client))

    yield AsyncFirestoreGateway(client=cast(AsyncClient, mock_client))

    # Clean up the global manager after the test
    clear_global_async_transaction_manager()
    mock_client.clear_data()  # Ensure data isolation

@pytest.fixture
def mock_async_aggregation(monkeypatch):
    """Fixture to mock the real AsyncAggregationQuery with our mock version."""
    # Patch the AsyncAggregationQuery class directly in the module where it's imported
    from firestore_schema.gateway import async_gateway
    
    monkeypatch.setattr(
        async_gateway,
        'AsyncAggregationQuery',
        MockAsyncAggregationQuery
    )

# 3. Test Cases
@pytest.mark.asyncio
async def test_get_document_found(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test that `get` returns a validated model when a document is found."""
    # Arrange: Add data to the mock Firestore
    doc_path = "users/test_user"
    doc_data = {"name": "Test User", "age": 30}
    await mock_client.collection("users").document("test_user").set(doc_data)

    # Act: Call the get method
    user = await gateway.get(doc_path, AsyncUserDocument)

    # Assert: Check that the returned object has the expected data
    assert user is not None
    assert user.name == "Test User"
    assert user.age == 30

@pytest.mark.asyncio
async def test_get_document_not_found(gateway: AsyncFirestoreGateway):
    """Test that `get` returns None when a document is not found."""
    # Arrange: The document does not exist
    doc_path = "users/non_existent_user"

    # Act: Call the get method
    user = await gateway.get(doc_path, AsyncUserDocument)

    # Assert: Check that the result is None
    assert user is None

@pytest.mark.asyncio
async def test_document_exists(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test that `exists` returns True for a document that exists."""
    # Arrange: Add data to the mock Firestore
    doc_path = "users/test_user"
    doc_data = {"name": "Test User", "age": 30}
    await mock_client.collection("users").document("test_user").set(doc_data)

    # Act: Call the exists method
    result = await gateway.exists(doc_path, model_class=AsyncUserDocument)

    # Assert: Check that the result is True
    assert result is True

@pytest.mark.asyncio
async def test_document_does_not_exist(gateway: AsyncFirestoreGateway):
    """Test that `exists` returns False for a document that does not exist."""
    # Arrange: The document does not exist
    doc_path = "users/non_existent_user"

    # Act: Call the exists method
    result = await gateway.exists(doc_path, model_class=AsyncUserDocument)

    # Assert: Check that the result is False
    assert result is False

@pytest.mark.asyncio
async def test_get_direct_document_found(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test that `get_direct` returns a model when a document is found, without a transaction."""
    # Arrange
    doc_path = "users/test_user_direct"
    doc_data = {"name": "Test User Direct", "age": 31}
    await mock_client.collection("users").document("test_user_direct").set(doc_data)

    # Act
    user = await gateway.get_direct(doc_path, AsyncUserDocument)

    # Assert
    assert user is not None
    assert user.name == "Test User Direct"
    assert user.age == 31

@pytest.mark.asyncio
async def test_get_direct_document_not_found(gateway: AsyncFirestoreGateway):
    """Test that `get_direct` returns None when a document is not found."""
    # Arrange
    doc_path = "users/non_existent_user_direct"

    # Act
    user = await gateway.get_direct(doc_path, AsyncUserDocument)

    # Assert
    assert user is None

@pytest.mark.asyncio
async def test_document_exists_direct(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test that `exists_direct` returns True for an existing document."""
    # Arrange
    doc_path = "users/test_user_direct_exists"
    doc_data = {"name": "Test User", "age": 30}
    await mock_client.collection("users").document("test_user_direct_exists").set(doc_data)

    # Act
    result = await gateway.exists_direct(doc_path)

    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_document_does_not_exist_direct(gateway: AsyncFirestoreGateway):
    """Test that `exists_direct` returns False for a non-existent document."""
    # Arrange
    doc_path = "users/non_existent_user_direct_exists"

    # Act
    result = await gateway.exists_direct(doc_path)

    # Assert
    assert result is False

# 4. Tests for Async Transactional CRUD Methods

@pytest.mark.asyncio
async def test_create_success(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test successful document creation asynchronously."""
    # Arrange
    doc_path = "users/new_user"
    new_user_data = {"name": "New User", "age": 25}

    # Act
    created_user = await gateway.create(doc_path, AsyncUserDocument, new_user_data)

    # Assert
    assert created_user is not None
    assert created_user.name == "New User"
    # Verify data in mock client
    snapshot = await mock_client.collection("users").document("new_user").get()
    assert snapshot.exists
    stored_data = snapshot.to_dict()
    assert stored_data is not None
    assert stored_data["name"] == "New User"

@pytest.mark.asyncio
async def test_create_document_already_exists(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test that create raises DocumentAlreadyExistsError if the document exists."""
    # Arrange
    doc_path = "users/existing_user"
    await mock_client.collection("users").document("existing_user").set({"name": "Exists", "age": 99})

    # Act & Assert
    with pytest.raises(DocumentAlreadyExistsError):
        await gateway.create(doc_path, AsyncUserDocument, {"name": "Should Fail", "age": 100})

@pytest.mark.asyncio
async def test_set_new_document(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test that `set` creates a new document asynchronously."""
    # Arrange
    doc_path = "users/set_user"
    user_data = {"name": "Set User", "age": 40}

    # Act
    await gateway.set(doc_path, AsyncUserDocument, user_data)

    # Assert
    snapshot = await mock_client.collection("users").document("set_user").get()
    assert snapshot.exists
    stored_data = snapshot.to_dict()
    assert stored_data is not None
    assert stored_data["age"] == 40

@pytest.mark.asyncio
async def test_set_overwrite_document(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test that `set` overwrites an existing document asynchronously."""
    # Arrange
    doc_path = "users/overwrite_user"
    await mock_client.collection("users").document("overwrite_user").set({"name": "Original", "age": 50})
    new_data = {"name": "Overwritten", "age": 51}

    # Act
    await gateway.set(doc_path, AsyncUserDocument, new_data)

    # Assert
    snapshot = await mock_client.collection("users").document("overwrite_user").get()
    assert snapshot.exists
    stored_data = snapshot.to_dict()
    assert stored_data is not None
    assert stored_data["name"] == "Overwritten"

@pytest.mark.asyncio
async def test_set_merge_document(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test that `set` with merge=True updates fields asynchronously."""
    # Arrange
    doc_path = "users/merge_user"
    await mock_client.collection("users").document("merge_user").set({"name": "Original", "age": 60, "email": "original@test.com"})
    new_data = {"age": 61, "email": "merged@test.com"}

    # Act
    await gateway.set(doc_path, AsyncUserDocument, new_data, merge=True)

    # Assert
    snapshot = await mock_client.collection("users").document("merge_user").get()
    assert snapshot.exists
    stored_data = snapshot.to_dict()
    assert stored_data is not None
    assert stored_data["name"] == "Original"
    assert stored_data["age"] == 61

@pytest.mark.asyncio
async def test_update_success(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test successful document update asynchronously."""
    # Arrange
    doc_path = "users/update_user"
    await mock_client.collection("users").document("update_user").set({"name": "Initial", "age": 70})
    update_data = {"age": 71, "email": "updated@test.com"}

    # Act
    updated_user = await gateway.update(doc_path, AsyncUserDocument, update_data)

    # Assert
    assert updated_user.age == 71
    snapshot = await mock_client.collection("users").document("update_user").get()
    assert snapshot.exists
    stored_data = snapshot.to_dict()
    assert stored_data is not None
    assert stored_data["age"] == 71

@pytest.mark.asyncio
async def test_update_document_not_found(gateway: AsyncFirestoreGateway):
    """Test that update raises DocumentNotFoundError if the document does not exist."""
    # Arrange
    doc_path = "users/non_existent_for_update"

    # Act & Assert
    with pytest.raises(DocumentNotFoundError):
        await gateway.update(doc_path, AsyncUserDocument, {"name": "Alice", "age": 30})

@pytest.mark.asyncio
async def test_delete_success(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test successful document deletion asynchronously."""
    # Arrange
    doc_path = "users/delete_user"
    await mock_client.collection("users").document("delete_user").set({"name": "Delete Me", "age": 99})

    # Act
    await gateway.delete(doc_path, model_class=AsyncUserDocument)

    # Assert
    snapshot = await mock_client.collection("users").document("delete_user").get()
    assert not snapshot.exists

@pytest.mark.asyncio
async def test_delete_document_not_found(gateway: AsyncFirestoreGateway):
    """Test that delete raises DocumentNotFoundError if the document does not exist."""
    # Arrange
    doc_path = "users/non_existent_for_delete"

    # Act & Assert
    with pytest.raises(DocumentNotFoundError):
        await gateway.delete(doc_path, model_class=AsyncUserDocument)


# 5. Tests for Async Batch Writer

@pytest.mark.asyncio
async def test_async_batch_writer_success(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test that the async batch writer successfully commits all operations."""
    # Arrange: Prepare existing data
    await mock_client.collection("users").document("update_me").set({"name": "Initial", "age": 10})
    await mock_client.collection("users").document("delete_me").set({"name": "Delete", "age": 20})

    # Act: Perform batch operations
    async with gateway.batch() as batch:
        batch.create("users/create_me", {"name": "Created", "age": 30})
        batch.update("users/update_me", {"age": 11})
        batch.delete("users/delete_me")

    # Assert: Verify the results
    created_doc = await mock_client.collection("users").document("create_me").get()
    assert created_doc.exists
    created_data = created_doc.to_dict()
    assert created_data is not None
    assert created_data["age"] == 30

    updated_doc = await mock_client.collection("users").document("update_me").get()
    assert updated_doc.exists
    updated_data = updated_doc.to_dict()
    assert updated_data is not None
    assert updated_data["age"] == 11

    deleted_doc = await mock_client.collection("users").document("delete_me").get()
    assert not deleted_doc.exists

@pytest.mark.asyncio
async def test_async_batch_writer_failure_rolls_back(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test that the async batch writer rolls back operations on failure."""
    # Arrange: Prepare existing data
    await mock_client.collection("users").document("dont_update").set({"name": "Initial", "age": 50})

    # Act & Assert: An exception within the 'async with' block should prevent any commits
    with pytest.raises(ValueError, match="Test error"):
        async with gateway.batch() as batch:
            batch.create("users/dont_create", {"name": "Created", "age": 60})
            batch.update("users/dont_update", {"age": 51})
            raise ValueError("Test error")

    # Assert: Verify that no changes were committed
    created_doc = await mock_client.collection("users").document("dont_create").get()
    assert not created_doc.exists
    updated_doc = await mock_client.collection("users").document("dont_update").get()
    assert updated_doc.exists
    updated_data = updated_doc.to_dict()
    assert updated_data is not None
    assert updated_data['age'] == 50  # Age should remain unchanged


# 6. Tests for Async Query Builder

@pytest.mark.asyncio
async def test_async_query_with_where_clause(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test async querying with a 'where' clause."""
    # Arrange
    await mock_client.collection("users").document("user1").set({"name": "Alice", "age": 30})
    await mock_client.collection("users").document("user2").set({"name": "Bob", "age": 30})
    await mock_client.collection("users").document("user3").set({"name": "Charlie", "age": 35})

    # Act
    results = await gateway.query(users_collection).where("age", "==", 30).get()

    # Assert
    assert isinstance(results, list)
    assert len(results) == 2
    assert {user.name for user in results} == {"Alice", "Bob"}

@pytest.mark.asyncio
async def test_async_query_with_order_by_and_limit(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test async querying with 'order_by' and 'limit' clauses."""
    # Arrange
    await mock_client.collection("users").document("user1").set({"name": "Alice", "age": 30})
    await mock_client.collection("users").document("user2").set({"name": "Bob", "age": 25})
    await mock_client.collection("users").document("user3").set({"name": "Charlie", "age": 35})

    # Act
    results = await gateway.query(users_collection).order_by("age").limit(2).get()

    # Assert
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0].name == "Bob"
    assert results[1].name == "Alice"

@pytest.mark.asyncio
async def test_async_query_get_one(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient):
    """Test fetching a single document with 'get_one'."""
    # Arrange
    await mock_client.collection("users").document("user1").set({"name": "Alice", "age": 30})
    await mock_client.collection("users").document("user2").set({"name": "Bob", "age": 25})

    # Act
    result = await gateway.query(users_collection).where("name", "==", "Alice").get_one()

    # Assert
    assert result is not None
    assert result.name == "Alice"

@pytest.mark.asyncio
async def test_async_query_get_one_not_found(gateway: AsyncFirestoreGateway):
    """Test 'get_one' when no document matches."""
    # Act
    result = await gateway.query(users_collection).where("name", "==", "NonExistent").get_one()

    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_async_query_aggregation_count(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient, mock_async_aggregation):
    """Test async query aggregation for count."""
    # Arrange
    await mock_client.collection("users").document("user1").set({"name": "Alice", "age": 30})
    await mock_client.collection("users").document("user2").set({"name": "Bob", "age": 30})
    await mock_client.collection("users").document("user3").set({"name": "Charlie", "age": 35})

    # Act
    result = await gateway.query(users_collection).count(alias="total").get()

    # Assert
    assert isinstance(result, dict)
    assert result["total"] == 3

@pytest.mark.asyncio
async def test_async_query_aggregation_sum_and_avg(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient, mock_async_aggregation):
    """Test async query aggregation for sum and average."""
    # Arrange
    await mock_client.collection("users").document("user1").set({"name": "Alice", "age": 25})
    await mock_client.collection("users").document("user2").set({"name": "Bob", "age": 30})
    await mock_client.collection("users").document("user3").set({"name": "Charlie", "age": 30})
    await mock_client.collection("users").document("user4").set({"name": "David", "age": 35})

    # Act
    result = await gateway.query(users_collection).sum("age", alias="total_age").avg("age", alias="avg_age").get()

    # Assert
    assert isinstance(result, dict)
    assert result["total_age"] == 120
    assert result["avg_age"] == 30

@pytest.mark.asyncio
async def test_async_query_aggregation_empty_result(gateway: AsyncFirestoreGateway, mock_client: AsyncMockFirestoreClient, mock_async_aggregation):
    """Test that aggregation returns zero values for an empty query result."""
    # Act: Test count on a query with no results
    result_count = await gateway.query(users_collection).where("age", ">", 99).count(alias="total").get()

    # Assert
    assert isinstance(result_count, dict)
    assert result_count["total"] == 0

    # Act: Test sum and avg on a query with no results
    result_sum_avg = await gateway.query(users_collection).where("age", ">", 99).sum("age", alias="total_age").avg("age", alias="avg_age").get()

    # Assert
    assert isinstance(result_sum_avg, dict)
    assert result_sum_avg["total_age"] == 0
    assert result_sum_avg["avg_age"] == 0

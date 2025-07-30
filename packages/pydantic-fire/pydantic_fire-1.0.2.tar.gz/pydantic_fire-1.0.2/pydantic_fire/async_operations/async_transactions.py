"""
Asynchronous Transaction and Batch Operation Management for Firestore

This module provides the core low-level components for managing atomic and
bulk write operations in Firestore. It is the "engine" that powers the
higher-level abstractions found in `async_decorators.py`.

Core Components:
- AsyncTransactionManager: The primary orchestrator for Firestore transactions.
  It handles the entire lifecycle: starting a transaction, managing automatic
  retries with exponential backoff on contention, and committing or rolling
  back the transaction.

- AsyncTransactionContext: A wrapper around the raw Google Firestore transaction.
  When a function is decorated with `@async_transactional`, an instance of this
  class is injected as the `transaction` argument. Its methods MUST be used to
  perform operations within the transaction.

- AsyncBatchBuilder: A tool for performing a large number of write operations
  (create, set, update, delete) efficiently in a single request. This is NOT
  a standard transaction, as it cannot include read operations.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, List, AsyncGenerator, cast
from datetime import datetime
from contextlib import asynccontextmanager
from dataclasses import dataclass

from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.async_transaction import AsyncTransaction
from google.cloud.firestore_v1.base_transaction import BaseTransaction
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.api_core import exceptions as google_exceptions

from ..core.exceptions import TransactionError, TransactionConflictError
from ..gateway.exceptions import DocumentNotFoundError, DocumentAlreadyExistsError



@dataclass
class AsyncTransactionConfig:
    """Configuration for async transactions."""
    max_retries: int = 3
    backoff_multiplier: float = 2.0
    max_backoff: float = 60.0
    log_operations: bool = True

class AsyncTransactionContext(BaseTransaction):
    """Wraps the Firestore AsyncTransaction to provide logging and context."""
    
    def __init__(self, transaction: AsyncTransaction, config: AsyncTransactionConfig,
                 transaction_id: str, logger: logging.Logger):

        self._transaction = transaction
        self._config = config
        self._transaction_id = transaction_id
        self._logger = logger
        self._operations: List[Dict[str, Any]] = []
        self._start_time = datetime.utcnow()

    @property
    def _id(self) -> bytes:
        return self._transaction._id

    @property
    def in_progress(self) -> bool:
        return self._transaction.in_progress

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def create(self, doc_ref, data: Dict[str, Any]) -> None:
        try:
            self._transaction.create(doc_ref, data)
            if self._config.log_operations:
                self._logger.info(f"TXN({self._transaction_id}): CREATE {doc_ref.path}")
        except Exception as e:
            self._logger.error(f"TXN({self._transaction_id}): CREATE failed on {doc_ref.path}: {e}")
            raise TransactionError(f"Transaction create failed: {e}") from e

    async def set(self, doc_ref, data: Dict[str, Any], merge: bool = False) -> None:
        try:
            self._transaction.set(doc_ref, data, merge=merge)
            if self._config.log_operations:
                self._logger.info(f"TXN({self._transaction_id}): SET {doc_ref.path}")
        except Exception as e:
            self._logger.error(f"TXN({self._transaction_id}): SET failed on {doc_ref.path}: {e}")
            raise TransactionError(f"Transaction set failed: {e}") from e
    
    async def update(self, doc_ref, data: Dict[str, Any]) -> None:
        try:
            self._transaction.update(doc_ref, data)
            if self._config.log_operations:
                self._logger.info(f"TXN({self._transaction_id}): UPDATE {doc_ref.path}")
        except Exception as e:
            self._logger.error(f"TXN({self._transaction_id}): UPDATE failed on {doc_ref.path}: {e}")
            raise TransactionError(f"Transaction update failed: {e}") from e
    
    async def delete(self, doc_ref) -> None:
        try:
            self._transaction.delete(doc_ref)
            if self._config.log_operations:
                self._logger.info(f"TXN({self._transaction_id}): DELETE {doc_ref.path}")
        except Exception as e:
            self._logger.error(f"TXN({self._transaction_id}): DELETE failed on {doc_ref.path}: {e}")
            raise TransactionError(f"Transaction delete failed: {e}") from e

    async def query(self, query_ref) -> AsyncGenerator[DocumentSnapshot, None]:
        async for doc in query_ref.stream(transaction=self._transaction):
            yield doc

    async def get(self, doc_ref) -> Optional[Dict[str, Any]]:
        try:
            doc_snapshot = cast(DocumentSnapshot, await self._transaction.get(doc_ref))
            if self._config.log_operations:
                self._logger.info(f"TXN({self._transaction_id}): GET {doc_ref.path}")
            if doc_snapshot and doc_snapshot.exists:
                return doc_snapshot.to_dict()
            return None
        except Exception as e:
            self._logger.error(f"TXN({self._transaction_id}): GET failed on {doc_ref.path}: {e}")
            raise TransactionError(f"Transaction get failed: {e}") from e

class AsyncBatchBuilder:
    """Builds a batch of write operations to be executed atomically."""
    
    def __init__(self, batch_id: Optional[str] = None):
        self._batch_id = batch_id or f"batch_{uuid.uuid4().hex[:8]}"
        self._operations: List[Dict[str, Any]] = []
        self._logger = logging.getLogger(__name__)
        self._committed = False

    async def __aenter__(self) -> "AsyncBatchBuilder":
        self._committed = False
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and not self._committed:
            manager = get_async_transaction_manager()
            if not manager:
                raise TransactionError("AsyncTransactionManager not initialized. Cannot commit batch.")
            await self.execute(manager)
    
    def create(self, doc_ref, data: Dict[str, Any]) -> 'AsyncBatchBuilder':
        self._operations.append({'type': 'create', 'ref': doc_ref, 'data': data})
        return self

    def set(self, doc_ref, data: Dict[str, Any], merge: bool = False) -> 'AsyncBatchBuilder':
        self._operations.append({'type': 'set', 'ref': doc_ref, 'data': data, 'merge': merge})
        return self
    
    def update(self, doc_ref, data: Dict[str, Any]) -> 'AsyncBatchBuilder':
        self._operations.append({'type': 'update', 'ref': doc_ref, 'data': data})
        return self
    
    def delete(self, doc_ref) -> 'AsyncBatchBuilder':
        self._operations.append({'type': 'delete', 'ref': doc_ref, 'data': {}})
        return self
    
    async def execute(self, transaction_manager: "AsyncTransactionManager") -> Dict[str, Any]:
        if not self._operations:
            return {'status': 'success', 'message': 'No operations to execute'}
        
        try:
            await transaction_manager._execute_batch_operations(self._batch_id, self._operations)
            return {'status': 'success'}
        except Exception as e:
            self._logger.error(f"Batch {self._batch_id} failed: {e}")
            raise TransactionError(f"Batch execution failed: {e}") from e

class AsyncTransactionManager:
    """Manages the lifecycle of Firestore async transactions and batches."""
    
    def __init__(self, client: Optional[AsyncClient] = None, config: Optional[AsyncTransactionConfig] = None):
        self._client = client
        self._config = config or AsyncTransactionConfig()
        self._logger = logging.getLogger(__name__)

    def set_client(self, client: AsyncClient) -> None:
        self._client = client

    @asynccontextmanager
    async def transaction_context(self, config: Optional[AsyncTransactionConfig] = None):
        if not self._client:
            raise TransactionError("Async client not set in TransactionManager.")

        transaction_config = config or self._config
        transaction_id = f"txn_{uuid.uuid4().hex[:10]}"

        for attempt in range(transaction_config.max_retries + 1):
            try:
                async with self._client.transaction() as transaction:
                    self._logger.info(f"TXN({transaction_id}): Starting attempt {attempt + 1}")
                    tx_context = AsyncTransactionContext(
                        transaction=transaction,
                        config=transaction_config,
                        transaction_id=transaction_id,
                        logger=self._logger
                    )
                    yield tx_context
                
                self._logger.info(f"TXN({transaction_id}): Completed successfully.")
                return

            except google_exceptions.Aborted as e:
                self._logger.warning(f"TXN({transaction_id}): Conflict on attempt {attempt + 1}. Retrying...")
                if attempt < transaction_config.max_retries:
                    backoff_time = (transaction_config.backoff_multiplier ** attempt)
                    await asyncio.sleep(min(backoff_time, transaction_config.max_backoff))
                else:
                    self._logger.error(f"TXN({transaction_id}): Failed after max retries.")
                    raise TransactionConflictError(f"Transaction failed after {transaction_config.max_retries + 1} attempts.") from e
            except (DocumentNotFoundError, DocumentAlreadyExistsError) as e:
                # Allow expected exceptions to propagate
                raise
            except Exception as e:
                self._logger.error(f"TXN({transaction_id}): An unexpected error occurred: {e}")
                raise TransactionError(f"Transaction failed unexpectedly.") from e

    async def _execute_batch_operations(self, batch_id: str, operations: List[Dict[str, Any]]):
        if not self._client:
            raise TransactionError("Async client not set in TransactionManager.")

        batch = self._client.batch()
        self._logger.info(f"BATCH({batch_id}): Executing with {len(operations)} operations.")

        for op in operations:
            op_type, doc_ref, data = op['type'], op['ref'], op['data']
            
            # Convert string document paths to actual document references
            if isinstance(doc_ref, str):
                # Parse the document path to extract collection and document ID
                path_parts = doc_ref.split('/')
                if len(path_parts) >= 2:
                    collection_name = path_parts[0]
                    document_id = path_parts[1]
                    doc_ref = self._client.collection(collection_name).document(document_id)
                else:
                    raise TransactionError(f"Invalid document path: {doc_ref}")
            
            if op_type == 'create':
                # Firestore batch does not have 'create', so we use 'set' which achieves the same goal.
                batch.set(doc_ref, data)
            elif op_type == 'set':
                batch.set(doc_ref, data, merge=op.get('merge', False))
            elif op_type == 'update':
                batch.update(doc_ref, data)
            elif op_type == 'delete':
                batch.delete(doc_ref)
        
        await batch.commit()
        self._logger.info(f"BATCH({batch_id}): Committed successfully.")

# --- Global Instance Management ---

_global_async_transaction_manager: Optional[AsyncTransactionManager] = None

def initialize_async_transaction_manager(client: AsyncClient, config: Optional[AsyncTransactionConfig] = None) -> None:
    """Initializes the global async transaction manager."""
    global _global_async_transaction_manager
    if _global_async_transaction_manager is None:
        _global_async_transaction_manager = AsyncTransactionManager(client, config)
        logging.info("Global AsyncTransactionManager initialized.")

def get_async_transaction_manager() -> Optional[AsyncTransactionManager]:
    """Gets the global async transaction manager instance."""
    return _global_async_transaction_manager

def create_async_batch_builder(batch_id: Optional[str] = None) -> AsyncBatchBuilder:
    """Creates a new async batch builder."""
    return AsyncBatchBuilder(batch_id)

def clear_global_async_transaction_manager() -> None:
    """Clears the global async transaction manager instance. For testing purposes."""
    global _global_async_transaction_manager
    _global_async_transaction_manager = None
    logging.info("Global AsyncTransactionManager cleared.")

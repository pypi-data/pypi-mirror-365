"""
Transaction management utilities for Firestore operations.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional, Type, Callable, TypeVar
from functools import wraps
from datetime import datetime
import logging
from contextlib import contextmanager

from google.api_core.exceptions import Aborted
from google.cloud.exceptions import Conflict, InternalServerError, ServiceUnavailable

from ..core.base import Document, Collection
from ..core.exceptions import SchemaError, ValidationError
from ..gateway.exceptions import DocumentAlreadyExistsError, DocumentNotFoundError


# Type variable for transaction functions
T = TypeVar('T')


class TransactionManager:
    """
    Manager for Firestore transactions with schema validation.
    """
    
    def __init__(self, client: Any = None):
        """
        Initialize transaction manager.
        
        Args:
            client: Firestore client instance
        """
        self._client = client
        self._logger = logging.getLogger(__name__)
        self._transaction_history = []
    
    def set_client(self, client: Any) -> None:
        """
        Set the Firestore client.
        
        Args:
            client: Firestore client instance
        """
        self._client = client
    
    @staticmethod
    def transactional(
        max_retries: int = 3,
        log_operations: bool = True
    ) -> Callable:
        """
        Decorator for transactional operations with schema validation.
        
        Args:
            max_retries: Maximum number of retry attempts
            log_operations: Whether to log transaction operations
        
        Returns:
            Decorated function that runs in a transaction
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                # Get transaction manager instance
                manager = kwargs.get('transaction_manager')
                if not manager:
                    # Try to get from first argument if it's a class instance
                    if args and hasattr(args[0], '_transaction_manager'):
                        manager = args[0]._transaction_manager
                    else:
                        # Create default manager
                        manager = TransactionManager()
                
                return manager._execute_transaction(
                    func, args, kwargs, max_retries=max_retries, log_operations=log_operations
                )
            
            return wrapper
        return decorator
    
    def run(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Runs a function within a transaction, handling retries and context."""
        return self._execute_transaction(
            func,
            args=args,
            kwargs=kwargs,
            max_retries=3, # Default retries
            log_operations=True
        )
    
    def _execute_transaction(self,
                           func: Callable,
                           args: tuple,
                           kwargs: dict,
                           max_retries: int,
                           log_operations: bool) -> Any:
        """Execute function within a transaction with retries."""
        if not self._client:
            raise SchemaError("No Firestore client configured for transaction")
        
        transaction_id = f"txn_{int(datetime.now().timestamp() * 1000)}"
        
        if log_operations:
            self._logger.info(f"Starting transaction {transaction_id}")
        
        # Record transaction start
        transaction_record = {
            'id': transaction_id,
            'function': func.__name__,
            'started_at': datetime.now(),
            'attempts': 0,
            'operations': [],
            'status': 'started'
        }
        
        for attempt in range(max_retries + 1):
            transaction_record['attempts'] = attempt + 1
            
            try:
                if hasattr(self._client, 'transaction'):
                    # Use real Firestore transaction
                    transaction = self._client.transaction()

                    with transaction:
                        # Create transaction context
                        tx_context = TransactionContext(
                            transaction, log_operations, transaction_record
                        )

                        # Execute function with transaction context
                        result = func(*args, transaction=tx_context, **kwargs)

                        transaction_record['status'] = 'committed'
                        transaction_record['completed_at'] = datetime.now()

                        if log_operations:
                            self._logger.info(f"Transaction {transaction_id} committed successfully")

                        self._transaction_history.append(transaction_record)
                        return result

                else:
                    # Use mock transaction for testing
                    tx_context = TransactionContext(
                        None, log_operations, transaction_record
                    )

                    result = func(*args, transaction=tx_context, **kwargs)

                    transaction_record['status'] = 'committed'
                    transaction_record['completed_at'] = datetime.now()

                    self._transaction_history.append(transaction_record)
                    return result

            except (Aborted, Conflict, InternalServerError, ServiceUnavailable) as e:
                # These are transient errors that can be retried
                transaction_record['status'] = 'retrying'
                transaction_record['error'] = str(e)
                if log_operations:
                    self._logger.warning(f"Transaction {transaction_id} attempt {attempt + 1} failed with transient error, retrying: {e}")
                if attempt == max_retries:
                    transaction_record['status'] = 'aborted'
                    self._transaction_history.append(transaction_record)
                    if log_operations:
                        self._logger.error(f"Transaction {transaction_id} aborted after {max_retries + 1} attempts due to transient errors.")
                    raise SchemaError(f"Transaction failed after {max_retries + 1} attempts: {e}") from e

            except (DocumentNotFoundError, DocumentAlreadyExistsError) as e:
                # These are application-level errors that should not be retried.
                transaction_record['status'] = 'failed'
                transaction_record['error'] = str(e)
                transaction_record['failed_at'] = datetime.now()
                self._transaction_history.append(transaction_record)
                if log_operations:
                    self._logger.error(f"Transaction {transaction_id} failed with non-retriable error: {e}")
                raise  # Re-raise immediately

            except Exception as e:
                # Catch any other unexpected errors
                transaction_record['status'] = 'failed'
                transaction_record['error'] = str(e)
                transaction_record['failed_at'] = datetime.now()
                self._transaction_history.append(transaction_record)
                if log_operations:
                    self._logger.error(f"Transaction {transaction_id} failed with unexpected error: {e}", exc_info=True)
                raise SchemaError(f"An unexpected error occurred in transaction: {e}") from e
        
        # Should never reach here
        raise SchemaError("Unexpected transaction execution path")
    
    def batch_write(self, operations: List[Dict[str, Any]]) -> None:
        """
        Execute batch write operations.
        
        Args:
            operations: List of operation dictionaries
                       Each dict should have: {'type': 'set'|'update'|'delete', 'ref': doc_ref, 'data': data}
        """
        if not self._client:
            raise SchemaError("No Firestore client configured for batch write")
        
        batch_id = f"batch_{int(datetime.now().timestamp() * 1000)}"
        self._logger.info(f"Starting batch write {batch_id} with {len(operations)} operations")
        
        try:
            if hasattr(self._client, 'batch'):
                # Use real Firestore batch
                batch = self._client.batch()
                
                for operation in operations:
                    op_type = operation.get('type')
                    doc_ref = operation.get('ref')
                    data = operation.get('data', {})
                    
                    if op_type == 'set':
                        merge = operation.get('merge', False)
                        batch.set(doc_ref, data, merge=merge)
                    elif op_type == 'update':
                        batch.update(doc_ref, data)
                    elif op_type == 'delete':
                        batch.delete(doc_ref)
                    else:
                        raise ValueError(f"Unknown operation type: {op_type}")
                
                # Commit batch
                batch.commit()
                self._logger.info(f"Batch write {batch_id} committed successfully")
                
            else:
                # Mock batch for testing
                for operation in operations:
                    op_type = operation.get('type')
                    doc_ref = operation.get('ref')
                    data = operation.get('data', {})
                    
                    if op_type == 'set' and doc_ref:
                        merge = operation.get('merge', False)
                        doc_ref.set(data, merge=merge)
                    elif op_type == 'update' and doc_ref:
                        doc_ref.update(data)
                    elif op_type == 'delete' and doc_ref:
                        doc_ref.delete()
                
                self._logger.info(f"Mock batch write {batch_id} completed")
                
        except Exception as e:
            self._logger.error(f"Batch write {batch_id} failed: {e}")
            raise SchemaError(f"Batch write failed: {e}")
    
    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """
        Get history of all transactions.
        
        Returns:
            List of transaction records
        """
        return self._transaction_history.copy()
    
    def clear_transaction_history(self) -> None:
        """Clear transaction history."""
        self._transaction_history.clear()
    
    @contextmanager
    def transaction_context(self, 
                          log_operations: bool = True):
        """
        Context manager for manual transaction handling.
        
        Args:
            validate_schema: Whether to validate against schema
            log_operations: Whether to log operations
        
        Yields:
            TransactionContext instance
        """
        if not self._client:
            raise SchemaError("No Firestore client configured for transaction")
        
        transaction_id = f"ctx_{int(datetime.now().timestamp() * 1000)}"
        
        transaction_record = {
            'id': transaction_id,
            'function': 'context_manager',
            'started_at': datetime.now(),
            'attempts': 1,
            'operations': [],
            'status': 'started'
        }
        
        try:
            if hasattr(self._client, 'transaction'):
                transaction = self._client.transaction()
                
                with transaction:
                    tx_context = TransactionContext(
                        transaction, log_operations, transaction_record
                    )
                    
                    yield tx_context
                    
                    transaction_record['status'] = 'committed'
                    transaction_record['completed_at'] = datetime.now()
            else:
                # Mock transaction
                tx_context = TransactionContext(
                    None, log_operations, transaction_record
                )
                
                yield tx_context
                
                transaction_record['status'] = 'committed'
                transaction_record['completed_at'] = datetime.now()
            
            self._transaction_history.append(transaction_record)
            
        except Exception as e:
            transaction_record['status'] = 'failed'
            transaction_record['error'] = str(e)
            transaction_record['failed_at'] = datetime.now()
            self._transaction_history.append(transaction_record)
            raise


class TransactionContext:
    """
    Context for transaction operations.
    """
    
    def __init__(self, 
                 transaction: Any,
                 log_operations: bool = True,
                 transaction_record: Optional[Dict] = None):
        """
        Initialize transaction context.
        
        Args:
            transaction: Firestore transaction instance
            log_operations: Whether to log operations
            transaction_record: Transaction record for logging
        """
        self._transaction = transaction
        self._log_operations = log_operations
        self._transaction_record = transaction_record or {}
        self._logger = logging.getLogger(__name__)
    
    def get(self, doc_ref: Any) -> Any:
        """
        Get document within transaction.
        
        Args:
            doc_ref: Document reference
        
        Returns:
            Document snapshot
        """
        self._log_operation('get', doc_ref)
        
        if self._transaction:
            return self._transaction.get(doc_ref)
        else:
            # Mock transaction
            return doc_ref.get()
    
    def set(self, 
            doc_ref: Any, 
            data: Dict[str, Any], 
            merge: bool = False) -> None:
        """
        Set document within transaction.
        
        Args:
            doc_ref: Document reference
            data: Document data
            merge: Whether to merge with existing data
        """
        self._log_operation('set', doc_ref, data={'merge': merge})
        
        if self._transaction:
            self._transaction.set(doc_ref, data, merge=merge)
        else:
            # Mock transaction
            doc_ref.set(data, merge=merge)
    
    def update(self, 
               doc_ref: Any, 
               field_updates: Dict[str, Any]) -> None:
        """
        Update document within transaction.
        
        Args:
            doc_ref: Document reference
            field_updates: Fields to update
        """
        self._log_operation('update', doc_ref)
        
        if self._transaction:
            self._transaction.update(doc_ref, field_updates)
        else:
            # Mock transaction
            doc_ref.update(field_updates)
    
    def delete(self, doc_ref: Any) -> None:
        """
        Delete document within transaction.
        
        Args:
            doc_ref: Document reference
        """
        self._log_operation('delete', doc_ref)
        
        if self._transaction:
            self._transaction.delete(doc_ref)
        else:
            # Mock transaction
            doc_ref.delete()
    
    def _log_operation(self, operation: str, doc_ref: Any, data: Optional[Dict] = None) -> None:
        """Log transaction operation."""
        if self._log_operations:
            operation_record = {
                'operation': operation,
                'document_path': getattr(doc_ref, 'path', str(doc_ref)),
                'timestamp': datetime.now(),
                'data': data
            }
            
            self._transaction_record.setdefault('operations', []).append(operation_record)
            
            self._logger.debug(f"Transaction operation: {operation} on {operation_record['document_path']}")


class BatchOperationBuilder:
    """
    Builder for constructing batch operations.
    """
    
    def __init__(self):
        """Initialize batch operation builder."""
        self._operations = []
    
    def set(self, doc_ref: Any, data: Dict[str, Any], merge: bool = False) -> BatchOperationBuilder:
        """
        Add set operation to batch.
        
        Args:
            doc_ref: Document reference
            data: Document data
            merge: Whether to merge with existing data
        
        Returns:
            Self for method chaining
        """
        self._operations.append({
            'type': 'set',
            'ref': doc_ref,
            'data': data,
            'merge': merge
        })
        return self
    
    def update(self, doc_ref: Any, field_updates: Dict[str, Any]) -> BatchOperationBuilder:
        """
        Add update operation to batch.
        
        Args:
            doc_ref: Document reference
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
    
    def delete(self, doc_ref: Any) -> BatchOperationBuilder:
        """
        Add delete operation to batch.
        
        Args:
            doc_ref: Document reference
        
        Returns:
            Self for method chaining
        """
        self._operations.append({
            'type': 'delete',
            'ref': doc_ref
        })
        return self
    
    def build(self) -> List[Dict[str, Any]]:
        """
        Build the list of operations.
        
        Returns:
            List of operation dictionaries
        """
        return self._operations.copy()
    
    def execute(self, transaction_manager: TransactionManager) -> None:
        """
        Execute the batch operations.
        
        Args:
            transaction_manager: Transaction manager to execute with
        """
        transaction_manager.batch_write(self._operations)


# Global transaction manager instance
_global_transaction_manager = TransactionManager()


def set_global_client(client: Any) -> None:
    """
    Set the global Firestore client for transactions.
    
    Args:
        client: Firestore client instance
    """
    _global_transaction_manager.set_client(client)


def get_transaction_manager() -> TransactionManager:
    """
    Get the global transaction manager.
    
    Returns:
        Global TransactionManager instance
    """
    return _global_transaction_manager


def create_transaction_manager(client: Any = None) -> TransactionManager:
    """
    Factory function to create a transaction manager.
    
    Args:
        client: Firestore client instance
    
    Returns:
        Configured TransactionManager instance
    """
    return TransactionManager(client)


def create_batch_builder() -> BatchOperationBuilder:
    """
    Factory function to create a batch operation builder.
    
    Returns:
        New BatchOperationBuilder instance
    """
    return BatchOperationBuilder()

"""
A Python package for defining a type-safe, dynamic, and maintainable Firestore schema.
"""

from .core.base import Document, Collection, DocumentType, SubcollectionType
from .core.fields import Field, PydanticField
from .schema_manager import FirestoreSchema
# Phase 2: Advanced Features
from .utils.rules_generator import FirestoreRulesGenerator, create_rules_generator
from .utils.introspection import SchemaIntrospector, create_schema_introspector
from .utils.visualization import SchemaVisualizer, create_schema_visualizer
from .utils.docs_generator import DocsGenerator, create_docs_generator
# Phase 3: Performance & Integration
from .utils.emulator import FirestoreEmulator, EmulatorTestSuite, create_emulator, create_test_suite
from .sync_operations.transactions import TransactionManager, TransactionContext, BatchOperationBuilder, create_transaction_manager, create_batch_builder, get_transaction_manager, set_global_client
from .sync_operations.decorators import transactional, retry_on_conflict, log_operations, cache_result, measure_performance, firestore_operation
from .gateway.sync_gateway import FirestoreGateway

# Phase 4: Async Support & Distribution
from .async_operations.async_base import AsyncDocument
from .async_operations.async_transactions import AsyncTransactionManager, AsyncTransactionConfig, AsyncTransactionContext, AsyncBatchBuilder, create_async_batch_builder, get_async_transaction_manager
from .async_operations.async_decorators import async_transactional, async_retry_on_conflict, async_log_operations, async_cache_result, async_measure_performance, async_firestore_operation
from .gateway.async_gateway import AsyncFirestoreGateway

from .common.decorators import DEFAULT_RETRYABLE_EXCEPTIONS, performance_monitor, operation_logger, retry_logic_generator

__all__ = [
    # Core components
    "Document",
    "Collection",
    "DocumentType",
    "SubcollectionType",
    "Field",
    "PydanticField",
    "FirestoreSchema",
    # Phase 2: Advanced Features
    "FirestoreRulesGenerator",
    "create_rules_generator",
    "SchemaIntrospector",
    "create_schema_introspector",
    "SchemaVisualizer",
    "create_schema_visualizer",
    "DocsGenerator",
    "create_docs_generator",
    # Phase 3: Performance & Integration
    "FirestoreEmulator",
    "EmulatorTestSuite",
    "create_emulator",
    "create_test_suite",
    "TransactionManager",
    "TransactionContext",
    "BatchOperationBuilder",
    "create_transaction_manager",
    "create_batch_builder",
    "get_transaction_manager",
    "set_global_client",
    "transactional",
    "retry_on_conflict",
    "log_operations",
    "cache_result",
    "measure_performance",
    "firestore_operation",
    "FirestoreGateway",
    # Phase 4: Async Support & Distribution
    "AsyncDocument",

    "AsyncTransactionManager",
    "AsyncTransactionConfig",
    "AsyncTransactionContext",
    "AsyncBatchBuilder",
    "create_async_batch_builder",
    "get_async_transaction_manager",
    "async_transactional",
    "async_retry_on_conflict",
    "async_log_operations",
    "async_cache_result",
    "async_measure_performance",
    "async_firestore_operation",
    "AsyncFirestoreGateway",
    "DEFAULT_RETRYABLE_EXCEPTIONS",
    "performance_monitor",
    "operation_logger",
    "retry_logic_generator",
]

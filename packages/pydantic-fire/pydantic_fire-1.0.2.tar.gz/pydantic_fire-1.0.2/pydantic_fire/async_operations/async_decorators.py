"""
Async decorators for Firestore operations.

Asynchronous Decorators for Firestore Operations

This module provides a suite of powerful asynchronous decorators designed to
augment Firestore operations with essential production-grade features like
transaction management, automatic retries, caching, and robust logging.

By applying these decorators to functions, you can cleanly separate cross-cutting
concerns from your core business logic, leading to more readable, maintainable,
and resilient code.

Key Decorators:
- @async_transactional: Wraps a function in a Firestore transaction, ensuring
  all operations within it are atomic. It automatically handles retries on
  contention errors, injecting an `AsyncTransactionContext` object into the
  decorated function. This is the primary bridge to the `async_transactions` module.

- @async_retry: A general-purpose retry decorator for any async function that
  might fail intermittently.

- @async_cache: Provides simple in-memory caching for function results to
  reduce redundant calls for non-volatile data.

- @async_log_operation: Logs function entry, exit, arguments, and execution
  time for debugging and performance monitoring.

How it fits with `async_transactions.py`:
This module is the primary consumer of the `AsyncTransactionManager` from
`async_transactions.py`. The `@async_transactional` decorator uses the global
transaction manager to start, commit, and roll back transactions. You do not
need to interact with the `AsyncTransactionManager` directly when using this
decorator.

Usage with Batch Operations:
Batch operations, managed by `AsyncBatchBuilder` in `async_transactions.py`,
are handled differently and are NOT typically used with these decorators.
A batch is built manually by chaining methods (`.create()`, `.set()`, etc.) and
then executed with a single call to `batch.execute(transaction_manager)`.
This pattern is for bulk data writes where the operations do not depend on
reads performed within the same transaction.
"""

import asyncio
import functools
import logging
import time
import hashlib
from typing import Dict, Any, Optional, Callable, TypeVar, Type, Awaitable, Tuple

from .async_transactions import AsyncTransactionConfig, get_async_transaction_manager
from ..core.exceptions import SchemaError
from ..common.decorators import DEFAULT_RETRYABLE_EXCEPTIONS, async_performance_monitor, async_operation_logger, retry_logic_generator

T = TypeVar('T')


def async_transactional(max_retries: int = 3, 
                       log_operations: bool = True,
                       backoff_multiplier: float = 2.0,
                       max_backoff: float = 60.0) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Async decorator for transactional operations with automatic retries.
    
    Args:
        max_retries: Maximum number of retry attempts
        log_operations: Whether to log transaction operations
        backoff_multiplier: Multiplier for exponential backoff
        max_backoff: Maximum backoff delay in seconds
        
    Returns:
        Decorated async function with transaction support
        
    Example:
        @async_transactional(max_retries=3)
        async def create_user(user_data, transaction=None):
            user_ref = firestore_client.collection('users').document(user_data['id'])
            await transaction.set(user_ref, user_data)
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get transaction manager
            tx_manager = get_async_transaction_manager()
            if not tx_manager:
                raise SchemaError("Async transaction manager not configured. Call initialize_async_transaction_manager() first.")
            
            # Create transaction config
            config = AsyncTransactionConfig(
                max_retries=max_retries,
                backoff_multiplier=backoff_multiplier,
                max_backoff=max_backoff,
                log_operations=log_operations
            )
            
            # Execute function within transaction
            async with tx_manager.transaction_context(config) as tx:
                # Inject transaction into kwargs if not provided
                if 'transaction' not in kwargs:
                    kwargs['transaction'] = tx
                
                return await func(*args, **kwargs)
        
        # Mark function as transactional for introspection
        setattr(wrapper, '_is_async_transactional', True)
        setattr(wrapper, '_async_transaction_config', {
            'max_retries': max_retries,
            'log_operations': log_operations,
            'backoff_multiplier': backoff_multiplier,
            'max_backoff': max_backoff
        })
        
        return wrapper
    return decorator





def async_retry_on_conflict(
    max_retries: int = 3,
    backoff_multiplier: float = 1.5,
    max_backoff: float = 60.0,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Async decorator to retry a function on specific, retryable exceptions.

    Args:
        max_retries: Maximum number of retry attempts.
        backoff_multiplier: Multiplier for exponential backoff.
        max_backoff: Maximum backoff time in seconds.
        retryable_exceptions: A tuple of exception types to retry on. 
                              Defaults to common Firestore conflict errors.

    Returns:
        Decorated async function with automatic retry on conflicts.
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            exceptions_to_retry = retryable_exceptions or DEFAULT_RETRYABLE_EXCEPTIONS
            retry_gen = retry_logic_generator(max_retries, backoff_multiplier, max_backoff)

            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions_to_retry as e:
                    last_exception = e
                    if attempt < max_retries:
                        backoff_time = next(retry_gen)
                        logger.warning(
                            f"Attempt {attempt + 1} for {func.__name__} failed with {e.__class__.__name__}. "
                            f"Retrying in {backoff_time:.2f}s..."
                        )
                        await asyncio.sleep(backoff_time)
                    else:
                        logger.error(f"Function {func.__name__} failed after {max_retries + 1} attempts.", exc_info=last_exception)
                        raise SchemaError(f"Function {func.__name__} exhausted all retries.") from last_exception
            
            # This path should not be reached, but is a safeguard.
            raise SchemaError(f"Function {func.__name__} failed unexpectedly.") from last_exception

        # Mark function as retryable for introspection
        setattr(wrapper, '_has_async_retry', True)
        setattr(wrapper, '_async_retry_config', {
            'max_retries': max_retries,
            'backoff_multiplier': backoff_multiplier,
            'max_backoff': max_backoff,
            'retryable_exceptions': retryable_exceptions or DEFAULT_RETRYABLE_EXCEPTIONS
        })
        return wrapper
    return decorator


def async_log_operations(log_level: int = logging.INFO,
                        include_args: bool = False,
                        include_result: bool = False,
                        logger_name: Optional[str] = None) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Async decorator for operation logging with performance metrics.

    Args:
        log_level: Logging level (e.g., logging.INFO, logging.DEBUG).
        include_args: Whether to include function arguments in logs.
        include_result: Whether to include function result in logs.
        logger_name: Custom logger name (defaults to function module).

    Returns:
        Decorated async function with logging.
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            
            async with async_operation_logger(logger, func.__name__, log_level, include_args, include_result, args, kwargs) as log_info:
                result = await func(*args, **kwargs)
                if include_result:
                    log_info['result'] = str(result)
                return result

        # Mark function as logged for introspection
        setattr(wrapper, '_has_async_logging', True)
        setattr(wrapper, '_async_logging_config', {
            'log_level': log_level,
            'include_args': include_args,
            'include_result': include_result,
            'logger_name': logger_name
        })
        return wrapper
    return decorator


def async_cache_result(ttl_seconds: int = 300,
                      cache_key_func: Optional[Callable] = None,
                      max_cache_size: int = 1000) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Async decorator for result caching with TTL and size limits.
    
    Args:
        ttl_seconds: Time-to-live for cached results in seconds
        cache_key_func: Custom function to generate cache keys
        max_cache_size: Maximum number of items in cache
        
    Returns:
        Decorated async function with caching
        
    Example:
        @async_cache_result(ttl_seconds=600)
        async def get_user_profile(user_id):
            # Results are cached for 10 minutes
            pass
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        cache: Dict[str, Dict[str, Any]] = {}
        
        def default_cache_key(*args, **kwargs) -> str:
            """Generate default cache key from function arguments."""
            key_data = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            return hashlib.md5(key_data.encode()).hexdigest()
        
        def cleanup_cache():
            """Remove expired entries from cache."""
            current_time = time.time()
            expired_keys = [
                key for key, value in cache.items()
                if current_time > value['expires_at']
            ]
            for key in expired_keys:
                del cache[key]
        
        def clear_cache():
            """Clear all cached results."""
            cache.clear()
        
        def get_cache_stats() -> Dict[str, Any]:
            """Get cache statistics."""
            cleanup_cache()
            return {
                'size': len(cache),
                'max_size': max_cache_size,
                'keys': list(cache.keys())
            }
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = default_cache_key(*args, **kwargs)
            
            # Check cache
            current_time = time.time()
            if cache_key in cache:
                cached_entry = cache[cache_key]
                if current_time <= cached_entry['expires_at']:
                    return cached_entry['result']
                else:
                    # Remove expired entry
                    del cache[cache_key]
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            if len(cache) >= max_cache_size:
                cleanup_cache()
                # If still at max size, remove oldest entry
                if len(cache) >= max_cache_size:
                    oldest_key = min(cache.keys(), key=lambda k: cache[k]['created_at'])
                    del cache[oldest_key]
            
            cache[cache_key] = {
                'result': result,
                'created_at': current_time,
                'expires_at': current_time + ttl_seconds
            }
            
            return result
        
        setattr(wrapper, 'clear_cache', clear_cache)
        setattr(wrapper, 'get_cache_stats', get_cache_stats)
        
        # Mark function as cached for introspection
        setattr(wrapper, '_has_async_caching', True)
        setattr(wrapper, '_async_caching_config', {
            'ttl_seconds': ttl_seconds,
            'cache_key_func': cache_key_func,
            'max_cache_size': max_cache_size
        })
        
        return wrapper
    return decorator


def async_measure_performance(threshold_seconds: float = 1.0,
                            log_slow_operations: bool = True) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Async decorator for performance monitoring and slow operation detection.

    Args:
        threshold_seconds: Threshold for slow operation warnings.
        log_slow_operations: Whether to log slow operations.

    Returns:
        Decorated async function with performance monitoring.
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not log_slow_operations:
                return await func(*args, **kwargs)

            logger = logging.getLogger(func.__module__)
            async with async_performance_monitor(func.__name__, logger, threshold_seconds):
                return await func(*args, **kwargs)

        # Mark for introspection
        setattr(wrapper, '_has_async_performance_monitoring', True)
        setattr(wrapper, '_async_performance_config', {
            'threshold_seconds': threshold_seconds,
            'log_slow_operations': log_slow_operations
        })
        return wrapper
    return decorator


def async_firestore_operation(use_transaction: bool = False,
                             log_operations: bool = True,
                             max_retries: int = 3,
                             cache_ttl: Optional[int] = None,
                             performance_threshold: float = 1.0) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Comprehensive async decorator combining all Firestore operation features.
    
    Args:
        use_transaction: Whether to wrap in transaction
        log_operations: Whether to log operations
        max_retries: Maximum retry attempts
        cache_ttl: Cache TTL in seconds (None to disable)
        performance_threshold: Performance monitoring threshold
        
    Returns:
        Decorated async function with comprehensive features
        
    Example:
        @async_firestore_operation(
            use_transaction=True,
            max_retries=3,
            cache_ttl=300
        )
        async def comprehensive_user_operation(user_data, transaction=None):
            # This operation will be transactional, with retries and caching.
            pass
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        """Applies decorators in a specific order."""
        
        # Apply decorators in reverse order (innermost to outermost)
        decorated_func: Callable[..., Awaitable[T]] = func
        
        if cache_ttl is not None:
            decorated_func = async_cache_result(ttl_seconds=cache_ttl)(decorated_func)

        if performance_threshold > 0:
            decorated_func = async_measure_performance(threshold_seconds=performance_threshold)(decorated_func)
            
        if log_operations:
            decorated_func = async_log_operations(log_level=logging.INFO)(decorated_func)

        if use_transaction:
            decorated_func = async_transactional(max_retries=max_retries)(decorated_func)
        else:
            decorated_func = async_retry_on_conflict(max_retries=max_retries)(decorated_func)

        # Return a new async function that calls the decorated chain
        @functools.wraps(decorated_func)
        async def wrapper(*args, **kwargs) -> T:
            return await decorated_func(*args, **kwargs)

        return wrapper
    return decorator

"""
Decorators for Firestore schema operations.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Tuple, Union
from functools import wraps
import logging
from datetime import datetime

from .transactions import TransactionManager, get_transaction_manager
from ..core.exceptions import SchemaError, ValidationError
from ..core.base import Document
from ..common.decorators import DEFAULT_RETRYABLE_EXCEPTIONS, performance_monitor, operation_logger, retry_logic_generator


# Type variable for decorated functions
T = TypeVar('T')


def transactional(
    max_retries: int = 3,
    log_operations: bool = True,
    transaction_manager: Optional[TransactionManager] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to make a function run within a Firestore transaction.
    
    Args:
        max_retries: Maximum number of retry attempts on transaction conflicts
        validate_schema: Whether to validate data against schema definitions
        log_operations: Whether to log transaction operations
        transaction_manager: Specific transaction manager to use (uses global if None)
    
    Returns:
        Decorated function that runs in a transaction
    
    Example:
        @transactional(max_retries=5, validate_schema=True)
        def update_user_profile(user_id: str, profile_data: dict, transaction=None):
            # Function receives transaction context as 'transaction' parameter
            user_ref = db.collection('users').document(user_id)
            transaction.update(user_ref, profile_data, document_class=UserDocument)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Get transaction manager
            manager = transaction_manager or get_transaction_manager()
            
            # Execute function in transaction
            return manager._execute_transaction(
                func, args, kwargs, max_retries, log_operations
            )
        
        # Mark function as transactional for introspection
        setattr(wrapper, '_is_transactional', True)
        setattr(wrapper, '_transaction_config', {
            'max_retries': max_retries,
            'log_operations': log_operations
        })
        
        return wrapper
    return decorator

def retry_on_conflict(
    max_retries: int = 3,
    backoff_multiplier: float = 1.5,
    max_backoff: float = 60.0,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to retry a function on specific, retryable exceptions.

    Args:
        max_retries: Maximum number of retry attempts.
        backoff_multiplier: Multiplier for exponential backoff.
        max_backoff: Maximum backoff time in seconds.
        retryable_exceptions: A tuple of exception types to retry on. 
                              Defaults to common Firestore conflict errors.

    Returns:
        Decorated function with automatic retry on conflicts.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            import time
            import random
            
            logger = logging.getLogger(func.__module__)
            exceptions_to_retry = retryable_exceptions or DEFAULT_RETRYABLE_EXCEPTIONS
            retry_gen = retry_logic_generator(max_retries, backoff_multiplier, max_backoff)

            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions_to_retry as e:
                    last_exception = e
                    if attempt < max_retries:
                        backoff_time = next(retry_gen)
                        logger.warning(
                            f"Attempt {attempt + 1} for {func.__name__} failed with {e.__class__.__name__}. "
                            f"Retrying in {backoff_time:.2f}s..."
                        )
                        time.sleep(backoff_time)
                    else:
                        logger.error(f"Function {func.__name__} failed after {max_retries + 1} attempts.", exc_info=last_exception)
                        raise SchemaError(f"Function {func.__name__} exhausted all retries.") from last_exception
            
            # This path should not be reached, but is a safeguard.
            raise SchemaError(f"Function {func.__name__} failed unexpectedly.") from last_exception
        
        # Mark function as retryable for introspection
        setattr(wrapper, '_has_retry', True)
        setattr(wrapper, '_retry_config', {
            'max_retries': max_retries,
            'backoff_multiplier': backoff_multiplier,
            'max_backoff': max_backoff
        })
        
        return wrapper
    return decorator


def log_operations(
    logger: Optional[logging.Logger] = None,
    log_level: int = logging.INFO,
    include_args: bool = False,
    include_result: bool = False
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to log function operations.

    Args:
        logger: Logger instance to use (creates default if None).
        log_level: Logging level to use.
        include_args: Whether to include function arguments in logs.
        include_result: Whether to include function result in logs.

    Returns:
        Decorated function with automatic operation logging.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            final_logger = logger or logging.getLogger(func.__module__)
            
            with operation_logger(final_logger, func.__name__, log_level, include_args, include_result, args, kwargs) as log_info:
                result = func(*args, **kwargs)
                if include_result:
                    log_info['result'] = str(result)
                return result

        # Mark function as logged for introspection
        setattr(wrapper, '_has_logging', True)
        setattr(wrapper, '_logging_config', {
            'log_level': log_level,
            'include_args': include_args,
            'include_result': include_result
        })
        return wrapper
    return decorator


def cache_result(
    ttl_seconds: int = 300,
    cache_key_func: Optional[Callable] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to cache function results (useful for read operations).
    
    Args:
        ttl_seconds: Time to live for cached results in seconds
        cache_key_func: Function to generate cache key from args/kwargs
    
    Returns:
        Decorated function with result caching
    
    Example:
        @cache_result(ttl_seconds=600)
        def get_user_profile(user_id: str):
            # Results are cached for 10 minutes
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Check cache
            current_time = datetime.now()
            if cache_key in cache:
                cached_result, cached_time = cache[cache_key]
                if (current_time - cached_time).total_seconds() < ttl_seconds:
                    return cached_result
                else:
                    # Expired, remove from cache
                    del cache[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            
            return result
        
        # Add cache management methods
        def clear_cache():
            cache.clear()
        
        def get_cache_stats():
            return {
                'size': len(cache),
                'keys': list(cache.keys())
            }
        
        setattr(wrapper, 'clear_cache', clear_cache)
        setattr(wrapper, 'get_cache_stats', get_cache_stats)
        
        # Mark function as cached for introspection
        setattr(wrapper, '_has_caching', True)
        setattr(wrapper, '_caching_config', {
            'ttl_seconds': ttl_seconds,
            'cache_key_func': cache_key_func
        })
        
        return wrapper
    return decorator


def measure_performance(
    logger: Optional[logging.Logger] = None,
    threshold_seconds: float = 1.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to measure and log function performance.

    Args:
        logger: Logger instance to use.
        threshold_seconds: Log warning if execution exceeds this threshold.

    Returns:
        Decorated function with performance monitoring.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            log = logger or logging.getLogger(func.__module__)
            with performance_monitor(func.__name__, log, threshold_seconds):
                return func(*args, **kwargs)

        # Mark for introspection
        setattr(wrapper, '_has_performance_monitoring', True)
        setattr(wrapper, '_performance_config', {'threshold_seconds': threshold_seconds})
        return wrapper
    return decorator


# Combination decorators for common patterns
def firestore_operation(
    use_transaction: bool = False,
    log_operations: bool = True,
    max_retries: int = 3
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Combination decorator for common Firestore operations.
    
    Args:
        use_transaction: Whether to wrap in transaction
        log_operations: Whether to log operations
        max_retries: Maximum retry attempts
    
    Returns:
        Decorated function with multiple enhancements
    
    Example:
        @firestore_operation(use_transaction=True, log_operations=True)
        def update_user_profile(user_id: str, data: dict):
            # Function has validation, transactions, logging, and retries
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Apply decorators in order
        decorated_func = func
        
        # Add performance monitoring
        decorated_func = measure_performance()(decorated_func)
        
        # Add operation logging if requested
        if log_operations:
            from . import decorators as dec_module
            decorated_func = dec_module.log_operations()(decorated_func)
        
        # Add retry logic
        decorated_func = retry_on_conflict(max_retries=max_retries)(decorated_func)
        
        # Add transaction if requested
        if use_transaction:
            decorated_func = transactional(
                max_retries=max_retries,
                log_operations=log_operations
            )(decorated_func)
        
        return decorated_func
    
    return decorator

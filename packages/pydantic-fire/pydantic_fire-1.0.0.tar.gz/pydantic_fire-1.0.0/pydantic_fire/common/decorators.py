# common/decorators.py

"""
This module contains common, reusable logic for decorators to reduce duplication
between synchronous and asynchronous implementations.
"""

import time
import logging
from contextlib import contextmanager, asynccontextmanager
from typing import Optional, Any, Dict
from functools import wraps
import random

# A default set of retryable exceptions for Firestore. 
# google.api_core.exceptions.Aborted is the most common for transaction conflicts.
# This can be customized by the decorator user.
try:
    from google.api_core import exceptions as google_exceptions
    DEFAULT_RETRYABLE_EXCEPTIONS = (google_exceptions.Aborted, google_exceptions.Conflict, google_exceptions.InternalServerError, google_exceptions.ServiceUnavailable)
except ImportError:
    DEFAULT_RETRYABLE_EXCEPTIONS = (Exception,) # Fallback if google-cloud-core is not installed

@contextmanager
def performance_monitor(func_name: str, logger: logging.Logger, threshold_seconds: float):
    """A context manager to measure and log the performance of a code block."""
    start_time = time.time()
    try:
        yield
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Function {func_name} failed after {duration:.3f}s: {e}",
            extra={'function': func_name, 'duration_seconds': duration, 'error': str(e)}
        )
        raise
    else:
        duration = time.time() - start_time
        if duration > threshold_seconds:
            logger.warning(
                f"Slow operation detected: {func_name} took {duration:.3f}s (threshold: {threshold_seconds}s)",
                extra={
                    'function': func_name,
                    'duration_seconds': duration,
                    'threshold_seconds': threshold_seconds,
                    'threshold_exceeded': True
                }
            )

@contextmanager
def operation_logger(logger: logging.Logger, func_name: str, log_level: int, include_args: bool, include_result: bool, args, kwargs):
    """A context manager to handle logging for an operation."""
    start_time = time.monotonic()
    log_extra = {'function': func_name, 'args': str(args) if include_args else 'omitted', 'kwargs': str(kwargs) if include_args else 'omitted'}
    logger.log(log_level, f"Starting operation: {func_name}", extra=log_extra)

    log_info = {'status': 'success'}
    try:
        yield log_info
    except Exception as e:
        log_info['status'] = 'error'
        log_info['error'] = str(e)
        raise
    finally:
        duration = time.monotonic() - start_time
        log_extra['duration'] = f"{duration:.3f}s"
        log_extra.update(log_info)

        if log_info['status'] == 'success':
            msg = f"Completed operation: {func_name} in {duration:.3f}s"
            if include_result:
                log_extra['result'] = str(log_info.get('result', 'omitted'))
            logger.log(log_level, msg, extra=log_extra)
        else:
            msg = f"Failed operation: {func_name} after {duration:.3f}s: {log_info['error']}"
            logger.error(msg, extra=log_extra)

@asynccontextmanager
async def async_operation_logger(logger: logging.Logger, func_name: str, log_level: int, include_args: bool, include_result: bool, args, kwargs):
    """An async context manager to handle logging for an async operation."""
    start_time = time.monotonic()
    log_extra = {'function': func_name, 'args': str(args) if include_args else 'omitted', 'kwargs': str(kwargs) if include_args else 'omitted'}
    logger.log(log_level, f"Starting async operation: {func_name}", extra=log_extra)

    log_info = {'status': 'success'}
    try:
        yield log_info
    except Exception as e:
        log_info['status'] = 'error'
        log_info['error'] = str(e)
        raise
    finally:
        duration = time.monotonic() - start_time
        log_extra['duration'] = f"{duration:.3f}s"
        log_extra.update(log_info)

        if log_info['status'] == 'success':
            msg = f"Completed async operation: {func_name} in {duration:.3f}s"
            if include_result:
                log_extra['result'] = str(log_info.get('result', 'omitted'))
            logger.log(log_level, msg, extra=log_extra)
        else:
            msg = f"Failed async operation: {func_name} after {duration:.3f}s: {log_info['error']}"
            logger.error(msg, extra=log_extra)

def retry_logic_generator(max_retries: int, backoff_multiplier: float, max_backoff: float):
    """A generator that yields calculated backoff times for retry attempts."""
    for attempt in range(max_retries):
        backoff_time = min(
            (backoff_multiplier ** attempt) + random.uniform(0, 0.1),  # Jitter
            max_backoff
        )
        yield backoff_time

@asynccontextmanager
async def async_performance_monitor(func_name: str, logger: logging.Logger, threshold_seconds: float):
    """An async context manager to measure and log the performance of a code block."""
    start_time = time.time()
    try:
        yield
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Function {func_name} failed after {duration:.3f}s: {e}",
            extra={'function': func_name, 'duration_seconds': duration, 'error': str(e)}
        )
        raise
    else:
        duration = time.time() - start_time
        if duration > threshold_seconds:
            logger.warning(
                f"Slow operation detected: {func_name} took {duration:.3f}s (threshold: {threshold_seconds}s)",
                extra={
                    'function': func_name,
                    'duration_seconds': duration,
                    'threshold_seconds': threshold_seconds,
                    'threshold_exceeded': True
                }
            )


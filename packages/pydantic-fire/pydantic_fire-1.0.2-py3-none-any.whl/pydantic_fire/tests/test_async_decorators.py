import unittest
import asyncio
from unittest.mock import AsyncMock, patch, Mock
import logging

from ..async_operations.async_decorators import (
    async_measure_performance,
    async_log_operations,
    async_retry_on_conflict,
)
from ..core.exceptions import SchemaError

# Suppress logging output during tests
logging.disable(logging.CRITICAL)


class TestAsyncDecorators(unittest.IsolatedAsyncioTestCase):
    """Tests for asynchronous decorators."""

    def setUp(self):
        """Set up a logger and a mock function for each test."""
        self.logger = logging.getLogger(__name__)
        self.mock_func = AsyncMock()

    # --- Tests for @async_measure_performance --- #

    async def test_async_measure_performance_fast_operation(self):
        """Test that @async_measure_performance does not log for fast operations."""
        @async_measure_performance(threshold_seconds=0.1)
        async def fast_op():
            return "success"

        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            result = await fast_op()
            self.assertEqual(result, "success")
            mock_logger.warning.assert_not_called()

    async def test_async_measure_performance_slow_operation(self):
        """Test that @async_measure_performance logs a warning for slow operations."""
        @async_measure_performance(threshold_seconds=0.05)
        async def slow_op():
            await asyncio.sleep(0.1)
            return "done"

        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            result = await slow_op()
            self.assertEqual(result, "done")
            mock_logger.warning.assert_called_once()
            self.assertIn("Slow operation detected", mock_logger.warning.call_args[0][0])

    # --- Tests for @async_log_operations --- #

    async def test_async_log_operations_basic_logging(self):
        """Test basic start/end logging for @async_log_operations."""
        @async_log_operations()
        async def basic_op():
            return "result"

        with patch.object(self.logger, 'log') as mock_log:
            await basic_op()
            self.assertEqual(mock_log.call_count, 2)

            # Check start log
            start_call = mock_log.call_args_list[0]
            self.assertEqual(start_call.args, (logging.INFO, 'Starting async operation: basic_op'))
            self.assertEqual(start_call.kwargs['extra']['function'], 'basic_op')

            # Check completion log
            end_call = mock_log.call_args_list[1]
            self.assertIn('Completed async operation: basic_op', end_call.args[1])

    async def test_async_log_operations_with_args_and_result(self):
        """Test logging with arguments and results included."""
        @async_log_operations(include_args=True, include_result=True)
        async def complex_op(a, b):
            return a + b

        with patch.object(self.logger, 'log') as mock_log:
            await complex_op(1, b=2)
            self.assertEqual(mock_log.call_count, 2)

            # Check start log extra data
            start_call = mock_log.call_args_list[0]
            self.assertEqual(start_call.kwargs['extra']['args'], '(1,)')
            self.assertEqual(start_call.kwargs['extra']['kwargs'], "{'b': 2}")

            # Check completion log extra data
            end_call = mock_log.call_args_list[1]
            self.assertEqual(end_call.kwargs['extra']['result'], '3')

    async def test_async_log_operations_on_exception(self):
        """Test that @async_log_operations logs exceptions."""
        @async_log_operations()
        async def failing_op():
            raise ValueError("test error")

        with patch.object(self.logger, 'error') as mock_error:
            with self.assertRaises(ValueError):
                await failing_op()
            mock_error.assert_called_once()
            self.assertIn("Failed async operation: failing_op", mock_error.call_args.args[0])

    # --- Tests for @async_retry_on_conflict --- #

    class CustomRetryableError(Exception):
        pass

    async def test_async_retry_on_conflict_succeeds_on_first_try(self):
        """Test that the function is not retried if it succeeds."""
        self.mock_func.return_value = "success"
        decorated_func = async_retry_on_conflict()(self.mock_func)

        result = await decorated_func()

        self.assertEqual(result, "success")
        self.mock_func.assert_awaited_once()

    async def test_async_retry_on_conflict_succeeds_after_retries(self):
        """Test that the function succeeds after a few retries."""
        self.mock_func.side_effect = [self.CustomRetryableError, self.CustomRetryableError, "success"]
        decorated_func = async_retry_on_conflict(
            max_retries=3, retryable_exceptions=(self.CustomRetryableError,)
        )(self.mock_func)

        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await decorated_func()
            self.assertEqual(result, "success")
            self.assertEqual(self.mock_func.await_count, 3)
            self.assertEqual(mock_sleep.await_count, 2)

    async def test_async_retry_on_conflict_fails_after_all_retries(self):
        """Test that an exception is raised after all retries are exhausted."""
        self.mock_func.side_effect = self.CustomRetryableError("Permanent failure")
        decorated_func = async_retry_on_conflict(
            max_retries=2, retryable_exceptions=(self.CustomRetryableError,)
        )(self.mock_func)

        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            with self.assertRaises(SchemaError) as context:
                await decorated_func()
            
            self.assertIn("exhausted all retries", str(context.exception))
            self.assertEqual(self.mock_func.await_count, 3)  # 1 initial + 2 retries
            self.assertEqual(mock_sleep.await_count, 2)

if __name__ == '__main__':
    unittest.main()

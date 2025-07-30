"""
Tests for the common decorator utilities in `common/decorators.py`.
"""

import unittest
import logging
import time
import asyncio
from unittest.mock import MagicMock, patch, call, ANY

from ..common.decorators import (
    performance_monitor,
    operation_logger,
    async_performance_monitor,
    async_operation_logger,
    retry_logic_generator
)

# Suppress logging output during tests
logging.disable(logging.CRITICAL)


class TestCommonSyncDecorators(unittest.TestCase):
    """Tests for synchronous common decorator utilities."""

    def setUp(self):
        self.logger = MagicMock(spec=logging.Logger)

    @patch('time.time')
    def test_performance_monitor_slow_operation(self, mock_time):
        """Test that performance_monitor logs a warning for slow operations."""
        mock_time.side_effect = [100.0, 100.5]  # 0.5s duration
        func_name = 'test_slow_func'
        threshold = 0.2

        with performance_monitor(func_name, self.logger, threshold):
            pass

        self.logger.warning.assert_called_once()
        self.assertIn(f"Slow operation detected: {func_name}", self.logger.warning.call_args[0][0])

    @patch('time.time')
    def test_performance_monitor_fast_operation(self, mock_time):
        """Test that performance_monitor does not log for fast operations."""
        mock_time.side_effect = [100.0, 100.1]  # 0.1s duration

        with performance_monitor('test_fast_func', self.logger, 0.2):
            pass

        self.logger.warning.assert_not_called()

    @patch('time.time')
    def test_performance_monitor_exception(self, mock_time):
        """Test that performance_monitor logs an error on exception."""
        mock_time.side_effect = [100.0, 100.1]
        error = ValueError("Something went wrong")

        with self.assertRaises(ValueError):
            with performance_monitor('test_fail_func', self.logger, 0.2):
                raise error

        self.logger.error.assert_called_once()
        self.assertIn("failed after", self.logger.error.call_args[0][0])

    @patch('time.monotonic')
    def test_operation_logger_success(self, mock_monotonic):
        """Test operation_logger logs start and completion on success."""
        mock_monotonic.side_effect = [100.0, 100.1]
        func_name = 'test_op_success'

        with operation_logger(self.logger, func_name, logging.INFO, True, True, ('arg1',), {'kwarg1': 'val1'}) as log_info:
            log_info['result'] = 'SuccessData'

        self.assertEqual(self.logger.log.call_count, 2)
        self.logger.log.assert_any_call(logging.INFO, f"Starting operation: {func_name}", extra=ANY)
        self.logger.log.assert_any_call(logging.INFO, f"Completed operation: {func_name} in 0.100s", extra=ANY)
        final_log_extra = self.logger.log.call_args.kwargs['extra']
        self.assertEqual(final_log_extra['status'], 'success')
        self.assertEqual(final_log_extra['result'], 'SuccessData')

    @patch('time.monotonic')
    def test_operation_logger_failure(self, mock_monotonic):
        """Test operation_logger logs an error on failure."""
        mock_monotonic.side_effect = [100.0, 100.1]
        func_name = 'test_op_fail'
        error = RuntimeError("DB error")

        with self.assertRaises(RuntimeError):
            with operation_logger(self.logger, func_name, logging.INFO, True, True, (), {}):
                raise error

        self.logger.log.assert_called_once_with(logging.INFO, f"Starting operation: {func_name}", extra=ANY)
        self.logger.error.assert_called_once()
        self.assertIn(f"Failed operation: {func_name}", self.logger.error.call_args[0][0])
        final_log_extra = self.logger.error.call_args.kwargs['extra']
        self.assertEqual(final_log_extra['status'], 'error')
        self.assertEqual(final_log_extra['error'], str(error))

    def test_retry_logic_generator(self):
        """Test the retry_logic_generator yields correct backoff times."""
        max_retries = 3
        backoff_multiplier = 2.0
        max_backoff = 10.0

        with patch('random.uniform', return_value=0.0):
            gen = retry_logic_generator(max_retries, backoff_multiplier, max_backoff)
            backoffs = list(gen)

        self.assertEqual(len(backoffs), max_retries)
        self.assertAlmostEqual(backoffs[0], 1.0)  # 2**0
        self.assertAlmostEqual(backoffs[1], 2.0)  # 2**1
        self.assertAlmostEqual(backoffs[2], 4.0)  # 2**2


class TestCommonAsyncDecorators(unittest.IsolatedAsyncioTestCase):
    """Tests for asynchronous common decorator utilities."""

    def setUp(self):
        self.logger = MagicMock(spec=logging.Logger)

    @patch('time.time')
    async def test_async_performance_monitor_slow_operation(self, mock_time):
        """Test async_performance_monitor logs a warning for slow operations."""
        mock_time.side_effect = [100.0, 100.5]
        func_name = 'test_async_slow_func'
        threshold = 0.2

        async with async_performance_monitor(func_name, self.logger, threshold):
            await asyncio.sleep(0)

        self.logger.warning.assert_called_once()
        self.assertIn(f"Slow operation detected: {func_name}", self.logger.warning.call_args[0][0])

    @patch('time.monotonic')
    async def test_async_operation_logger_success(self, mock_monotonic):
        """Test async_operation_logger logs start and completion on success."""
        def monotonic_generator():
            yield 100.0
            yield 100.100
            while True:
                yield 100.3  # Keep yielding for any teardown calls
        mock_monotonic.side_effect = monotonic_generator()
        func_name = 'test_async_op_success'

        async with async_operation_logger(self.logger, func_name, logging.INFO, True, True, (), {}) as log_info:
            log_info['result'] = 'AsyncSuccess'

        self.assertEqual(self.logger.log.call_count, 2)
        self.logger.log.assert_any_call(logging.INFO, f"Starting async operation: {func_name}", extra=ANY)
        self.logger.log.assert_any_call(logging.INFO, f"Completed async operation: {func_name} in 0.100s", extra=ANY)
        final_log_extra = self.logger.log.call_args.kwargs['extra']
        self.assertEqual(final_log_extra['status'], 'success')
        self.assertEqual(final_log_extra['result'], 'AsyncSuccess')

    @patch('time.monotonic')
    async def test_async_operation_logger_failure(self, mock_monotonic):
        """Test async_operation_logger logs an error on failure."""
        def monotonic_generator():
            yield 100.0
            yield 100.1
            while True:
                yield 100.2  # Keep yielding for any teardown calls
        mock_monotonic.side_effect = monotonic_generator()
        func_name = 'test_async_op_fail'
        error = ConnectionError("Network down")

        with self.assertRaises(ConnectionError):
            async with async_operation_logger(self.logger, func_name, logging.INFO, True, True, (), {}):
                raise error

        self.logger.log.assert_called_once_with(logging.INFO, f"Starting async operation: {func_name}", extra=ANY)
        self.logger.error.assert_called_once()
        self.assertIn(f"Failed async operation: {func_name}", self.logger.error.call_args[0][0])
        final_log_extra = self.logger.error.call_args.kwargs['extra']
        self.assertEqual(final_log_extra['status'], 'error')
        self.assertEqual(final_log_extra['error'], str(error))


if __name__ == '__main__':
    unittest.main()

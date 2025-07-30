import unittest
from unittest.mock import Mock, patch, call
import logging
import time

from ..sync_operations.decorators import (
    measure_performance,
    log_operations,
    retry_on_conflict,
)

# Suppress logging output during tests
logging.disable(logging.CRITICAL)


class TestSyncDecorators(unittest.TestCase):
    """Tests for synchronous decorators."""

    def setUp(self):
        """Set up a logger and a mock function for each test."""
        self.logger = logging.getLogger(__name__)
        self.mock_func = Mock(__name__="mock_func")

    # --- Tests for @measure_performance --- #

    def test_measure_performance_fast_operation(self):
        """Test that @measure_performance does not log for fast operations."""
        @measure_performance(logger=self.logger, threshold_seconds=0.1)
        def fast_op():
            return "success"

        with patch.object(self.logger, 'warning') as mock_warning:
            result = fast_op()
            self.assertEqual(result, "success")
            mock_warning.assert_not_called()

    def test_measure_performance_slow_operation(self):
        """Test that @measure_performance logs a warning for slow operations."""
        @measure_performance(logger=self.logger, threshold_seconds=0.05)
        def slow_op():
            time.sleep(0.1)
            return "done"

        with patch.object(self.logger, 'warning') as mock_warning:
            result = slow_op()
            self.assertEqual(result, "done")
            mock_warning.assert_called_once()
            self.assertIn("Slow operation detected", mock_warning.call_args[0][0])

    # --- Tests for @log_operations --- #

    def test_log_operations_basic_logging(self):
        """Test basic start/end logging for @log_operations."""
        @log_operations(logger=self.logger)
        def basic_op():
            return "result"

        with patch.object(self.logger, 'log') as mock_log:
            basic_op()
            self.assertEqual(mock_log.call_count, 2)

            # Check start log
            start_call = mock_log.call_args_list[0]
            self.assertEqual(start_call.args, (logging.INFO, 'Starting operation: basic_op'))
            self.assertEqual(start_call.kwargs['extra']['function'], 'basic_op')

            # Check completion log
            end_call = mock_log.call_args_list[1]
            self.assertIn('Completed operation: basic_op', end_call.args[1])

    def test_log_operations_with_args_and_result(self):
        """Test logging with arguments and results included."""
        @log_operations(logger=self.logger, include_args=True, include_result=True)
        def complex_op(a, b):
            return a + b

        with patch.object(self.logger, 'log') as mock_log:
            complex_op(1, b=2)
            self.assertEqual(mock_log.call_count, 2)

            # Check start log extra data
            start_call = mock_log.call_args_list[0]
            self.assertEqual(start_call.kwargs['extra']['args'], '(1,)')
            self.assertEqual(start_call.kwargs['extra']['kwargs'], "{'b': 2}")

            # Check completion log extra data
            end_call = mock_log.call_args_list[1]
            self.assertEqual(end_call.kwargs['extra']['result'], '3')

    def test_log_operations_on_exception(self):
        """Test that @log_operations logs exceptions."""
        @log_operations(logger=self.logger)
        def failing_op():
            raise ValueError("test error")

        with patch.object(self.logger, 'error') as mock_error:
            with self.assertRaises(ValueError):
                failing_op()
            mock_error.assert_called_once()
            self.assertIn("Failed operation: failing_op", mock_error.call_args.args[0])

    # --- Tests for @retry_on_conflict --- #

    class CustomRetryableError(Exception):
        pass

    def test_retry_on_conflict_succeeds_on_first_try(self):
        """Test that the function is not retried if it succeeds."""
        self.mock_func.return_value = "success"
        decorated_func = retry_on_conflict()(self.mock_func)

        result = decorated_func()

        self.assertEqual(result, "success")
        self.mock_func.assert_called_once()

    def test_retry_on_conflict_succeeds_after_retries(self):
        """Test that the function succeeds after a few retries."""
        self.mock_func.side_effect = [self.CustomRetryableError, self.CustomRetryableError, "success"]
        decorated_func = retry_on_conflict(
            max_retries=3, retryable_exceptions=(self.CustomRetryableError,)
        )(self.mock_func)

        with patch('time.sleep') as mock_sleep:
            result = decorated_func()
            self.assertEqual(result, "success")
            self.assertEqual(self.mock_func.call_count, 3)
            self.assertEqual(mock_sleep.call_count, 2)

    def test_retry_on_conflict_fails_after_all_retries(self):
        """Test that an exception is raised after all retries are exhausted."""
        self.mock_func.side_effect = self.CustomRetryableError("Permanent failure")
        decorated_func = retry_on_conflict(
            max_retries=2, retryable_exceptions=(self.CustomRetryableError,)
        )(self.mock_func)

        with patch('time.sleep') as mock_sleep:
            with self.assertRaises(Exception) as context:
                decorated_func()
            
            self.assertIn("Function mock_func exhausted all retries.", str(context.exception))
            self.assertEqual(self.mock_func.call_count, 3)  # 1 initial + 2 retries
            self.assertEqual(mock_sleep.call_count, 2)

if __name__ == '__main__':
    unittest.main()

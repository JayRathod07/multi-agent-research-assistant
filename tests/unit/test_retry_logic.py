"""
Unit tests for retry_logic.py.
"""
import sys
import os
import pytest
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from unittest.mock import MagicMock, patch, call

from exceptions import AuthenticationError, NetworkError
from retry_logic import call_with_retry


class TestCallWithRetry:
    def test_successful_first_attempt_returns_result(self):
        func = MagicMock(return_value="success")
        result = call_with_retry(func, max_retries=1, backoff_seconds=0)
        assert result == "success"
        assert func.call_count == 1

    def test_retry_on_failure_then_success(self):
        func = MagicMock(side_effect=[NetworkError("fail"), "success"])
        result = call_with_retry(func, max_retries=1, backoff_seconds=0)
        assert result == "success"
        assert func.call_count == 2

    def test_raises_after_max_retries_exhausted(self):
        func = MagicMock(side_effect=NetworkError("fail"))
        with pytest.raises(NetworkError):
            call_with_retry(func, max_retries=1, backoff_seconds=0)
        assert func.call_count == 2  # 1 attempt + 1 retry

    def test_no_retry_for_authentication_error(self):
        func = MagicMock(side_effect=AuthenticationError("bad key"))
        with pytest.raises(AuthenticationError):
            call_with_retry(func, max_retries=1, backoff_seconds=0)
        assert func.call_count == 1  # Never retried

    def test_exactly_one_retry_by_default(self):
        func = MagicMock(side_effect=NetworkError("fail"))
        with pytest.raises(NetworkError):
            call_with_retry(func, backoff_seconds=0)
        assert func.call_count == 2

    @patch("retry_logic.time.sleep")
    def test_backoff_sleep_called_between_retries(self, mock_sleep):
        func = MagicMock(side_effect=[NetworkError("fail"), "ok"])
        call_with_retry(func, max_retries=1, backoff_seconds=2.0)
        mock_sleep.assert_called_once_with(2.0)

    @patch("retry_logic.time.sleep")
    def test_no_sleep_on_first_success(self, mock_sleep):
        func = MagicMock(return_value="ok")
        call_with_retry(func, max_retries=1, backoff_seconds=2.0)
        mock_sleep.assert_not_called()

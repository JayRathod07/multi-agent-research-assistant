"""
Retry utility for the Multi-Agent Research Assistant.

Provides call_with_retry() — a simple wrapper that executes a callable
and retries exactly once on failure, with configurable backoff.
Authentication errors are never retried (they won't succeed on retry).
"""

import time
from typing import Any, Callable, TypeVar

from exceptions import AuthenticationError
from utils.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def call_with_retry(
    func: Callable[[], T],
    max_retries: int = 1,
    backoff_seconds: float = 2.0,
    context: str = "operation",
) -> T:
    """
    Execute ``func`` with up to ``max_retries`` retries on failure.

    Args:
        func:            Zero-argument callable to execute.
        max_retries:     Number of additional attempts after first failure (default 1).
        backoff_seconds: Seconds to wait between attempts (default 2).
        context:         Human-readable label used in log messages.

    Returns:
        The return value of ``func`` on success.

    Raises:
        AuthenticationError: Immediately, without retry.
        Exception:           The last exception raised if all attempts fail.
    """
    last_exception: Exception = RuntimeError("No attempts made")

    for attempt in range(max_retries + 1):
        try:
            result = func()
            if attempt > 0:
                logger.info(
                    "[%s] Retry succeeded on attempt %d.",
                    context,
                    attempt + 1,
                )
            return result

        except AuthenticationError:
            # Authentication won't improve on retry — raise immediately.
            logger.error("[%s] Authentication error — not retrying.", context)
            raise

        except Exception as exc:  # noqa: BLE001
            last_exception = exc
            if attempt < max_retries:
                logger.warning(
                    "[%s] Attempt %d/%d failed: %s. "
                    "Retrying in %.1f second(s)…",
                    context,
                    attempt + 1,
                    max_retries + 1,
                    exc,
                    backoff_seconds,
                )
                time.sleep(backoff_seconds)
            else:
                logger.error(
                    "[%s] All %d attempt(s) failed. Last error: %s",
                    context,
                    max_retries + 1,
                    exc,
                )

    raise last_exception

"""
Custom exception hierarchy for the Multi-Agent Research Assistant pipeline.
All exceptions inherit from PipelineError for unified catching where needed.
"""

from typing import Optional


class PipelineError(Exception):
    """Base exception for all pipeline errors."""
    pass


class ValidationError(PipelineError):
    """Raised when input validation fails (e.g., empty or too-long topic)."""
    pass


class AgentExecutionError(PipelineError):
    """Raised when an agent fails to execute after all retries are exhausted."""

    def __init__(
        self,
        agent_name: str,
        message: str,
        original_error: Optional[Exception] = None,
    ):
        self.agent_name = agent_name
        self.original_error = original_error
        super().__init__(f"{agent_name} failed: {message}")


class APIError(PipelineError):
    """Base exception for API-related errors."""
    pass


class AuthenticationError(APIError):
    """Raised when the API key is missing or invalid."""
    pass


class RateLimitError(APIError):
    """Raised when the API rate limit is exceeded."""
    pass


class TimeoutError(APIError):
    """Raised when an API request times out."""
    pass


class NetworkError(APIError):
    """Raised when a network connection failure occurs."""
    pass

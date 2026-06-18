"""
Claude API client wrapper for the Multi-Agent Research Assistant.

Wraps the Anthropic SDK with:
- .env loading
- Structured error mapping to custom exceptions
- Simple call_claude() interface for all agents
"""

import os

import anthropic
from dotenv import load_dotenv

from error_messages import ERROR_MESSAGES
from exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    TimeoutError,
)
from utils.logging_config import get_logger

logger = get_logger(__name__)


class APIClient:
    """Thin wrapper around the Anthropic SDK for making Claude API calls."""

    def __init__(self) -> None:
        """
        Load the API key from the .env file and initialise the Anthropic client.

        Raises:
            AuthenticationError: If ANTHROPIC_API_KEY is missing from environment.
        """
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise AuthenticationError(ERROR_MESSAGES["missing_api_key"])

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022")
        self._max_tokens_default = int(os.getenv("MAX_TOKENS", "1024"))

        logger.debug(
            "APIClient initialised. Model: %s, max_tokens default: %d",
            self._model,
            self._max_tokens_default,
        )

    def call_claude(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 0,
    ) -> str:
        """
        Make a single API call to Claude and return the text response.

        Args:
            system_prompt: Agent-specific instruction passed as the system role.
            user_message:  The user-turn message (topic, notes, or combined input).
            max_tokens:    Maximum response length; defaults to MAX_TOKENS env var.

        Returns:
            Plain text string extracted from the API response.

        Raises:
            AuthenticationError: Invalid or missing API key.
            RateLimitError:      Rate limit exceeded.
            TimeoutError:        Request timed out.
            NetworkError:        Connection failure.
        """
        effective_max_tokens = max_tokens or self._max_tokens_default

        logger.debug(
            "Calling Claude | model=%s | max_tokens=%d | "
            "system_prompt_length=%d | user_message_length=%d",
            self._model,
            effective_max_tokens,
            len(system_prompt),
            len(user_message),
        )

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=effective_max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            text = self._extract_text(response)
            logger.debug("API response received: %d characters", len(text))
            return text

        except anthropic.AuthenticationError as exc:
            logger.error("Authentication failed: %s", exc)
            raise AuthenticationError(ERROR_MESSAGES["invalid_api_key"]) from exc

        except anthropic.RateLimitError as exc:
            logger.error("Rate limit exceeded: %s", exc)
            raise RateLimitError(ERROR_MESSAGES["rate_limit"]) from exc

        except anthropic.APITimeoutError as exc:
            logger.error("Request timed out: %s", exc)
            raise TimeoutError(ERROR_MESSAGES["timeout"]) from exc

        except anthropic.APIConnectionError as exc:
            logger.error("Network connection error: %s", exc)
            raise NetworkError(ERROR_MESSAGES["network_error"]) from exc

        except anthropic.APIStatusError as exc:
            logger.error("Unexpected API status error: %s", exc)
            raise NetworkError(
                f"Unexpected API error (status {exc.status_code}): {exc.message}"
            ) from exc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_text(response: anthropic.types.Message) -> str:
        """
        Extract the plain text from the first text block in an API response.

        Args:
            response: A raw Anthropic Message object.

        Returns:
            Text content, or empty string if none found.
        """
        for block in response.content:
            if block.type == "text":
                return block.text
        return ""

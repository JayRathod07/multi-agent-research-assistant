"""
Groq API client wrapper for the Multi-Agent Research Assistant.

Replaces the Anthropic/Claude client with Groq (free tier).
Uses llama-3.3-70b-versatile by default — fast, high quality, free.

Maintains the same call_claude() interface so all three agents
(researcher, analyst, writer) work without any changes.
"""

import os

from dotenv import load_dotenv
from groq import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError as GroqAuthError,
    Groq,
    RateLimitError as GroqRateLimitError,
)

from error_messages import ERROR_MESSAGES
from exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    TimeoutError,
)
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Default model — best free model on Groq
DEFAULT_MODEL    = "llama-3.3-70b-versatile"
DEFAULT_MAX_TOKENS = 1024


class APIClient:
    """Thin wrapper around the Groq SDK — drop-in replacement for the old Claude client."""

    def __init__(self) -> None:
        """
        Load the GROQ_API_KEY from environment and initialise the Groq client.

        Raises:
            AuthenticationError: If GROQ_API_KEY is missing from environment.
        """
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise AuthenticationError(
                "GROQ_API_KEY is not set. Add it to your .env file or "
                "Streamlit Cloud secrets."
            )

        self._client = Groq(api_key=api_key)
        self._model  = os.getenv("MODEL_NAME", DEFAULT_MODEL)
        self._max_tokens_default = int(os.getenv("MAX_TOKENS", str(DEFAULT_MAX_TOKENS)))

        logger.debug(
            "APIClient (Groq) initialised. Model: %s, max_tokens: %d",
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
        Make a single API call to Groq and return the text response.

        The method is intentionally named call_claude() so all existing
        agent code continues to work without modification.

        Args:
            system_prompt: Agent-specific instruction (system role).
            user_message:  The user-turn message.
            max_tokens:    Maximum response length; defaults to MAX_TOKENS env var.

        Returns:
            Plain text string from the model.

        Raises:
            AuthenticationError: Invalid or missing API key.
            RateLimitError:      Rate limit exceeded.
            TimeoutError:        Request timed out.
            NetworkError:        Connection failure.
        """
        effective_max_tokens = max_tokens or self._max_tokens_default

        logger.debug(
            "Calling Groq | model=%s | max_tokens=%d | "
            "system=%d chars | user=%d chars",
            self._model,
            effective_max_tokens,
            len(system_prompt),
            len(user_message),
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                max_tokens=effective_max_tokens,
                messages=[
                    {"role": "system",  "content": system_prompt},
                    {"role": "user",    "content": user_message},
                ],
            )

            text = response.choices[0].message.content or ""
            logger.debug("Groq response: %d characters", len(text))
            return text

        except GroqAuthError as exc:
            logger.error("Groq authentication failed: %s", exc)
            raise AuthenticationError(ERROR_MESSAGES["invalid_api_key"]) from exc

        except GroqRateLimitError as exc:
            logger.error("Groq rate limit exceeded: %s", exc)
            raise RateLimitError(ERROR_MESSAGES["rate_limit"]) from exc

        except APIConnectionError as exc:
            logger.error("Groq connection error: %s", exc)
            raise NetworkError(ERROR_MESSAGES["network_error"]) from exc

        except APIStatusError as exc:
            logger.error("Groq API status error %s: %s", exc.status_code, exc.message)
            raise NetworkError(
                f"Groq API error (status {exc.status_code}): {exc.message}"
            ) from exc

        except Exception as exc:  # noqa: BLE001
            logger.error("Unexpected Groq error: %s", exc)
            raise NetworkError(f"Unexpected error: {exc}") from exc

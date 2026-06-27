"""
Phase 2 unit tests — Groq API Client (api_client.py).

Strategy: We patch os.getenv to isolate key reading, and directly replace
the _client attribute on the APIClient instance with a mock so no real
network calls are ever made.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from unittest.mock import MagicMock, patch, PropertyMock

from exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_groq_response(text):
    """Build a minimal mock Groq chat completion response."""
    choice = MagicMock()
    choice.message.content = text
    response = MagicMock()
    response.choices = [choice]
    return response


def _make_api_client(mock_groq_create_value=None, mock_groq_create_error=None):
    """
    Create a real APIClient object using the real GROQ_API_KEY from .env,
    then swap out its internal _client with a MagicMock so no real HTTP
    calls are made.

    Args:
        mock_groq_create_value: Return value for chat.completions.create().
        mock_groq_create_error: Side-effect (exception) for chat.completions.create().
    """
    from api_client import APIClient
    client = APIClient()  # Uses real key from .env (OK — we won't make real calls)

    # Replace internal Groq client with mock
    mock_inner = MagicMock()
    if mock_groq_create_error is not None:
        mock_inner.chat.completions.create.side_effect = mock_groq_create_error
    else:
        mock_inner.chat.completions.create.return_value = mock_groq_create_value
    client._client = mock_inner
    return client, mock_inner


# ── Init tests ─────────────────────────────────────────────────────────────────

class TestGroqAPIClientInit:
    def test_raises_auth_error_when_key_missing(self):
        """APIClient raises AuthenticationError when GROQ_API_KEY env var is empty."""
        # Temporarily override getenv to return empty string for GROQ_API_KEY
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "GROQ_API_KEY":
                return ""
            return original_getenv(key, default)

        with patch("api_client.os.getenv", side_effect=mock_getenv):
            with patch("api_client.load_dotenv"):  # don't re-read .env
                from api_client import APIClient
                with pytest.raises(AuthenticationError):
                    APIClient()

    def test_initialises_successfully_with_valid_key(self):
        """APIClient constructs without error when a valid key is present."""
        from api_client import APIClient
        client = APIClient()  # uses real key from .env
        assert client is not None
        assert hasattr(client, "call_claude")


# ── call_claude tests ──────────────────────────────────────────────────────────

class TestGroqAPIClientCallClaude:
    def test_successful_call_returns_text(self):
        client, _ = _make_api_client(
            mock_groq_create_value=_make_groq_response("Key facts about AI in healthcare...")
        )
        result = client.call_claude("You are a researcher.", "Tell me about AI.")
        assert "AI" in result

    def test_system_and_user_messages_sent_correctly(self):
        client, mock_inner = _make_api_client(
            mock_groq_create_value=_make_groq_response("response")
        )
        client.call_claude("System prompt here", "User message here")
        call_kwargs = mock_inner.chat.completions.create.call_args[1]
        messages = call_kwargs["messages"]
        roles = [m["role"] for m in messages]
        contents = [m["content"] for m in messages]
        assert "system" in roles
        assert "user" in roles
        assert "System prompt here" in contents
        assert "User message here" in contents

    def test_groq_auth_error_maps_to_auth_error(self):
        from groq import AuthenticationError as GroqAuthError
        client, _ = _make_api_client(
            mock_groq_create_error=GroqAuthError(
                "Invalid key", response=MagicMock(status_code=401), body={}
            )
        )
        with pytest.raises(AuthenticationError):
            client.call_claude("system", "user")

    def test_groq_rate_limit_maps_to_rate_limit_error(self):
        from groq import RateLimitError as GroqRateLimitError
        client, _ = _make_api_client(
            mock_groq_create_error=GroqRateLimitError(
                "Rate limit", response=MagicMock(status_code=429), body={}
            )
        )
        with pytest.raises(RateLimitError):
            client.call_claude("system", "user")

    def test_connection_error_maps_to_network_error(self):
        from groq import APIConnectionError as GroqConnectionError
        client, _ = _make_api_client(
            mock_groq_create_error=GroqConnectionError(request=MagicMock())
        )
        with pytest.raises(NetworkError):
            client.call_claude("system", "user")

    def test_api_status_error_maps_to_network_error(self):
        from groq import APIStatusError
        client, _ = _make_api_client(
            mock_groq_create_error=APIStatusError(
                "Bad gateway", response=MagicMock(status_code=502), body={}
            )
        )
        with pytest.raises(NetworkError):
            client.call_claude("system", "user")

    def test_unexpected_error_maps_to_network_error(self):
        client, _ = _make_api_client(
            mock_groq_create_error=RuntimeError("Something weird")
        )
        with pytest.raises(NetworkError):
            client.call_claude("system", "user")

    def test_none_response_content_returns_empty_string(self):
        client, _ = _make_api_client(
            mock_groq_create_value=_make_groq_response(None)
        )
        result = client.call_claude("system", "user")
        assert result == ""

    def test_custom_max_tokens_passed_to_groq(self):
        client, mock_inner = _make_api_client(
            mock_groq_create_value=_make_groq_response("ok")
        )
        client.call_claude("system", "user", max_tokens=512)
        call_kwargs = mock_inner.chat.completions.create.call_args[1]
        assert call_kwargs["max_tokens"] == 512

    def test_default_max_tokens_used_when_zero(self):
        client, mock_inner = _make_api_client(
            mock_groq_create_value=_make_groq_response("ok")
        )
        client.call_claude("system", "user", max_tokens=0)
        call_kwargs = mock_inner.chat.completions.create.call_args[1]
        # Should use the instance default, not 0
        assert call_kwargs["max_tokens"] > 0

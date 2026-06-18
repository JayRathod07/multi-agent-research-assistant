"""
Unit tests for the Researcher Agent (agents/researcher.py).
All API calls are mocked — no real network requests are made.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from unittest.mock import MagicMock, patch

from agents import researcher
from exceptions import AgentExecutionError, NetworkError


TOPIC = "Machine Learning"

GOOD_RESPONSE = (
    "- ML is a subset of artificial intelligence\n"
    "- Supervised learning uses labelled training data\n"
    "- Neural networks are inspired by the human brain\n"
    "- Overfitting is a common challenge in ML models\n"
    "- Gradient descent is used to optimise model parameters"
)


def _make_client(response: str) -> MagicMock:
    client = MagicMock()
    client.call_claude.return_value = response
    return client


class TestResearcher:
    def test_returns_bullet_list_on_success(self):
        client = _make_client(GOOD_RESPONSE)
        result = researcher.execute(TOPIC, client)
        assert result == GOOD_RESPONSE
        assert "- " in result

    def test_api_called_with_correct_system_prompt(self):
        client = _make_client(GOOD_RESPONSE)
        researcher.execute(TOPIC, client)
        call_args = client.call_claude.call_args
        system_prompt = call_args[0][0]
        assert "Research Agent" in system_prompt

    def test_api_called_with_topic_in_user_message(self):
        client = _make_client(GOOD_RESPONSE)
        researcher.execute(TOPIC, client)
        call_args = client.call_claude.call_args
        user_message = call_args[0][1]
        assert TOPIC in user_message

    def test_short_response_triggers_enhanced_prompt_retry(self):
        # First call returns a short response; second returns a valid one
        client = MagicMock()
        client.call_claude.side_effect = ["short", GOOD_RESPONSE]
        result = researcher.execute(TOPIC, client)
        # Should have called call_claude twice
        assert client.call_claude.call_count == 2
        # Second call should include "at least 5 distinct points"
        second_call_user_msg = client.call_claude.call_args_list[1][0][1]
        assert "5 distinct points" in second_call_user_msg
        assert result == GOOD_RESPONSE

    def test_api_failure_raises_agent_execution_error(self):
        client = MagicMock()
        client.call_claude.side_effect = NetworkError("Connection failed")
        with pytest.raises(AgentExecutionError) as exc_info:
            researcher.execute(TOPIC, client)
        assert exc_info.value.agent_name == "Researcher"

    def test_agent_name_correct(self):
        assert researcher.AGENT_NAME == "Researcher"

    def test_min_response_length_constant(self):
        assert researcher.MIN_RESPONSE_LENGTH == 50

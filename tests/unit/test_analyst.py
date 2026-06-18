"""
Unit tests for the Analyst Agent (agents/analyst.py).
All API calls are mocked — no real network requests are made.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from unittest.mock import MagicMock

from agents import analyst
from exceptions import AgentExecutionError, NetworkError


NOTES = (
    "- Fact one about the topic\n"
    "- Fact two about the topic\n"
    "- Fact three about the topic"
)

GOOD_INSIGHTS = (
    "1. First key insight from the research\n"
    "2. Second key insight from the research\n"
    "3. Third key insight from the research"
)

PLACEHOLDER_NOTES = "Research data unavailable"


def _make_client(response: str) -> MagicMock:
    client = MagicMock()
    client.call_claude.return_value = response
    return client


class TestAnalyst:
    def test_returns_numbered_list_on_success(self):
        client = _make_client(GOOD_INSIGHTS)
        result = analyst.execute(NOTES, client)
        assert result == GOOD_INSIGHTS
        assert "1." in result

    def test_api_called_with_correct_system_prompt(self):
        client = _make_client(GOOD_INSIGHTS)
        analyst.execute(NOTES, client)
        call_args = client.call_claude.call_args
        system_prompt = call_args[0][0]
        assert "Analyst Agent" in system_prompt

    def test_research_notes_passed_as_user_message(self):
        client = _make_client(GOOD_INSIGHTS)
        analyst.execute(NOTES, client)
        call_args = client.call_claude.call_args
        user_message = call_args[0][1]
        assert NOTES == user_message

    def test_handles_empty_notes_without_crash(self):
        client = _make_client(GOOD_INSIGHTS)
        # Should not raise even with empty input
        result = analyst.execute("", client)
        assert result == GOOD_INSIGHTS

    def test_handles_placeholder_notes_without_crash(self):
        client = _make_client(GOOD_INSIGHTS)
        result = analyst.execute(PLACEHOLDER_NOTES, client)
        assert result == GOOD_INSIGHTS

    def test_api_failure_raises_agent_execution_error(self):
        client = MagicMock()
        client.call_claude.side_effect = NetworkError("Connection failed")
        with pytest.raises(AgentExecutionError) as exc_info:
            analyst.execute(NOTES, client)
        assert exc_info.value.agent_name == "Analyst"

    def test_agent_name_correct(self):
        assert analyst.AGENT_NAME == "Analyst"

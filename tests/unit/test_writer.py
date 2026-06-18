"""
Unit tests for the Writer Agent (agents/writer.py).
All API calls are mocked — no real network requests are made.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from unittest.mock import MagicMock

from agents import writer
from exceptions import AgentExecutionError, NetworkError


TOPIC = "Quantum Computing"

INSIGHTS = (
    "1. Quantum computers exploit superposition and entanglement\n"
    "2. They can solve certain problems exponentially faster than classical computers\n"
    "3. Error correction remains a significant technical challenge"
)

GOOD_REPORT = (
    "Quantum computing represents a new paradigm in computation.\n\n"
    "By harnessing the properties of quantum mechanics, these machines "
    "can perform certain calculations exponentially faster.\n\n"
    "However, significant technical challenges remain before widespread adoption.\n\n"
    "Error correction is the most pressing problem researchers are tackling today."
)

PLACEHOLDER_INSIGHTS = "Analysis unavailable"


def _make_client(response: str) -> MagicMock:
    client = MagicMock()
    client.call_claude.return_value = response
    return client


class TestWriter:
    def test_returns_multi_paragraph_report_on_success(self):
        client = _make_client(GOOD_REPORT)
        result = writer.execute(TOPIC, INSIGHTS, client)
        assert result == GOOD_REPORT
        paragraphs = [p for p in result.split("\n\n") if p.strip()]
        assert len(paragraphs) >= 3

    def test_api_called_with_correct_system_prompt(self):
        client = _make_client(GOOD_REPORT)
        writer.execute(TOPIC, INSIGHTS, client)
        call_args = client.call_claude.call_args
        system_prompt = call_args[0][0]
        assert "Writer Agent" in system_prompt

    def test_topic_and_insights_included_in_user_message(self):
        client = _make_client(GOOD_REPORT)
        writer.execute(TOPIC, INSIGHTS, client)
        call_args = client.call_claude.call_args
        user_message = call_args[0][1]
        assert TOPIC in user_message
        assert INSIGHTS in user_message

    def test_handles_placeholder_insights_without_crash(self):
        client = _make_client(GOOD_REPORT)
        result = writer.execute(TOPIC, PLACEHOLDER_INSIGHTS, client)
        assert result == GOOD_REPORT

    def test_handles_empty_insights_without_crash(self):
        client = _make_client(GOOD_REPORT)
        result = writer.execute(TOPIC, "", client)
        assert result == GOOD_REPORT

    def test_api_failure_raises_agent_execution_error(self):
        client = MagicMock()
        client.call_claude.side_effect = NetworkError("Connection failed")
        with pytest.raises(AgentExecutionError) as exc_info:
            writer.execute(TOPIC, INSIGHTS, client)
        assert exc_info.value.agent_name == "Writer"

    def test_agent_name_correct(self):
        assert writer.AGENT_NAME == "Writer"

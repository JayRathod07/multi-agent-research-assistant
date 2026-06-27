"""
Phase 2 integration tests — Researcher Agent with Web Search.

Patches agents.researcher.web_search (where it is imported-from in researcher.py)
so the mock replaces the name at the point of use.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from unittest.mock import MagicMock, patch


GOOD_RESEARCH_NOTES = (
    "- AI is transforming healthcare diagnostics\n"
    "- Machine learning models detect patterns in medical images\n"
    "- NLP enables better patient record management\n"
    "- AI reduces drug discovery timelines significantly\n"
    "- Regulatory challenges remain for clinical AI deployment"
)

SEARCH_RESULTS_MOCK = (
    "=== Web Search Results ===\n"
    "\n[1] AI Revolutionises Healthcare\n"
    "    AI systems now detect cancers earlier than traditional methods.\n"
    "    Source: https://example.com/ai-health\n"
    "\n[2] Machine Learning in Medicine\n"
    "    Deep learning models achieve radiologist-level accuracy.\n"
    "    Source: https://example.com/ml-med"
)

# Patch target: where web_search is used (imported into agents.researcher)
_SEARCH_PATCH = "agents.researcher.web_search"


class TestResearcherWithWebSearch:
    """Researcher agent behaviour when web search is available vs not."""

    def _make_api_client(self, response: str = GOOD_RESEARCH_NOTES) -> MagicMock:
        client = MagicMock()
        client.call_claude.return_value = response
        return client

    def test_uses_search_enriched_system_prompt_when_search_available(self):
        """When web_search returns results, SYSTEM_PROMPT_WITH_SEARCH is used."""
        api_client = self._make_api_client()
        with patch(_SEARCH_PATCH, return_value=SEARCH_RESULTS_MOCK):
            from agents import researcher
            researcher.execute("AI in healthcare", api_client)
            system_prompt = api_client.call_claude.call_args[0][0]
            # SYSTEM_PROMPT_WITH_SEARCH contains "web search results"
            assert "web search" in system_prompt.lower() or "search results" in system_prompt.lower()

    def test_uses_plain_system_prompt_when_no_search(self):
        """When web_search returns None, uses the plain SYSTEM_PROMPT (no search mention)."""
        api_client = self._make_api_client()
        with patch(_SEARCH_PATCH, return_value=None):
            from agents import researcher
            researcher.execute("AI in healthcare", api_client)
            system_prompt = api_client.call_claude.call_args[0][0]
            # Plain prompt should NOT mention web search results
            assert "web search results" not in system_prompt.lower()
            assert "Research Agent" in system_prompt

    def test_search_results_included_in_user_message_when_available(self):
        """Search results string is embedded in the user message to the LLM."""
        api_client = self._make_api_client()
        with patch(_SEARCH_PATCH, return_value=SEARCH_RESULTS_MOCK):
            from agents import researcher
            researcher.execute("AI in healthcare", api_client)
            user_message = api_client.call_claude.call_args[0][1]
            assert "Web Search Results" in user_message

    def test_topic_always_in_user_message_with_search(self):
        api_client = self._make_api_client()
        with patch(_SEARCH_PATCH, return_value=SEARCH_RESULTS_MOCK):
            from agents import researcher
            researcher.execute("quantum computing", api_client)
            user_message = api_client.call_claude.call_args[0][1]
            assert "quantum computing" in user_message

    def test_topic_always_in_user_message_without_search(self):
        api_client = self._make_api_client()
        with patch(_SEARCH_PATCH, return_value=None):
            from agents import researcher
            researcher.execute("quantum computing", api_client)
            user_message = api_client.call_claude.call_args[0][1]
            assert "quantum computing" in user_message

    def test_returns_response_string_with_search(self):
        api_client = self._make_api_client(GOOD_RESEARCH_NOTES)
        with patch(_SEARCH_PATCH, return_value=SEARCH_RESULTS_MOCK):
            from agents import researcher
            result = researcher.execute("ML trends", api_client)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_returns_response_string_without_search(self):
        api_client = self._make_api_client(GOOD_RESEARCH_NOTES)
        with patch(_SEARCH_PATCH, return_value=None):
            from agents import researcher
            result = researcher.execute("ML trends", api_client)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_search_returning_none_does_not_crash_researcher(self):
        """Graceful degradation when search is unavailable."""
        api_client = self._make_api_client()
        with patch(_SEARCH_PATCH, return_value=None):
            from agents import researcher
            result = researcher.execute("topic with no search", api_client)
            assert result is not None


class TestResearcherWebSearchPipelineIntegration:
    """End-to-end pipeline with web search mocked at agent level."""

    def _make_full_mock_client(self) -> MagicMock:
        client = MagicMock()

        def side_effect(system_prompt, user_message, max_tokens=0):
            if "Research Agent" in system_prompt:
                return GOOD_RESEARCH_NOTES
            elif "Analyst Agent" in system_prompt:
                return "1. Insight one\n2. Insight two\n3. Insight three"
            elif "Writer Agent" in system_prompt:
                return "Para one.\n\nPara two.\n\nPara three."
            return "response"

        client.call_claude.side_effect = side_effect
        return client

    def test_pipeline_succeeds_with_web_search_enabled(self):
        mock_client = self._make_full_mock_client()
        with patch("orchestrator.APIClient", return_value=mock_client), \
             patch("orchestrator.load_dotenv"), \
             patch(_SEARCH_PATCH, return_value=SEARCH_RESULTS_MOCK):
            from orchestrator import run_pipeline
            result = run_pipeline("AI in medicine")
            assert result.is_complete_success
            assert not result.research_notes.is_placeholder

    def test_pipeline_succeeds_without_web_search(self):
        mock_client = self._make_full_mock_client()
        with patch("orchestrator.APIClient", return_value=mock_client), \
             patch("orchestrator.load_dotenv"), \
             patch(_SEARCH_PATCH, return_value=None):
            from orchestrator import run_pipeline
            result = run_pipeline("climate change")
            assert result.is_complete_success
            assert not result.research_notes.is_placeholder

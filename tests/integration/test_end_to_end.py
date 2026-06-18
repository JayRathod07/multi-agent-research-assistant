"""
Integration tests for the full pipeline (Researcher → Analyst → Writer).
All Anthropic API calls are mocked — no real network requests are made.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from unittest.mock import MagicMock, patch

from exceptions import AgentExecutionError, NetworkError
from models import PipelineResult, ResearchNotes, Insights, FinalReport


# ── Canonical mock responses ──────────────────────────────────────────────────

RESEARCH_NOTES = (
    "- AI is transforming healthcare diagnostics\n"
    "- Machine learning models detect patterns in medical images\n"
    "- Natural language processing assists in patient records analysis\n"
    "- AI drug discovery cuts development time significantly\n"
    "- Ethical and regulatory challenges remain for clinical AI"
)

INSIGHTS = (
    "1. AI accelerates diagnosis through pattern recognition in imaging\n"
    "2. NLP streamlines patient data management and record analysis\n"
    "3. Regulatory and ethical frameworks must keep pace with AI advances"
)

REPORT = (
    "Artificial Intelligence is reshaping modern healthcare.\n\n"
    "By analysing medical images with high precision, AI tools are helping "
    "doctors detect diseases earlier and more accurately than ever.\n\n"
    "Natural language processing is also enabling smarter management of "
    "patient records, reducing administrative burdens.\n\n"
    "However, regulatory bodies and ethicists must work together to ensure "
    "these powerful technologies are deployed safely and fairly."
)


def _make_mock_client(
    researcher_resp=RESEARCH_NOTES,
    analyst_resp=INSIGHTS,
    writer_resp=REPORT,
):
    """Create a mock APIClient whose call_claude() dispatches by system prompt."""
    client = MagicMock()

    def side_effect(system_prompt, user_message, max_tokens=0):
        if "Research Agent" in system_prompt:
            return researcher_resp
        elif "Analyst Agent" in system_prompt:
            return analyst_resp
        elif "Writer Agent" in system_prompt:
            return writer_resp
        return "unexpected"

    client.call_claude.side_effect = side_effect
    return client


# ── Helper: patch APIClient and dotenv inside orchestrator ────────────────────

def _run_pipeline_with_mock(topic: str, mock_client):
    """Patch APIClient + load_dotenv and run the orchestrator pipeline."""
    with patch("orchestrator.APIClient", return_value=mock_client), \
         patch("orchestrator.load_dotenv"):
        from orchestrator import run_pipeline
        return run_pipeline(topic)


# ── Happy-path test ───────────────────────────────────────────────────────────

class TestHappyPath:
    def test_all_three_agents_succeed(self):
        client = _make_mock_client()
        result = _run_pipeline_with_mock("AI in Healthcare", client)

        assert isinstance(result, PipelineResult)
        assert result.is_complete_success
        assert result.failed_agents == []
        assert result.errors == []

    def test_research_notes_content_correct(self):
        client = _make_mock_client()
        result = _run_pipeline_with_mock("AI in Healthcare", client)
        assert not result.research_notes.is_placeholder
        assert RESEARCH_NOTES.strip() == result.research_notes.content

    def test_insights_content_correct(self):
        client = _make_mock_client()
        result = _run_pipeline_with_mock("AI in Healthcare", client)
        assert not result.insights.is_placeholder
        assert "1." in result.insights.content

    def test_final_report_content_correct(self):
        client = _make_mock_client()
        result = _run_pipeline_with_mock("AI in Healthcare", client)
        assert not result.final_report.is_placeholder
        paragraphs = [p for p in result.final_report.content.split("\n\n") if p.strip()]
        assert len(paragraphs) >= 3

    def test_all_three_agents_called(self):
        client = _make_mock_client()
        _run_pipeline_with_mock("AI in Healthcare", client)
        assert client.call_claude.call_count == 3

    def test_topic_stored_in_result(self):
        client = _make_mock_client()
        result = _run_pipeline_with_mock("Quantum Computing", client)
        assert result.topic == "Quantum Computing"


# ── Researcher failure ────────────────────────────────────────────────────────

class TestResearcherFailure:
    def _client_where_researcher_fails(self):
        client = MagicMock()
        call_count = {"n": 0}

        def side_effect(system_prompt, user_message, max_tokens=0):
            if "Research Agent" in system_prompt:
                call_count["n"] += 1
                raise NetworkError("Connection failed")
            elif "Analyst Agent" in system_prompt:
                return INSIGHTS
            elif "Writer Agent" in system_prompt:
                return REPORT
        client.call_claude.side_effect = side_effect
        return client

    def test_pipeline_continues_with_placeholder(self):
        client = self._client_where_researcher_fails()
        result = _run_pipeline_with_mock("Test topic", client)
        assert result.research_notes.is_placeholder
        assert "Researcher" in result.failed_agents

    def test_analyst_and_writer_still_run(self):
        client = self._client_where_researcher_fails()
        result = _run_pipeline_with_mock("Test topic", client)
        # Analyst and Writer should succeed
        assert result.execution_status.get("Analyst") is True
        assert result.execution_status.get("Writer") is True

    def test_errors_list_populated(self):
        client = self._client_where_researcher_fails()
        result = _run_pipeline_with_mock("Test topic", client)
        assert len(result.errors) >= 1
        assert any("Researcher" in e for e in result.errors)


# ── Analyst failure ───────────────────────────────────────────────────────────

class TestAnalystFailure:
    def _client_where_analyst_fails(self):
        client = MagicMock()

        def side_effect(system_prompt, user_message, max_tokens=0):
            if "Research Agent" in system_prompt:
                return RESEARCH_NOTES
            elif "Analyst Agent" in system_prompt:
                raise NetworkError("Connection failed")
            elif "Writer Agent" in system_prompt:
                return REPORT
        client.call_claude.side_effect = side_effect
        return client

    def test_pipeline_continues_with_placeholder_insights(self):
        client = self._client_where_analyst_fails()
        result = _run_pipeline_with_mock("Test topic", client)
        assert result.insights.is_placeholder
        assert "Analyst" in result.failed_agents

    def test_researcher_succeeded(self):
        client = self._client_where_analyst_fails()
        result = _run_pipeline_with_mock("Test topic", client)
        assert result.execution_status.get("Researcher") is True

    def test_writer_still_runs(self):
        client = self._client_where_analyst_fails()
        result = _run_pipeline_with_mock("Test topic", client)
        assert result.execution_status.get("Writer") is True


# ── Writer failure ────────────────────────────────────────────────────────────

class TestWriterFailure:
    def _client_where_writer_fails(self):
        client = MagicMock()

        def side_effect(system_prompt, user_message, max_tokens=0):
            if "Research Agent" in system_prompt:
                return RESEARCH_NOTES
            elif "Analyst Agent" in system_prompt:
                return INSIGHTS
            elif "Writer Agent" in system_prompt:
                raise NetworkError("Connection failed")
        client.call_claude.side_effect = side_effect
        return client

    def test_partial_results_returned(self):
        client = self._client_where_writer_fails()
        result = _run_pipeline_with_mock("Test topic", client)
        assert result.final_report.is_placeholder
        assert "Writer" in result.failed_agents

    def test_researcher_and_analyst_succeeded(self):
        client = self._client_where_writer_fails()
        result = _run_pipeline_with_mock("Test topic", client)
        assert result.execution_status.get("Researcher") is True
        assert result.execution_status.get("Analyst") is True


# ── Input validation ──────────────────────────────────────────────────────────

class TestInputValidation:
    def test_empty_topic_raises(self):
        from exceptions import ValidationError
        client = _make_mock_client()
        with patch("orchestrator.APIClient", return_value=client), \
             patch("orchestrator.load_dotenv"):
            from orchestrator import run_pipeline
            with pytest.raises((ValidationError, ValueError)):
                run_pipeline("")

    def test_whitespace_topic_raises(self):
        from exceptions import ValidationError
        client = _make_mock_client()
        with patch("orchestrator.APIClient", return_value=client), \
             patch("orchestrator.load_dotenv"):
            from orchestrator import run_pipeline
            with pytest.raises((ValidationError, ValueError)):
                run_pipeline("   ")

    def test_long_topic_raises(self):
        from exceptions import ValidationError
        client = _make_mock_client()
        with patch("orchestrator.APIClient", return_value=client), \
             patch("orchestrator.load_dotenv"):
            from orchestrator import run_pipeline
            with pytest.raises((ValidationError, ValueError)):
                run_pipeline("a" * 501)

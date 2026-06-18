"""
Unit tests for Topic, ResearchNotes, Insights, FinalReport, PipelineResult
data models defined in models.py.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from exceptions import ValidationError
from models import (
    FinalReport,
    Insights,
    PipelineResult,
    ResearchNotes,
    Topic,
)


# ── Topic validation ──────────────────────────────────────────────────────────

class TestTopic:
    def test_valid_topic_accepted(self):
        t = Topic("Artificial Intelligence")
        assert t.value == "Artificial Intelligence"

    def test_empty_topic_raises(self):
        with pytest.raises(ValidationError, match="empty"):
            Topic("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError):
            Topic("   ")

    def test_tab_only_raises(self):
        with pytest.raises(ValidationError):
            Topic("\t\t\t")

    def test_topic_is_trimmed(self):
        t = Topic("  AI Ethics  ")
        assert t.value == "AI Ethics"

    def test_exactly_500_chars_accepted(self):
        t = Topic("a" * 500)
        assert len(t.value) == 500

    def test_501_chars_raises(self):
        with pytest.raises(ValidationError, match="500"):
            Topic("a" * 501)

    def test_str_returns_value(self):
        t = Topic("Climate Change")
        assert str(t) == "Climate Change"

    def test_unicode_topic_accepted(self):
        t = Topic("人工智能")
        assert t.value == "人工智能"


# ── ResearchNotes ─────────────────────────────────────────────────────────────

class TestResearchNotes:
    def test_valid_output_accepted(self):
        content = "- Fact one\n- Fact two\n- Fact three and more details here"
        rn = ResearchNotes.from_agent_output(content)
        assert not rn.is_placeholder
        assert rn.content == content

    def test_none_output_gives_placeholder(self):
        rn = ResearchNotes.from_agent_output(None)
        assert rn.is_placeholder
        assert rn.content == ResearchNotes.PLACEHOLDER

    def test_empty_string_gives_placeholder(self):
        rn = ResearchNotes.from_agent_output("")
        assert rn.is_placeholder

    def test_short_output_gives_placeholder(self):
        # < 50 chars
        rn = ResearchNotes.from_agent_output("- Only one tiny fact")
        assert rn.is_placeholder

    def test_exactly_50_chars_accepted(self):
        content = "- " + "x" * 48
        rn = ResearchNotes.from_agent_output(content)
        assert not rn.is_placeholder

    def test_placeholder_constant_is_string(self):
        assert isinstance(ResearchNotes.PLACEHOLDER, str)
        assert len(ResearchNotes.PLACEHOLDER) > 0


# ── Insights ─────────────────────────────────────────────────────────────────

class TestInsights:
    def test_numbered_list_accepted(self):
        content = "1. First insight\n2. Second insight\n3. Third insight"
        ins = Insights.from_agent_output(content)
        assert not ins.is_placeholder
        assert "1." in ins.content

    def test_none_gives_placeholder(self):
        ins = Insights.from_agent_output(None)
        assert ins.is_placeholder

    def test_empty_string_gives_placeholder(self):
        ins = Insights.from_agent_output("")
        assert ins.is_placeholder

    def test_no_numbered_lines_gives_placeholder(self):
        ins = Insights.from_agent_output("Just some text without numbers")
        assert ins.is_placeholder

    def test_placeholder_constant_is_string(self):
        assert isinstance(Insights.PLACEHOLDER, str)

    def test_is_valid_format_detects_digit_prefix(self):
        assert Insights._is_valid_format("1. Something\n2. Another")
        assert not Insights._is_valid_format("- bullet only")
        assert not Insights._is_valid_format("")


# ── FinalReport ───────────────────────────────────────────────────────────────

class TestFinalReport:
    def test_valid_output_accepted(self):
        content = "Para one.\n\nPara two.\n\nPara three."
        fr = FinalReport.from_agent_output(content)
        assert not fr.is_placeholder
        assert fr.content == content

    def test_none_gives_placeholder(self):
        fr = FinalReport.from_agent_output(None)
        assert fr.is_placeholder
        assert "insufficient data" in fr.content.lower()

    def test_empty_string_gives_placeholder(self):
        fr = FinalReport.from_agent_output("")
        assert fr.is_placeholder

    def test_whitespace_only_gives_placeholder(self):
        fr = FinalReport.from_agent_output("   ")
        assert fr.is_placeholder


# ── PipelineResult ────────────────────────────────────────────────────────────

class TestPipelineResult:
    def _make_result(self, statuses: dict) -> PipelineResult:
        return PipelineResult(
            topic="Test topic",
            research_notes=ResearchNotes(content="notes"),
            insights=Insights(content="insights"),
            final_report=FinalReport(content="report"),
            execution_status=statuses,
            errors=[],
        )

    def test_complete_success(self):
        r = self._make_result(
            {"Researcher": True, "Analyst": True, "Writer": True}
        )
        assert r.is_complete_success is True
        assert r.failed_agents == []

    def test_one_failure(self):
        r = self._make_result(
            {"Researcher": False, "Analyst": True, "Writer": True}
        )
        assert r.is_complete_success is False
        assert "Researcher" in r.failed_agents

    def test_all_failures(self):
        r = self._make_result(
            {"Researcher": False, "Analyst": False, "Writer": False}
        )
        assert len(r.failed_agents) == 3

    def test_empty_execution_status(self):
        r = self._make_result({})
        assert r.is_complete_success is False

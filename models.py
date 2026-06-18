"""
Data models for the Multi-Agent Research Assistant pipeline.

Models:
- Topic          : Validated user input
- ResearchNotes  : Output of Researcher Agent
- Insights       : Output of Analyst Agent
- FinalReport    : Output of Writer Agent
- PipelineResult : Aggregated result of a full pipeline run
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from exceptions import ValidationError


# ---------------------------------------------------------------------------
# Input model
# ---------------------------------------------------------------------------

@dataclass
class Topic:
    """Validated user-provided research topic."""

    value: str

    def __post_init__(self) -> None:
        """Validate and normalise the topic string on creation."""
        # Trim surrounding whitespace
        self.value = self.value.strip()

        if not self.value:
            raise ValidationError(
                "Topic cannot be empty. Please enter a valid research topic."
            )

        if len(self.value) > 500:
            raise ValidationError(
                "Topic exceeds 500 characters. Please shorten your topic."
            )

    def __str__(self) -> str:
        return self.value


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

@dataclass
class ResearchNotes:
    """Bullet-point research findings produced by the Researcher Agent."""

    content: str
    is_placeholder: bool = False

    PLACEHOLDER: str = "Research data unavailable"

    @classmethod
    def from_agent_output(cls, output: Optional[str]) -> "ResearchNotes":
        """
        Create a ResearchNotes object from raw agent output.
        Falls back to placeholder when output is None, empty, or too short.
        """
        if not output or len(output.strip()) < 50:
            return cls(content=cls.PLACEHOLDER, is_placeholder=True)
        return cls(content=output.strip())


@dataclass
class Insights:
    """Numbered list of key insights produced by the Analyst Agent."""

    content: str
    is_placeholder: bool = False

    PLACEHOLDER: str = "Analysis unavailable"

    @classmethod
    def from_agent_output(cls, output: Optional[str]) -> "Insights":
        """
        Create an Insights object from raw agent output.
        Falls back to placeholder when output is None, empty, or malformed.
        """
        if not output or not cls._is_valid_format(output):
            return cls(content=cls.PLACEHOLDER, is_placeholder=True)
        return cls(content=output.strip())

    @staticmethod
    def _is_valid_format(output: str) -> bool:
        """Return True if output contains at least one numbered-list line."""
        lines = [line.strip() for line in output.split("\n") if line.strip()]
        return any(line and line[0].isdigit() for line in lines)


@dataclass
class FinalReport:
    """Polished 3-4 paragraph report produced by the Writer Agent."""

    content: str
    is_placeholder: bool = False

    @classmethod
    def from_agent_output(cls, output: Optional[str]) -> "FinalReport":
        """
        Create a FinalReport object from raw agent output.
        Falls back to a placeholder message when output is None or empty.
        """
        if not output or not output.strip():
            return cls(
                content="Report generation failed due to insufficient data.",
                is_placeholder=True,
            )
        return cls(content=output.strip())


# ---------------------------------------------------------------------------
# Pipeline result
# ---------------------------------------------------------------------------

@dataclass
class PipelineResult:
    """Aggregated output of a complete pipeline run."""

    topic: str
    research_notes: ResearchNotes
    insights: Insights
    final_report: FinalReport
    execution_status: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    @property
    def is_complete_success(self) -> bool:
        """Return True only when every agent completed without failure."""
        return bool(self.execution_status) and all(
            self.execution_status.values()
        )

    @property
    def failed_agents(self) -> List[str]:
        """Return a list of agent names that failed during this run."""
        return [
            name
            for name, success in self.execution_status.items()
            if not success
        ]

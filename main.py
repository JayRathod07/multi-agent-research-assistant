"""
Multi-Agent Research Assistant — CLI Entry Point.

Usage:
    python main.py

The user is prompted to enter a research topic. The pipeline runs three
AI agents (Researcher, Analyst, Writer) in sequence and displays all
intermediate outputs plus the final report.
"""

import os
import sys

from dotenv import load_dotenv

from error_messages import ERROR_MESSAGES
from exceptions import AuthenticationError, ValidationError
from orchestrator import run_pipeline
from utils.logging_config import setup_logging

# ── Suppress console logging — keep terminal output clean for the user ──────
# (All log messages still go to pipeline.log)
load_dotenv()
setup_logging(log_level="WARNING", log_file="pipeline.log")

# ── Display helpers ──────────────────────────────────────────────────────────

_WIDTH = 62
_DIVIDER = "=" * _WIDTH


def _section(title: str, content: str) -> None:
    """Print a clearly labelled output section to the terminal."""
    print(f"\n{_DIVIDER}")
    print(f" {title}")
    print(_DIVIDER)
    print(content)


def _banner() -> None:
    print(_DIVIDER)
    print(" Multi-Agent Research Assistant")
    print(_DIVIDER)


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    """CLI entry point: prompt → validate → run pipeline → display results."""
    _banner()

    # ── Get topic from user ──────────────────────────────────────────────────
    try:
        topic_input = input("\nEnter a research topic: ").strip()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Exiting.")
        sys.exit(0)

    # ── Basic pre-validation (before hitting the orchestrator) ───────────────
    if not topic_input:
        print(f"\n{ERROR_MESSAGES['empty_topic']}")
        sys.exit(1)

    if len(topic_input) > 500:
        print(f"\n{ERROR_MESSAGES['topic_too_long']}")
        sys.exit(1)

    print(f"\n{'─' * _WIDTH}")
    print(" Running pipeline — this may take 10–20 seconds…")
    print(f"{'─' * _WIDTH}")

    # ── Execute pipeline ─────────────────────────────────────────────────────
    try:
        print("\n[1/3] Researcher  — gathering information…", flush=True)
        # We import here so the progress messages appear before the API calls
        result = None

        # Run pipeline (blocking — agents execute sequentially inside)
        try:
            # Patch stdout progress via simple print then override
            result = _run_with_progress(topic_input)
        except ValidationError as exc:
            print(f"\n❌ Invalid topic: {exc}")
            sys.exit(1)
        except AuthenticationError as exc:
            print(f"\n❌ {exc}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nInterrupted during pipeline execution. Exiting.")
        sys.exit(0)

    if result is None:
        print("\n❌ Pipeline did not return a result. Check pipeline.log for details.")
        sys.exit(1)

    # ── Display results ──────────────────────────────────────────────────────
    print(f"\n\n{'=' * _WIDTH}")
    print(" RESULTS")

    _section("📋  RESEARCH NOTES", result.research_notes.content)
    _section("💡  KEY INSIGHTS", result.insights.content)
    _section("📄  FINAL REPORT", result.final_report.content)

    # ── Show any errors / partial-failure warnings ───────────────────────────
    if result.errors:
        print(f"\n{'-' * _WIDTH}")
        print(" ⚠️  Warnings / Errors:")
        for err in result.errors:
            print(f"   • {err}")

    if result.failed_agents:
        print(f"\n   ℹ️  Failed agents: {', '.join(result.failed_agents)}")
        print("   Partial results shown above. See pipeline.log for details.")
    else:
        print(f"\n✅ Pipeline completed successfully!")

    print(f"\n{'=' * _WIDTH}\n")


def _run_with_progress(topic_input: str):
    """
    Run the pipeline with accurate step-by-step progress messages.

    Messages are printed BETWEEN actual agent calls so the user sees
    each step appear as it begins, not all at once upfront.
    """
    # Import agents + orchestrator internals to intercept step boundaries
    from dotenv import load_dotenv
    from api_client import APIClient
    from agents import analyst, researcher, writer
    from models import FinalReport, Insights, PipelineResult, ResearchNotes, Topic
    from error_messages import ERROR_MESSAGES
    from exceptions import AgentExecutionError, AuthenticationError

    load_dotenv()
    topic_obj = Topic(value=topic_input)
    topic_str = topic_obj.value

    api_client = APIClient()
    execution_status: dict = {}
    errors: list = []

    # Step 1 — Researcher (already printed in main)
    raw_notes = None
    try:
        raw_notes = researcher.execute(topic_str, api_client)
        execution_status["Researcher"] = True
    except AgentExecutionError as exc:
        execution_status["Researcher"] = False
        errors.append(ERROR_MESSAGES["agent_failed"].format(agent_name="Researcher"))

    research_notes_obj = ResearchNotes.from_agent_output(raw_notes)

    # Step 2 — Analyst
    print("\n[2/3] Analyst     — extracting insights…", flush=True)
    raw_insights = None
    try:
        raw_insights = analyst.execute(research_notes_obj.content, api_client)
        execution_status["Analyst"] = True
    except AgentExecutionError as exc:
        execution_status["Analyst"] = False
        errors.append(ERROR_MESSAGES["agent_failed"].format(agent_name="Analyst"))

    insights_obj = Insights.from_agent_output(raw_insights)

    # Step 3 — Writer
    print("[3/3] Writer      — generating report…", flush=True)
    raw_report = None
    try:
        raw_report = writer.execute(topic_str, insights_obj.content, api_client)
        execution_status["Writer"] = True
    except AgentExecutionError as exc:
        execution_status["Writer"] = False
        errors.append(ERROR_MESSAGES["agent_failed"].format(agent_name="Writer"))

    final_report_obj = FinalReport.from_agent_output(raw_report)

    return PipelineResult(
        topic=topic_str,
        research_notes=research_notes_obj,
        insights=insights_obj,
        final_report=final_report_obj,
        execution_status=execution_status,
        errors=errors,
    )


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()

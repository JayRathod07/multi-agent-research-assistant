"""
Orchestrator for the Multi-Agent Research Assistant.

Coordinates the sequential execution of three agents:
  Researcher → Analyst → Writer

State is held in Python variables for Phase 1 (no database).
Graceful degradation: if any agent fails, a placeholder is substituted
and the pipeline continues so partial results are always returned.
"""

import os

from dotenv import load_dotenv

from agents import analyst, researcher, writer
from api_client import APIClient
from error_messages import ERROR_MESSAGES
from exceptions import AgentExecutionError, AuthenticationError
from models import (
    FinalReport,
    Insights,
    PipelineResult,
    ResearchNotes,
    Topic,
)
from utils.logging_config import get_logger

logger = get_logger(__name__)


def run_pipeline(topic_input: str) -> PipelineResult:
    """
    Execute the full Researcher → Analyst → Writer pipeline.

    Args:
        topic_input: Raw topic string provided by the user.

    Returns:
        PipelineResult containing all outputs and execution status.

    Raises:
        ValueError:          If the topic is empty, whitespace-only, or >500 chars.
        AuthenticationError: If the API key is missing/invalid (non-retryable).
    """
    # -----------------------------------------------------------------------
    # 1. Validate & normalise topic
    # -----------------------------------------------------------------------
    topic_obj = Topic(value=topic_input)   # raises ValueError on bad input
    topic_str = topic_obj.value

    logger.info("Pipeline starting for topic: %.80s…", topic_str)

    # -----------------------------------------------------------------------
    # 2. Initialise shared state
    # -----------------------------------------------------------------------
    execution_status: dict = {}
    errors: list = []

    # -----------------------------------------------------------------------
    # 3. Initialise API client
    # -----------------------------------------------------------------------
    load_dotenv()
    api_client = APIClient()

    # -----------------------------------------------------------------------
    # 4. Researcher Agent
    # -----------------------------------------------------------------------
    raw_notes: str | None = None
    try:
        raw_notes = researcher.execute(topic_str, api_client)
        execution_status["Researcher"] = True
        logger.info("Researcher completed successfully.")
    except AgentExecutionError as exc:
        execution_status["Researcher"] = False
        error_msg = ERROR_MESSAGES["agent_failed"].format(agent_name="Researcher")
        errors.append(error_msg)
        logger.error("Researcher failed: %s", exc)

    research_notes_obj = ResearchNotes.from_agent_output(raw_notes)
    if research_notes_obj.is_placeholder:
        logger.warning(
            "Using placeholder for Research Notes: %s", research_notes_obj.content
        )

    # -----------------------------------------------------------------------
    # 5. Analyst Agent
    # -----------------------------------------------------------------------
    raw_insights: str | None = None
    try:
        raw_insights = analyst.execute(research_notes_obj.content, api_client)
        execution_status["Analyst"] = True
        logger.info("Analyst completed successfully.")
    except AgentExecutionError as exc:
        execution_status["Analyst"] = False
        error_msg = ERROR_MESSAGES["agent_failed"].format(agent_name="Analyst")
        errors.append(error_msg)
        logger.error("Analyst failed: %s", exc)

    insights_obj = Insights.from_agent_output(raw_insights)
    if insights_obj.is_placeholder:
        logger.warning(
            "Using placeholder for Insights: %s", insights_obj.content
        )

    # -----------------------------------------------------------------------
    # 6. Writer Agent
    # -----------------------------------------------------------------------
    raw_report: str | None = None
    try:
        raw_report = writer.execute(topic_str, insights_obj.content, api_client)
        execution_status["Writer"] = True
        logger.info("Writer completed successfully.")
    except AgentExecutionError as exc:
        execution_status["Writer"] = False
        error_msg = ERROR_MESSAGES["agent_failed"].format(agent_name="Writer")
        errors.append(error_msg)
        logger.error("Writer failed: %s", exc)

    final_report_obj = FinalReport.from_agent_output(raw_report)
    if final_report_obj.is_placeholder:
        logger.warning(
            "Using placeholder for Final Report: %s", final_report_obj.content
        )

    # -----------------------------------------------------------------------
    # 7. Assemble result
    # -----------------------------------------------------------------------
    result = PipelineResult(
        topic=topic_str,
        research_notes=research_notes_obj,
        insights=insights_obj,
        final_report=final_report_obj,
        execution_status=execution_status,
        errors=errors,
    )

    if result.is_complete_success:
        logger.info("Pipeline completed successfully for topic: %.80s…", topic_str)
    else:
        logger.warning(
            "Pipeline completed with failures. Failed agents: %s",
            result.failed_agents,
        )

    # State is released when this function returns (all locals go out of scope)
    return result

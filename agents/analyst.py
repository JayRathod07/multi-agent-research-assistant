"""
Analyst Agent for the Multi-Agent Research Assistant.

Responsibility: Synthesize research notes into exactly 3 key insights.

System prompt (exact, as specified):
  "You are an Analyst Agent. You receive raw research notes. Identify the
   3 most important insights, patterns, or implications.
   Output as a numbered list."

Error handling:
  - Empty / placeholder research notes are handled gracefully: the agent still
    runs and the LLM will produce insights noting lack of data.
  - API failure after retry raises AgentExecutionError.
"""

from api_client import APIClient
from exceptions import AgentExecutionError
from retry_logic import call_with_retry
from utils.logging_config import get_logger

logger = get_logger(__name__)

AGENT_NAME = "Analyst"

SYSTEM_PROMPT = (
    "You are an Analyst Agent. You receive raw research notes. "
    "Identify the 3 most important insights, patterns, or implications. "
    "Output as a numbered list."
)


def execute(research_notes: str, api_client: APIClient) -> str:
    """
    Analyse research notes and return 3 numbered insights.

    Args:
        research_notes: Output from the Researcher Agent (may be placeholder).
        api_client:     Configured Claude API client.

    Returns:
        Numbered list of key insights as a string.

    Raises:
        AgentExecutionError: If the API call fails after retry.
    """
    logger.info(
        "[%s] Starting analysis. Input length: %d chars.",
        AGENT_NAME,
        len(research_notes),
    )

    # Log a warning if we're working with placeholder data
    if not research_notes or research_notes.strip() in ("", "Research data unavailable"):
        logger.warning(
            "[%s] Received empty or placeholder research notes. "
            "Analysis will reflect lack of data.",
            AGENT_NAME,
        )

    try:
        response = call_with_retry(
            func=lambda: api_client.call_claude(SYSTEM_PROMPT, research_notes),
            max_retries=1,
            backoff_seconds=2.0,
            context=AGENT_NAME,
        )
    except Exception as exc:
        raise AgentExecutionError(
            agent_name=AGENT_NAME,
            message="API call failed after retry.",
            original_error=exc,
        ) from exc

    logger.info(
        "[%s] Completed. Response length: %d chars.", AGENT_NAME, len(response)
    )
    return response

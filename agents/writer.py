"""
Writer Agent for the Multi-Agent Research Assistant.

Responsibility: Produce a polished 3-4 paragraph report from topic + insights.

System prompt (exact, as specified):
  "You are a Writer Agent. You receive a topic and key insights. Write a
   short, clear report (3-4 paragraphs) for a non-expert reader, based
   ONLY on the given insights."

Error handling:
  - Placeholder / empty insights are still passed to the LLM; the system
    prompt instructs it to note "insufficient data" rather than invent content.
  - API failure after retry raises AgentExecutionError.
"""

from api_client import APIClient
from exceptions import AgentExecutionError
from retry_logic import call_with_retry
from utils.logging_config import get_logger

logger = get_logger(__name__)

AGENT_NAME = "Writer"

SYSTEM_PROMPT = (
    "You are a Writer Agent. You receive a topic and key insights. "
    "Write a short, clear report (3-4 paragraphs) for a non-expert reader, "
    "based ONLY on the given insights."
)


def execute(topic: str, insights: str, api_client: APIClient) -> str:
    """
    Generate a final 3-4 paragraph report from the topic and insights.

    Args:
        topic:      Original research topic.
        insights:   Output from the Analyst Agent (may be placeholder).
        api_client: Configured Claude API client.

    Returns:
        Final report as a multi-paragraph string.

    Raises:
        AgentExecutionError: If the API call fails after retry.
    """
    logger.info("[%s] Starting report generation for topic: %.80s…", AGENT_NAME, topic)

    # Log a warning if we're working with placeholder insights
    if not insights or insights.strip() in ("", "Analysis unavailable"):
        logger.warning(
            "[%s] Received empty or placeholder insights. "
            "Report will note insufficient data.",
            AGENT_NAME,
        )

    # Compose the user message combining topic and insights
    user_message = (
        f"Topic: {topic}\n\n"
        f"Key Insights:\n{insights}"
    )

    try:
        response = call_with_retry(
            func=lambda: api_client.call_claude(SYSTEM_PROMPT, user_message),
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

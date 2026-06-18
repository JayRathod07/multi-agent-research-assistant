"""
Researcher Agent for the Multi-Agent Research Assistant.

Responsibility: Gather key facts, trends, and data points about a topic.

System prompt (exact, as specified):
  "You are a Research Agent. Given a topic, list the key facts, trends,
   and data points relevant to it. Be factual and concise.
   Output as a bullet list."

Retry behaviour:
  - If the API call fails → call_with_retry handles 1 automatic retry.
  - If the response is too short (< 50 chars) → retry once with an enhanced
    prompt requesting "at least 5 distinct points".
"""

from api_client import APIClient
from exceptions import AgentExecutionError
from retry_logic import call_with_retry
from utils.logging_config import get_logger

logger = get_logger(__name__)

AGENT_NAME = "Researcher"

SYSTEM_PROMPT = (
    "You are a Research Agent. Given a topic, list the key facts, trends, "
    "and data points relevant to it. Be factual and concise. "
    "Output as a bullet list."
)

MIN_RESPONSE_LENGTH = 50


def execute(topic: str, api_client: APIClient) -> str:
    """
    Generate bullet-point research notes for the given topic.

    Args:
        topic:      Research subject (validated, trimmed string).
        api_client: Configured Claude API client.

    Returns:
        Bullet-point research notes as a string.

    Raises:
        AgentExecutionError: If the API call fails after retry.
    """
    logger.info("[%s] Starting research on topic: %.80s…", AGENT_NAME, topic)

    try:
        response = call_with_retry(
            func=lambda: api_client.call_claude(SYSTEM_PROMPT, topic),
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

    # --- Quality check: if response is too short, retry with enhanced prompt ---
    if len(response.strip()) < MIN_RESPONSE_LENGTH:
        logger.warning(
            "[%s] Response too short (%d chars). Retrying with enhanced prompt.",
            AGENT_NAME,
            len(response.strip()),
        )
        enhanced_prompt = f"List at least 5 distinct points about: {topic}"
        try:
            response = call_with_retry(
                func=lambda: api_client.call_claude(SYSTEM_PROMPT, enhanced_prompt),
                max_retries=1,
                backoff_seconds=2.0,
                context=f"{AGENT_NAME}-enhanced",
            )
        except Exception as exc:
            raise AgentExecutionError(
                agent_name=AGENT_NAME,
                message="Enhanced-prompt retry also failed.",
                original_error=exc,
            ) from exc

    logger.info(
        "[%s] Completed. Response length: %d chars.", AGENT_NAME, len(response)
    )
    return response

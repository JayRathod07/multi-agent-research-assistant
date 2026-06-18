"""
Researcher Agent for the Multi-Agent Research Assistant.

Responsibility: Gather key facts, trends, and data points about a topic.

Phase 2 upgrade: real web search via Tavily is prepended to the LLM prompt
when TAVILY_API_KEY is configured. Falls back to LLM-only mode if the key
is absent (identical to Phase 1 behaviour — no breaking change).

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
from tools.search import web_search
from utils.logging_config import get_logger

logger = get_logger(__name__)

AGENT_NAME = "Researcher"

SYSTEM_PROMPT = (
    "You are a Research Agent. Given a topic, list the key facts, trends, "
    "and data points relevant to it. Be factual and concise. "
    "Output as a bullet list."
)

SYSTEM_PROMPT_WITH_SEARCH = (
    "You are a Research Agent. You have been provided with real web search "
    "results below. Use them as your primary source and supplement with your "
    "own knowledge. List the key facts, trends, and data points relevant to "
    "the topic. Be factual and concise. Output as a bullet list."
)

MIN_RESPONSE_LENGTH = 50


def _build_prompt(topic: str, search_results: str | None) -> str:
    """Construct the user prompt, optionally including web search results."""
    if search_results:
        return (
            f"Topic: {topic}\n\n"
            f"{search_results}\n\n"
            "Based on the search results above (and your knowledge), "
            "provide a bullet-point research summary."
        )
    return topic


def execute(topic: str, api_client: APIClient) -> str:
    """
    Generate bullet-point research notes for the given topic.

    Phase 2: attempts a live web search first; blends results into the LLM
    prompt if available. Silently degrades to LLM-only if search is
    unavailable.

    Args:
        topic:      Research subject (validated, trimmed string).
        api_client: Configured Claude API client.

    Returns:
        Bullet-point research notes as a string.

    Raises:
        AgentExecutionError: If the API call fails after retry.
    """
    logger.info("[%s] Starting research on topic: %.80s…", AGENT_NAME, topic)

    # --- Phase 2: try web search ---
    search_results = web_search(topic)
    system_prompt = SYSTEM_PROMPT_WITH_SEARCH if search_results else SYSTEM_PROMPT
    user_prompt = _build_prompt(topic, search_results)

    if search_results:
        logger.info("[%s] Web search successful — enriching LLM prompt.", AGENT_NAME)
    else:
        logger.info("[%s] No web search results — using LLM-only mode.", AGENT_NAME)

    try:
        response = call_with_retry(
            func=lambda: api_client.call_claude(system_prompt, user_prompt),
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
        enhanced_prompt = _build_prompt(
            f"List at least 5 distinct points about: {topic}", search_results
        )
        try:
            response = call_with_retry(
                func=lambda: api_client.call_claude(system_prompt, enhanced_prompt),
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

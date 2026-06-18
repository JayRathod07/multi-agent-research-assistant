"""
Web Search Tool for the Multi-Agent Research Assistant.

Uses the Tavily API to fetch real, up-to-date web results for the
Researcher agent. Falls back gracefully if the key is absent or the
call fails so the rest of the pipeline is unaffected.

Phase 2 addition.
"""

import os
from typing import Optional

from utils.logging_config import get_logger

logger = get_logger(__name__)

_MAX_RESULTS = 5
_MAX_CONTENT_LENGTH = 400  # characters per result snippet


def web_search(query: str) -> Optional[str]:
    """
    Search the web for the given query using Tavily.

    Args:
        query: The search query string.

    Returns:
        A formatted string of search results, or None if unavailable.
    """
    api_key = os.getenv("TAVILY_API_KEY", "").strip()

    if not api_key or api_key == "your_tavily_key_here":
        logger.info("[WebSearch] TAVILY_API_KEY not set — skipping web search.")
        return None

    try:
        from tavily import TavilyClient  # type: ignore

        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=_MAX_RESULTS,
        )

        results = response.get("results", [])
        if not results:
            logger.warning("[WebSearch] No results returned for query: %.80s", query)
            return None

        lines = ["=== Web Search Results ==="]
        for i, item in enumerate(results, start=1):
            title = item.get("title", "No title")
            content = item.get("content", "")
            url = item.get("url", "")
            snippet = content[:_MAX_CONTENT_LENGTH].strip()
            if len(content) > _MAX_CONTENT_LENGTH:
                snippet += "…"
            lines.append(f"\n[{i}] {title}")
            lines.append(f"    {snippet}")
            if url:
                lines.append(f"    Source: {url}")

        formatted = "\n".join(lines)
        logger.info(
            "[WebSearch] Fetched %d results (%d chars).", len(results), len(formatted)
        )
        return formatted

    except ImportError:
        logger.warning(
            "[WebSearch] 'tavily-python' not installed. Run: pip install tavily-python"
        )
        return None
    except Exception as exc:  # noqa: BLE001
        logger.warning("[WebSearch] Search failed: %s", exc)
        return None

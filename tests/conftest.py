"""
Shared fixtures and mock utilities for the test suite.
"""
import pytest
from unittest.mock import MagicMock


# ── Fake API responses ────────────────────────────────────────────────────────

MOCK_RESEARCH_NOTES = (
    "- Artificial Intelligence is transforming many industries\n"
    "- Machine learning models require large datasets\n"
    "- Deep learning excels at image and speech recognition\n"
    "- AI ethics is an emerging area of concern\n"
    "- Natural Language Processing enables human-computer dialogue"
)

MOCK_INSIGHTS = (
    "1. AI is reshaping industries through automation and data analysis\n"
    "2. Ethical considerations are central to responsible AI deployment\n"
    "3. Large data requirements create barriers for smaller organisations"
)

MOCK_REPORT = (
    "Artificial Intelligence is changing the way we live and work.\n\n"
    "The technology relies on vast amounts of data to learn and improve.\n\n"
    "Ethical concerns must be addressed as AI becomes more prevalent.\n\n"
    "Smaller organisations may struggle due to high data requirements."
)


# ── Mock API client ───────────────────────────────────────────────────────────

def make_mock_api_client(
    researcher_response: str = MOCK_RESEARCH_NOTES,
    analyst_response: str = MOCK_INSIGHTS,
    writer_response: str = MOCK_REPORT,
):
    """
    Return a MagicMock APIClient whose call_claude() returns appropriate
    canned responses based on the system prompt content.
    """
    client = MagicMock()

    def _call_claude(system_prompt: str, user_message: str, max_tokens: int = 0) -> str:
        if "Research Agent" in system_prompt:
            return researcher_response
        elif "Analyst Agent" in system_prompt:
            return analyst_response
        elif "Writer Agent" in system_prompt:
            return writer_response
        return "Generic response"

    client.call_claude.side_effect = _call_claude
    return client


@pytest.fixture
def mock_api_client():
    """Pytest fixture: a mock API client with realistic canned responses."""
    return make_mock_api_client()


@pytest.fixture
def failing_api_client():
    """Pytest fixture: an API client that always raises NetworkError."""
    from exceptions import NetworkError
    client = MagicMock()
    client.call_claude.side_effect = NetworkError("Connection failed")
    return client

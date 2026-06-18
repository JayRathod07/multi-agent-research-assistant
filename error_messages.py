"""
Centralised error message templates for the Multi-Agent Research Assistant.
Use ERROR_MESSAGES[key] to retrieve the appropriate message string.
For messages with placeholders, use .format(**kwargs) on the result.
"""

ERROR_MESSAGES: dict = {
    # --- Input validation ---
    "empty_topic": (
        "Error: Topic cannot be empty. Please enter a valid research topic."
    ),
    "whitespace_topic": (
        "Error: Topic contains only whitespace. Please enter meaningful text."
    ),
    "topic_too_long": (
        "Error: Topic exceeds 500 characters. Please shorten your topic."
    ),

    # --- API / authentication ---
    "missing_api_key": (
        "Error: ANTHROPIC_API_KEY not found. Please add it to your .env file."
    ),
    "invalid_api_key": (
        "Error: Authentication failed. Please check your API key in .env file."
    ),

    # --- API errors ---
    "rate_limit": (
        "Error: API rate limit exceeded. Please wait and try again later."
    ),
    "timeout": (
        "Error: Request timed out. Please check your network connection and try again."
    ),
    "network_error": (
        "Error: Network connection failed. Please check your internet connection."
    ),

    # --- Agent failures ---
    "agent_failed": (
        "Warning: {agent_name} agent failed after retry. "
        "Using placeholder data to continue."
    ),
}

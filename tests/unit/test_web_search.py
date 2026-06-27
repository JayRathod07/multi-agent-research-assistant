"""
Phase 2 unit tests — Web Search Tool (tools/search.py).

TavilyClient is imported inside the function body in search.py, so we patch
the tavily module itself rather than the tools.search namespace.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from unittest.mock import MagicMock, patch


# ── Helpers ──────────────────────────────────────────────────────────────────

def _mock_tavily_response(titles_urls: list) -> dict:
    """Build a fake Tavily API response dict."""
    return {
        "results": [
            {
                "title": t,
                "content": f"Detailed content about {t}",
                "url": u,
            }
            for t, u in titles_urls
        ]
    }


# ── No-key / skip behaviour ───────────────────────────────────────────────────

class TestWebSearchNoKey:
    """Web search gracefully skips when TAVILY_API_KEY is absent or placeholder."""

    def test_returns_none_when_key_absent(self):
        env = {k: v for k, v in os.environ.items() if k != "TAVILY_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            import importlib
            import tools.search as sm
            importlib.reload(sm)
            result = sm.web_search("AI in healthcare")
            assert result is None

    def test_returns_none_when_key_is_placeholder(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "your_tavily_key_here"}):
            import importlib
            import tools.search as sm
            importlib.reload(sm)
            result = sm.web_search("quantum computing")
            assert result is None

    def test_returns_none_when_key_is_empty_string(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "   "}):
            import importlib
            import tools.search as sm
            importlib.reload(sm)
            result = sm.web_search("machine learning")
            assert result is None


# ── Successful search ─────────────────────────────────────────────────────────

class TestWebSearchSuccess:
    """Web search returns a formatted string on success."""

    # TavilyClient is imported INSIDE the function, so patch at the module level
    # it's imported from: "tavily.TavilyClient"
    _PATCH_TARGET = "tavily.TavilyClient"

    def test_returns_non_empty_string(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "tvly-test-valid"}):
            mock_client = MagicMock()
            mock_client.search.return_value = _mock_tavily_response([
                ("AI in Healthcare: A Review", "https://example.com/ai"),
                ("Machine Learning in Medicine", "https://example.com/ml"),
            ])
            with patch(self._PATCH_TARGET, return_value=mock_client):
                import importlib
                import tools.search as sm
                importlib.reload(sm)
                result = sm.web_search("AI healthcare")
                assert result is not None
                assert isinstance(result, str)
                assert len(result) > 0

    def test_result_contains_web_search_header(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "tvly-test-valid"}):
            mock_client = MagicMock()
            mock_client.search.return_value = _mock_tavily_response([
                ("Title One", "https://a.com"),
            ])
            with patch(self._PATCH_TARGET, return_value=mock_client):
                import importlib
                import tools.search as sm
                importlib.reload(sm)
                result = sm.web_search("topic")
                assert "Web Search Results" in result

    def test_result_contains_article_title(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "tvly-test-valid"}):
            mock_client = MagicMock()
            mock_client.search.return_value = _mock_tavily_response([
                ("AI in Healthcare: A Review", "https://example.com/ai"),
            ])
            with patch(self._PATCH_TARGET, return_value=mock_client):
                import importlib
                import tools.search as sm
                importlib.reload(sm)
                result = sm.web_search("AI")
                assert "AI in Healthcare: A Review" in result

    def test_result_contains_source_url(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "tvly-test-valid"}):
            mock_client = MagicMock()
            mock_client.search.return_value = _mock_tavily_response([
                ("Title", "https://example.com/source"),
            ])
            with patch(self._PATCH_TARGET, return_value=mock_client):
                import importlib
                import tools.search as sm
                importlib.reload(sm)
                result = sm.web_search("topic")
                assert "example.com/source" in result

    def test_search_called_with_correct_query(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "tvly-test-valid"}):
            mock_client = MagicMock()
            mock_client.search.return_value = _mock_tavily_response([
                ("T", "https://x.com"),
            ])
            with patch(self._PATCH_TARGET, return_value=mock_client):
                import importlib
                import tools.search as sm
                importlib.reload(sm)
                sm.web_search("blockchain technology")
                call_kwargs = mock_client.search.call_args[1]
                assert call_kwargs["query"] == "blockchain technology"


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestWebSearchEdgeCases:
    _PATCH_TARGET = "tavily.TavilyClient"

    def test_empty_results_returns_none(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "tvly-test-valid"}):
            mock_client = MagicMock()
            mock_client.search.return_value = {"results": []}
            with patch(self._PATCH_TARGET, return_value=mock_client):
                import importlib
                import tools.search as sm
                importlib.reload(sm)
                result = sm.web_search("obscure topic nobody knows about")
                assert result is None

    def test_api_exception_returns_none(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "tvly-test-valid"}):
            mock_client = MagicMock()
            mock_client.search.side_effect = Exception("Connection timeout from Tavily")
            with patch(self._PATCH_TARGET, return_value=mock_client):
                import importlib
                import tools.search as sm
                importlib.reload(sm)
                result = sm.web_search("some topic")
                # Must NOT raise — must return None
                assert result is None

    def test_function_exists_and_is_callable(self):
        import tools.search as sm
        assert callable(sm.web_search)

# Multi-Agent Research Assistant

A learning + portfolio project demonstrating **agent orchestration** in Python. Three specialized AI agents collaborate to research a topic, analyze findings, and produce a final report — all coordinated by a central Orchestrator.

**Phase 2 ✅** — Now with a Streamlit Web UI and real web search via Tavily!

---

## What It Does

You give it a topic. Then:
1. **Researcher Agent** gathers key facts, trends, and data points (+ live web search in Phase 2)
2. **Analyst Agent** extracts the 3 most important insights
3. **Writer Agent** produces a clean, readable 3–4 paragraph report

All intermediate outputs (research notes, insights, final report) are displayed so you can see every step.

---

## Architecture

```
User Input (Topic)
      │
      ▼
 Orchestrator
      │
      ├── 1. Researcher Agent ──► (Web Search) ──► Research Notes
      │
      ├── 2. Analyst Agent ────────────────────► Key Insights
      │
      └── 3. Writer Agent ─────────────────────► Final Report
```

---

## Setup

### Prerequisites
- Python 3.8+
- An [Anthropic API key](https://console.anthropic.com/)
- *(Optional)* A [Tavily API key](https://app.tavily.com) for real web search (free tier: 1,000 searches/month)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/JayRathod07/multi-agent-research-assistant.git
cd multi-agent-research-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your API keys
copy .env.example .env
# Then open .env and replace the placeholder values with your actual keys
```

---

## Usage

### 🖥️ Streamlit Web UI (Phase 2 — Recommended)

```bash
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`

### ⌨️ CLI (Phase 1 — also works)

```bash
python main.py
```

---

## Project Structure

```
Multi-Agent Research Assistant/
├── app.py               # Streamlit Web UI (Phase 2)
├── main.py              # CLI entry point (Phase 1)
├── orchestrator.py      # Pipeline coordination
├── api_client.py        # Claude API wrapper
├── retry_logic.py       # Retry utility
├── models.py            # Data models
├── exceptions.py        # Custom exceptions
├── error_messages.py    # Error message templates
├── agents/
│   ├── researcher.py    # Researcher (+ web search in Phase 2)
│   ├── analyst.py
│   └── writer.py
├── tools/
│   └── search.py        # Tavily web search tool (Phase 2)
├── utils/
│   └── logging_config.py
├── tests/
│   ├── unit/
│   └── integration/
├── .env.example         # Copy → .env and add your keys
├── requirements.txt
└── requirements-dev.txt
```

---

## Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.8+ |
| LLM | Claude (Anthropic SDK) |
| Web Search | Tavily API (Phase 2) |
| UI | Streamlit (Phase 2) / CLI (Phase 1) |
| Testing | pytest |

---

## Roadmap

- ✅ **Phase 1** — CLI pipeline with three agents
- ✅ **Phase 2** — Streamlit web UI + real web search via Tavily
- ⬜ **Phase 3** — Deployment to Streamlit Community Cloud

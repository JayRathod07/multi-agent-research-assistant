# Multi-Agent Research Assistant

A learning + portfolio project demonstrating **agent orchestration** in Python. Three specialized AI agents collaborate to research a topic, analyze findings, and produce a final report — all coordinated by a central Orchestrator.

---

## What It Does

You give it a topic. Then:
1. **Researcher Agent** gathers key facts, trends, and data points
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
      ├── 1. Researcher Agent ──► Research Notes
      │
      ├── 2. Analyst Agent ────► Key Insights
      │
      └── 3. Writer Agent ─────► Final Report
```

---

## Setup

### Prerequisites
- Python 3.8+
- An [Anthropic API key](https://console.anthropic.com/)

### Installation

```bash
# 1. Clone the repo (or download the project folder)
cd "Multi-Agent Research Assistant"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your API key
copy .env.example .env
# Then open .env and replace `your_api_key_here` with your actual key
```

---

## Usage

```bash
python main.py
```

You will be prompted to enter a topic. Example:

```
==============================
 Multi-Agent Research Assistant
==============================
Enter a research topic: Artificial Intelligence in Healthcare

[Researcher] Gathering information...
[Analyst]    Extracting key insights...
[Writer]     Generating report...

============================================================
 RESEARCH NOTES
============================================================
- AI is being used to detect diseases earlier than traditional methods...
- Machine learning models can analyse medical images with high accuracy...
...

============================================================
 KEY INSIGHTS
============================================================
1. AI accelerates diagnosis by analysing data at superhuman speed
2. Personalised treatment plans powered by AI improve patient outcomes
3. Ethical concerns around data privacy and algorithmic bias remain key challenges

============================================================
 FINAL REPORT
============================================================
Artificial Intelligence is rapidly transforming healthcare...
...
```

---

## Project Structure

```
Multi-Agent Research Assistant/
├── main.py              # CLI entry point
├── orchestrator.py      # Pipeline coordination
├── api_client.py        # Claude API wrapper
├── retry_logic.py       # Retry utility
├── models.py            # Data models
├── exceptions.py        # Custom exceptions
├── error_messages.py    # Error message templates
├── agents/
│   ├── researcher.py
│   ├── analyst.py
│   └── writer.py
├── utils/
│   └── logging_config.py
├── tests/
│   ├── unit/
│   └── integration/
├── .env.example         # Copy → .env and add your key
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
| UI | CLI (Phase 1), Streamlit (Phase 2) |
| Testing | pytest + hypothesis |

---

## Roadmap

- ✅ **Phase 1** — CLI pipeline with three agents (this version)
- ⬜ **Phase 2** — Streamlit web UI + real web search
- ⬜ **Phase 3** — Deployment to Streamlit Community Cloud

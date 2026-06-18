"""
Multi-Agent Research Assistant — Streamlit Web UI (Phase 2)
Claude-inspired design with #00b4d8 accent color.

Run with:
    streamlit run app.py
"""

import sys
import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS — Claude-inspired dark UI with #00b4d8 accent ───────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Reset & base ── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* ── App background ── */
    .stApp {
        background-color: #1a1b1e;
    }

    /* Hide default Streamlit chrome */
    #MainMenu, header, footer { visibility: hidden; }
    [data-testid="stDecoration"] { display: none; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #111214 !important;
        border-right: 1px solid #2a2b2e !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    /* ── Sidebar scrollbar ── */
    [data-testid="stSidebar"]::-webkit-scrollbar { width: 4px; }
    [data-testid="stSidebar"]::-webkit-scrollbar-track { background: transparent; }
    [data-testid="stSidebar"]::-webkit-scrollbar-thumb { background: #2a2b2e; border-radius: 4px; }

    /* ── Main content padding ── */
    .main .block-container {
        padding: 2rem 2.5rem 3rem 2.5rem;
        max-width: 900px;
    }

    /* ── Sidebar logo/brand ── */
    .brand-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 1rem 1.5rem 1rem;
        border-bottom: 1px solid #2a2b2e;
        margin-bottom: 1.5rem;
    }
    .brand-icon {
        width: 32px;
        height: 32px;
        background: #00b4d8;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }
    .brand-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f4f4f5;
        line-height: 1.2;
    }
    .brand-version {
        font-size: 0.7rem;
        color: #52525b;
        font-weight: 400;
    }

    /* ── Sidebar section titles ── */
    .sidebar-section-title {
        font-size: 0.7rem;
        font-weight: 600;
        color: #52525b;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0 1rem;
        margin-bottom: 0.6rem;
    }

    /* ── Pipeline step items ── */
    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.65rem 1rem;
        border-radius: 8px;
        margin: 0 0.4rem 0.25rem 0.4rem;
        cursor: default;
        transition: background 0.15s ease;
    }
    .pipeline-step.idle {
        background: transparent;
    }
    .pipeline-step.active {
        background: rgba(0, 180, 216, 0.12);
        border: 1px solid rgba(0, 180, 216, 0.25);
    }
    .pipeline-step.done {
        background: rgba(0, 180, 216, 0.06);
    }
    .step-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .step-dot.idle  { background: #3f3f46; }
    .step-dot.active { background: #00b4d8; box-shadow: 0 0 0 3px rgba(0,180,216,0.2); }
    .step-dot.done  { background: #00b4d8; }
    .step-info {}
    .step-name {
        font-size: 0.875rem;
        font-weight: 500;
        color: #d4d4d8;
        line-height: 1.3;
    }
    .step-name.active { color: #00b4d8; }
    .step-desc {
        font-size: 0.75rem;
        color: #52525b;
        margin-top: 1px;
    }
    .step-check {
        margin-left: auto;
        color: #00b4d8;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* ── Sidebar history ── */
    .history-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        margin: 0 0.4rem 0.15rem 0.4rem;
        transition: background 0.15s;
    }
    .history-item:hover { background: #1e1f22; }
    .history-dot { font-size: 0.55rem; color: #52525b; }
    .history-text {
        font-size: 0.8rem;
        color: #71717a;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* ── Page header ── */
    .page-header {
        margin-bottom: 2.5rem;
    }
    .page-header-eyebrow {
        font-size: 0.75rem;
        font-weight: 600;
        color: #00b4d8;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .page-header-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f4f4f5;
        line-height: 1.25;
        margin-bottom: 0.6rem;
    }
    .page-header-subtitle {
        font-size: 0.95rem;
        color: #71717a;
        line-height: 1.6;
        max-width: 600px;
    }

    /* ── Input label ── */
    .input-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: #a1a1aa;
        margin-bottom: 0.5rem;
        letter-spacing: 0.01em;
    }

    /* ── Streamlit text input override ── */
    .stTextInput > label { display: none !important; }
    .stTextInput > div > div > input {
        background: #111214 !important;
        border: 1px solid #2a2b2e !important;
        border-radius: 10px !important;
        color: #f4f4f5 !important;
        font-size: 0.975rem !important;
        padding: 0.8rem 1.1rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.15s, box-shadow 0.15s !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00b4d8 !important;
        box-shadow: 0 0 0 3px rgba(0,180,216,0.12) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #3f3f46 !important;
        font-style: italic;
    }

    /* ── Run button ── */
    .stButton > button {
        background: #00b4d8 !important;
        color: #0d0d0e !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.78rem 1.6rem !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.01em !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        background: #0096b4 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(0,180,216,0.35) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: none !important;
    }

    /* ── Progress bar ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #0096b4, #00b4d8, #48cae4) !important;
        border-radius: 999px !important;
        transition: width 0.4s ease !important;
    }
    .stProgress > div > div {
        background: #2a2b2e !important;
        border-radius: 999px !important;
    }

    /* ── Status text ── */
    .status-line {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.85rem;
        color: #71717a;
        padding: 0.6rem 0;
    }
    .status-dot-pulse {
        width: 7px;
        height: 7px;
        background: #00b4d8;
        border-radius: 50%;
        flex-shrink: 0;
        animation: pulse 1.2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
    }

    /* ── Result section ── */
    .result-section {
        margin-top: 2rem;
    }
    .result-section-divider {
        height: 1px;
        background: #2a2b2e;
        margin: 2rem 0;
    }

    /* ── Result card ── */
    .result-card {
        background: #111214;
        border: 1px solid #2a2b2e;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 1.25rem;
    }
    .result-card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 1rem 1.4rem;
        border-bottom: 1px solid #2a2b2e;
    }
    .result-card-accent {
        width: 3px;
        height: 20px;
        border-radius: 2px;
        flex-shrink: 0;
    }
    .accent-research { background: #00b4d8; }
    .accent-insights  { background: #48cae4; }
    .accent-report    { background: #90e0ef; }

    .result-card-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #a1a1aa;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .result-card-badge {
        margin-left: auto;
        font-size: 0.7rem;
        font-weight: 500;
        color: #00b4d8;
        background: rgba(0,180,216,0.1);
        padding: 2px 8px;
        border-radius: 999px;
        border: 1px solid rgba(0,180,216,0.2);
    }
    .result-card-body {
        padding: 1.3rem 1.4rem;
    }
    .result-card-content {
        font-size: 0.925rem;
        line-height: 1.85;
        color: #d4d4d8;
        white-space: pre-wrap;
        word-break: break-word;
        font-weight: 400;
    }

    /* ── Metrics row ── */
    .metrics-row {
        display: flex;
        gap: 12px;
        margin-bottom: 1.5rem;
    }
    .metric-chip {
        display: flex;
        align-items: center;
        gap: 6px;
        background: #111214;
        border: 1px solid #2a2b2e;
        border-radius: 8px;
        padding: 0.5rem 0.9rem;
        font-size: 0.8rem;
        color: #71717a;
    }
    .metric-chip-value {
        color: #00b4d8;
        font-weight: 600;
    }

    /* ── Streamlit metric override ── */
    [data-testid="metric-container"] {
        background: #111214;
        border: 1px solid #2a2b2e;
        border-radius: 10px;
        padding: 0.85rem 1rem;
    }
    [data-testid="metric-container"] label {
        color: #52525b !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f4f4f5 !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
    }

    /* ── Download button ── */
    [data-testid="stDownloadButton"] > button {
        background: transparent !important;
        color: #00b4d8 !important;
        border: 1px solid rgba(0,180,216,0.35) !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.15s !important;
        width: auto !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: rgba(0,180,216,0.08) !important;
        border-color: #00b4d8 !important;
    }

    /* ── Alert/error boxes ── */
    [data-testid="stAlert"] {
        border-radius: 10px !important;
        border: none !important;
        font-size: 0.9rem !important;
    }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: #111214 !important;
        border: 1px solid #2a2b2e !important;
        border-radius: 10px !important;
    }
    .streamlit-expanderHeader {
        color: #a1a1aa !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }

    /* ── Divider ── */
    hr { border-color: #2a2b2e !important; margin: 1.5rem 0 !important; }

    /* ── Success message ── */
    .success-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(0,180,216,0.08);
        border: 1px solid rgba(0,180,216,0.2);
        border-radius: 10px;
        padding: 0.75rem 1.1rem;
        font-size: 0.875rem;
        color: #00b4d8;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session State Init ─────────────────────────────────────────────────────────
pipeline_steps = [
    ("Researcher", "Gathers facts & live data"),
    ("Analyst",    "Extracts key insights"),
    ("Writer",     "Drafts the final report"),
]
if "step_states" not in st.session_state:
    st.session_state.step_states = {name: "idle" for name, _ in pipeline_steps}
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown(
        """
        <div class="brand-wrap">
            <div class="brand-icon">🔬</div>
            <div>
                <div class="brand-name">Research Assistant</div>
                <div class="brand-version">Phase 2 · Multi-Agent</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Pipeline status
    st.markdown('<div class="sidebar-section-title">Pipeline</div>', unsafe_allow_html=True)
    for name, desc in pipeline_steps:
        state = st.session_state.step_states.get(name, "idle")
        check = "✓" if state == "done" else ("›" if state == "active" else "")
        name_class = "step-name active" if state == "active" else "step-name"
        st.markdown(
            f"""
            <div class="pipeline-step {state}">
                <div class="step-dot {state}"></div>
                <div class="step-info">
                    <div class="{name_class}">{name}</div>
                    <div class="step-desc">{desc}</div>
                </div>
                <div class="step-check">{check}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent topics
    if st.session_state.history:
        st.markdown('<div class="sidebar-section-title">Recent Topics</div>', unsafe_allow_html=True)
        for h in reversed(st.session_state.history[-6:]):
            label = h[:34] + "…" if len(h) > 34 else h
            st.markdown(
                f"""
                <div class="history-item">
                    <div class="history-dot">●</div>
                    <div class="history-text">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Divider + info
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="padding: 0 1rem; border-top: 1px solid #2a2b2e; padding-top: 1.2rem;">
            <div style="font-size:0.75rem; color:#3f3f46; line-height:1.7;">
                Powered by Claude (Anthropic)<br>
                Web Search via Tavily API
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Main Layout ────────────────────────────────────────────────────────────────

# Page header
st.markdown(
    """
    <div class="page-header">
        <div class="page-header-eyebrow">Multi-Agent AI</div>
        <div class="page-header-title">Research Assistant</div>
        <div class="page-header-subtitle">
            Enter any topic and three specialized AI agents will collaborate
            to gather information, extract insights, and write a complete report.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Input area
st.markdown('<div class="input-label">Research Topic</div>', unsafe_allow_html=True)

col_in, col_btn = st.columns([5, 1])
with col_in:
    topic_input = st.text_input(
        "topic",
        label_visibility="collapsed",
        placeholder="e.g. Artificial Intelligence in Healthcare",
        key="topic_field",
    )
with col_btn:
    run_clicked = st.button("Run →", key="run_btn", use_container_width=True)

st.markdown("---")

# ── Pipeline Execution ─────────────────────────────────────────────────────────
if run_clicked:
    topic = topic_input.strip()

    if not topic:
        st.error("Please enter a research topic before running.")
        st.stop()
    if len(topic) > 500:
        st.error("Topic is too long — please keep it under 500 characters.")
        st.stop()

    # Update history
    if topic not in st.session_state.history:
        st.session_state.history.append(topic)

    # Reset pipeline state
    st.session_state.step_states = {name: "idle" for name, _ in pipeline_steps}
    st.session_state.last_result = None

    # Import pipeline
    try:
        sys.path.insert(0, ".")
        from exceptions import AuthenticationError, ValidationError
        from orchestrator import run_pipeline
    except Exception as e:
        st.error(f"Import error: {e}")
        st.stop()

    start_time = time.time()

    # Progress display
    progress = st.progress(0, text="Initialising pipeline…")
    status_placeholder = st.empty()

    def show_status(msg: str):
        status_placeholder.markdown(
            f'<div class="status-line"><div class="status-dot-pulse"></div>{msg}</div>',
            unsafe_allow_html=True,
        )

    try:
        # ── Researcher ──
        st.session_state.step_states["Researcher"] = "active"
        progress.progress(15, text="Researcher is gathering information…")
        show_status("Researcher is gathering facts and data…")

        result = run_pipeline(topic)

        # ── Analyst ──
        st.session_state.step_states["Researcher"] = "done"
        st.session_state.step_states["Analyst"] = "active"
        progress.progress(55, text="Analyst is extracting insights…")
        show_status("Analyst is identifying key insights…")

        # ── Writer ──
        st.session_state.step_states["Analyst"] = "done"
        st.session_state.step_states["Writer"] = "active"
        progress.progress(82, text="Writer is composing the report…")
        show_status("Writer is drafting the final report…")

        st.session_state.step_states["Writer"] = "done"
        progress.progress(100, text="Done")
        st.session_state.last_result = result

    except ValidationError as e:
        st.error(f"Invalid topic: {e}")
        st.stop()
    except AuthenticationError:
        st.error(
            "**Authentication Error** — could not connect to Claude.\n\n"
            "Check that `ANTHROPIC_API_KEY` is set in your `.env` file."
        )
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.stop()

    elapsed = round(time.time() - start_time, 1)
    status_placeholder.empty()
    progress.empty()

    # Store elapsed for display
    st.session_state.elapsed = elapsed

# ── Show Results ───────────────────────────────────────────────────────────────
if st.session_state.last_result:
    result = st.session_state.last_result
    elapsed = st.session_state.get("elapsed", "–")

    # Success bar
    st.markdown(
        f'<div class="success-bar">✓ &nbsp;Pipeline completed in {elapsed}s — all three agents ran successfully</div>',
        unsafe_allow_html=True,
    )

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("⏱ Time", f"{elapsed}s")
    col2.metric("📋 Notes", f"{len(result.research_notes.content):,} ch")
    col3.metric("💡 Insights", f"{len(result.insights.content):,} ch")
    col4.metric("📄 Report", f"{len(result.final_report.content):,} ch")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Research Notes card ──
    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-card-header">
                <div class="result-card-accent accent-research"></div>
                <div class="result-card-title">Research Notes</div>
                <div class="result-card-badge">Researcher Agent</div>
            </div>
            <div class="result-card-body">
                <div class="result-card-content">{result.research_notes.content}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Key Insights card ──
    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-card-header">
                <div class="result-card-accent accent-insights"></div>
                <div class="result-card-title">Key Insights</div>
                <div class="result-card-badge">Analyst Agent</div>
            </div>
            <div class="result-card-body">
                <div class="result-card-content">{result.insights.content}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Final Report card ──
    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-card-header">
                <div class="result-card-accent accent-report"></div>
                <div class="result-card-title">Final Report</div>
                <div class="result-card-badge">Writer Agent</div>
            </div>
            <div class="result-card-body">
                <div class="result-card-content">{result.final_report.content}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Errors ──
    if result.errors:
        with st.expander("⚠ Warnings"):
            for err in result.errors:
                st.warning(err)

    # ── Download ──
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    topic_for_file = st.session_state.history[-1] if st.session_state.history else "report"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c for c in topic_for_file[:40] if c.isalnum() or c in " -_").strip().replace(" ", "_")
    filename = f"report_{safe_topic}_{timestamp}.txt"

    report_text = (
        f"MULTI-AGENT RESEARCH ASSISTANT\n"
        f"{'=' * 60}\n"
        f"Topic:     {topic_for_file}\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Duration:  {elapsed}s\n\n"
        f"{'=' * 60}\n"
        f"RESEARCH NOTES\n"
        f"{'=' * 60}\n"
        f"{result.research_notes.content}\n\n"
        f"{'=' * 60}\n"
        f"KEY INSIGHTS\n"
        f"{'=' * 60}\n"
        f"{result.insights.content}\n\n"
        f"{'=' * 60}\n"
        f"FINAL REPORT\n"
        f"{'=' * 60}\n"
        f"{result.final_report.content}\n"
    )

    st.download_button(
        label="⬇  Download Report (.txt)",
        data=report_text,
        file_name=filename,
        mime="text/plain",
        key="dl_btn",
    )

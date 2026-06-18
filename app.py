"""
Multi-Agent Research Assistant — Streamlit Web UI (Phase 2)

Run with:
    streamlit run app.py
"""

import sys
import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# ── Bootstrap ──────────────────────────────────────────────────────────────────
load_dotenv()

# Must be the very first Streamlit call
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0d0f1a 0%, #111827 50%, #0d1117 100%);
        min-height: 100vh;
    }

    /* ── Hide default header ── */
    #MainMenu, header, footer { visibility: hidden; }

    /* ── Hero Banner ── */
    .hero-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #1e3a5f 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #a5b4fc, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.2;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 0.6rem;
        font-weight: 400;
    }

    /* ── Agent Step Cards ── */
    .agent-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.3s ease;
    }
    .agent-card.active {
        border-color: rgba(99,102,241,0.6);
        background: rgba(99,102,241,0.1);
        box-shadow: 0 0 20px rgba(99,102,241,0.15);
    }
    .agent-card.done {
        border-color: rgba(52,211,153,0.4);
        background: rgba(52,211,153,0.07);
    }
    .agent-icon { font-size: 1.6rem; }
    .agent-label { color: #e2e8f0; font-weight: 600; font-size: 0.95rem; }
    .agent-desc { color: #64748b; font-size: 0.8rem; }

    /* ── Input Section ── */
    .input-section {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    .section-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    /* Override Streamlit input styles */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        font-size: 1.1rem !important;
        padding: 0.9rem 1.2rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(99,102,241,0.7) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #475569 !important;
    }

    /* ── Run Button ── */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2.5rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(79,70,229,0.4) !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(79,70,229,0.5) !important;
        background: linear-gradient(135deg, #5b52f0, #8b47f5) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Result Cards ── */
    .result-card {
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        padding: 1.8rem 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.07);
        position: relative;
        overflow: hidden;
    }
    .result-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
    }
    .result-card.research::before  { background: linear-gradient(90deg, #60a5fa, #3b82f6); }
    .result-card.insights::before  { background: linear-gradient(90deg, #a78bfa, #7c3aed); }
    .result-card.report::before    { background: linear-gradient(90deg, #34d399, #059669); }

    .result-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 1.2rem;
    }
    .result-icon { font-size: 1.5rem; }
    .result-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f1f5f9;
    }
    .result-content {
        color: #cbd5e1;
        font-size: 0.97rem;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    /* ── Status Pill ── */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-success {
        background: rgba(52,211,153,0.15);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
    }
    .status-error {
        background: rgba(239,68,68,0.15);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.25);
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: rgba(13,15,26,0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.07) !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li {
        color: #94a3b8;
        font-size: 0.88rem;
    }

    /* ── Progress bar ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4f46e5, #7c3aed, #34d399) !important;
        border-radius: 999px !important;
    }

    /* ── Metrics ── */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1rem;
    }
    [data-testid="metric-container"] label { color: #64748b !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
    }

    /* ── Download button ── */
    [data-testid="stDownloadButton"] > button {
        background: rgba(52,211,153,0.15) !important;
        color: #34d399 !important;
        border: 1px solid rgba(52,211,153,0.3) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: rgba(52,211,153,0.25) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Divider ── */
    hr { border-color: rgba(255,255,255,0.07) !important; }

    /* ── Warning / Error boxes ── */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 Research Assistant")
    st.markdown("---")

    # Pipeline steps
    st.markdown("### Pipeline")
    pipeline_steps = [
        ("🔍", "Researcher", "Gathers facts & data"),
        ("💡", "Analyst", "Extracts key insights"),
        ("✍️", "Writer", "Drafts the final report"),
    ]

    step_states = st.session_state.get("step_states", {s[1]: "idle" for s in pipeline_steps})

    for icon, name, desc in pipeline_steps:
        state = step_states.get(name, "idle")
        css_class = "agent-card active" if state == "active" else ("agent-card done" if state == "done" else "agent-card")
        icon_display = "⏳" if state == "active" else ("✅" if state == "done" else icon)
        st.markdown(
            f"""
            <div class="{css_class}">
                <div class="agent-icon">{icon_display}</div>
                <div>
                    <div class="agent-label">{name}</div>
                    <div class="agent-desc">{desc}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown(
        "Three AI agents collaborate to research any topic and produce a structured report.\n\n"
        "**Powered by:** Claude (Anthropic)\n\n"
        "**Web Search:** Tavily API *(optional)*"
    )

    st.markdown("---")
    # Show past topics in session
    if "history" in st.session_state and st.session_state.history:
        st.markdown("### 🕑 Recent Topics")
        for h in reversed(st.session_state.history[-5:]):
            st.markdown(f"- {h}")

# ── Main Content ───────────────────────────────────────────────────────────────

# Hero Banner
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">🔬 Multi-Agent Research Assistant</div>
        <div class="hero-subtitle">
            Enter any topic — Researcher, Analyst & Writer agents collaborate to deliver a complete report.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Input Section ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Research Topic</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    topic_input = st.text_input(
        label="topic",
        label_visibility="collapsed",
        placeholder="e.g.  Artificial Intelligence in Healthcare, Quantum Computing, Climate Change…",
        key="topic_input",
    )
with col_btn:
    run_clicked = st.button("🚀 Run", key="run_button", use_container_width=True)

st.markdown("---")

# ── Pipeline Execution ─────────────────────────────────────────────────────────
if run_clicked:
    topic = topic_input.strip()

    if not topic:
        st.error("⚠️  Please enter a research topic before running.")
        st.stop()

    if len(topic) > 500:
        st.error("⚠️  Topic is too long. Please keep it under 500 characters.")
        st.stop()

    # Track history
    if "history" not in st.session_state:
        st.session_state.history = []
    if topic not in st.session_state.history:
        st.session_state.history.append(topic)

    # Reset step states
    st.session_state.step_states = {name: "idle" for _, name, _ in pipeline_steps}

    start_time = time.time()

    # Progress bar + status text
    progress_bar = st.progress(0, text="Starting pipeline…")
    status_text  = st.empty()

    # ── Import pipeline ──
    try:
        sys.path.insert(0, ".")
        from error_messages import ERROR_MESSAGES
        from exceptions import AuthenticationError, ValidationError
        from orchestrator import run_pipeline
    except Exception as import_err:
        st.error(f"❌ Failed to import pipeline: {import_err}")
        st.stop()

    # ── Run with progress updates ──
    result = None
    try:
        # Step 1 — Researcher
        st.session_state.step_states = {**st.session_state.step_states, "Researcher": "active"}
        progress_bar.progress(10, text="🔍 Researcher is gathering information…")
        status_text.markdown(
            '<span class="status-pill" style="background:rgba(99,102,241,0.15);color:#a5b4fc;border:1px solid rgba(99,102,241,0.25);">⏳ Running Researcher…</span>',
            unsafe_allow_html=True,
        )

        result = run_pipeline(topic)

        # Fake progressive updates (pipeline is synchronous; show steps after completion)
        st.session_state.step_states["Researcher"] = "done"
        progress_bar.progress(50, text="💡 Analyst is extracting key insights…")
        st.session_state.step_states["Analyst"] = "done"
        progress_bar.progress(80, text="✍️ Writer is drafting the final report…")
        st.session_state.step_states["Writer"] = "done"
        progress_bar.progress(100, text="✅ Pipeline complete!")

    except ValidationError as exc:
        st.error(f"❌ Invalid topic: {exc}")
        st.stop()
    except AuthenticationError:
        st.error(
            "❌ **API Key Error** — Could not authenticate with Claude.\n\n"
            "Make sure `ANTHROPIC_API_KEY` is set in your `.env` file."
        )
        st.stop()
    except Exception as exc:
        st.error(f"❌ Unexpected error: {exc}")
        st.stop()

    elapsed = round(time.time() - start_time, 1)
    status_text.empty()

    # ── Metrics row ──────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⏱️ Total Time", f"{elapsed}s")
    m2.metric("📋 Research", f"{len(result.research_notes.content)} chars")
    m3.metric("💡 Insights", f"{len(result.insights.content)} chars")
    m4.metric("📄 Report", f"{len(result.final_report.content)} chars")

    st.markdown("---")

    # ── Result Cards ─────────────────────────────────────────────────────────

    # Research Notes
    st.markdown(
        f"""
        <div class="result-card research">
            <div class="result-header">
                <div class="result-icon">📋</div>
                <div class="result-title">Research Notes</div>
            </div>
            <div class="result-content">{result.research_notes.content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Key Insights
    st.markdown(
        f"""
        <div class="result-card insights">
            <div class="result-header">
                <div class="result-icon">💡</div>
                <div class="result-title">Key Insights</div>
            </div>
            <div class="result-content">{result.insights.content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Final Report
    st.markdown(
        f"""
        <div class="result-card report">
            <div class="result-header">
                <div class="result-icon">📄</div>
                <div class="result-title">Final Report</div>
            </div>
            <div class="result-content">{result.final_report.content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Errors / warnings ────────────────────────────────────────────────────
    if result.errors:
        with st.expander("⚠️ Warnings / Partial Failures"):
            for err in result.errors:
                st.warning(err)
        if result.failed_agents:
            st.info(f"ℹ️ Failed agents: {', '.join(result.failed_agents)} — see pipeline.log for details.")

    # ── Download button ──────────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c for c in topic[:40] if c.isalnum() or c in " -_").strip()
    filename = f"report_{safe_topic}_{timestamp}.txt".replace(" ", "_")

    report_text = (
        f"MULTI-AGENT RESEARCH ASSISTANT — REPORT\n"
        f"{'=' * 60}\n"
        f"Topic:     {topic}\n"
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

    st.markdown("---")
    st.download_button(
        label="⬇️  Download Full Report (.txt)",
        data=report_text,
        file_name=filename,
        mime="text/plain",
        key="download_btn",
    )

    # Success toast
    if result.is_complete_success:
        st.success(f"✅ Pipeline completed successfully in {elapsed}s!")

"""
Multi-Agent Research Assistant — Streamlit Web UI (Phase 2)
Claude-inspired design with #00b4d8 accent · Light & Dark themes.

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

# ── Session State Init ─────────────────────────────────────────────────────────
pipeline_steps = [
    ("Researcher", "Gathers facts & live data"),
    ("Analyst",    "Extracts key insights"),
    ("Writer",     "Drafts the final report"),
]
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "step_states" not in st.session_state:
    st.session_state.step_states = {name: "idle" for name, _ in pipeline_steps}
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

T = st.session_state.theme  # shorthand

# ── Theme Palettes ─────────────────────────────────────────────────────────────
themes = {
    "dark": {
        "app_bg":           "#1a1b1e",
        "sidebar_bg":       "#111214",
        "border":           "#2a2b2e",
        "card_bg":          "#111214",
        "input_bg":         "#111214",
        "text_primary":     "#f4f4f5",
        "text_secondary":   "#a1a1aa",
        "text_muted":       "#52525b",
        "text_faint":       "#3f3f46",
        "accent":           "#00b4d8",
        "accent_hover":     "#0096b4",
        "accent_light":     "#48cae4",
        "accent_lighter":   "#90e0ef",
        "accent_bg":        "rgba(0,180,216,0.10)",
        "accent_bg_hover":  "rgba(0,180,216,0.08)",
        "accent_border":    "rgba(0,180,216,0.25)",
        "success_bg":       "rgba(0,180,216,0.08)",
        "success_border":   "rgba(0,180,216,0.20)",
        "btn_text":         "#0d0d0e",
        "metric_bg":        "#111214",
        "pulse_color":      "#00b4d8",
        "scrollbar_thumb":  "#2a2b2e",
        "toggle_icon":      "☀️",
        "toggle_tip":       "Switch to Light mode",
    },
    "light": {
        "app_bg":           "#f8f9fa",
        "sidebar_bg":       "#ffffff",
        "border":           "#e4e4e7",
        "card_bg":          "#ffffff",
        "input_bg":         "#ffffff",
        "text_primary":     "#18181b",
        "text_secondary":   "#52525b",
        "text_muted":       "#71717a",
        "text_faint":       "#a1a1aa",
        "accent":           "#00b4d8",
        "accent_hover":     "#0096b4",
        "accent_light":     "#0077b6",
        "accent_lighter":   "#023e8a",
        "accent_bg":        "rgba(0,180,216,0.08)",
        "accent_bg_hover":  "rgba(0,180,216,0.12)",
        "accent_border":    "rgba(0,180,216,0.30)",
        "success_bg":       "rgba(0,180,216,0.07)",
        "success_border":   "rgba(0,180,216,0.25)",
        "btn_text":         "#ffffff",
        "metric_bg":        "#ffffff",
        "pulse_color":      "#00b4d8",
        "scrollbar_thumb":  "#e4e4e7",
        "toggle_icon":      "🌙",
        "toggle_tip":       "Switch to Dark mode",
    },
}

p = themes[T]  # active palette

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }}

    /* ── App background ── */
    .stApp {{
        background-color: {p['app_bg']} !important;
    }}

    /* Hide default chrome */
    #MainMenu, header, footer {{ visibility: hidden; }}
    [data-testid="stDecoration"] {{ display: none; }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background-color: {p['sidebar_bg']} !important;
        border-right: 1px solid {p['border']} !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{ padding-top: 1.5rem; }}
    [data-testid="stSidebar"]::-webkit-scrollbar {{ width: 4px; }}
    [data-testid="stSidebar"]::-webkit-scrollbar-track {{ background: transparent; }}
    [data-testid="stSidebar"]::-webkit-scrollbar-thumb {{
        background: {p['scrollbar_thumb']}; border-radius: 4px;
    }}

    /* ── Main container ── */
    .main .block-container {{
        padding: 2rem 2.5rem 3rem 2.5rem;
        max-width: 900px;
    }}

    /* ── Brand ── */
    .brand-wrap {{
        display: flex; align-items: center; gap: 10px;
        padding: 0 1rem 1.5rem 1rem;
        border-bottom: 1px solid {p['border']};
        margin-bottom: 1.5rem;
    }}
    .brand-icon {{
        width: 32px; height: 32px;
        background: {p['accent']};
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; flex-shrink: 0;
    }}
    .brand-name {{ font-size: 0.95rem; font-weight: 600; color: {p['text_primary']}; line-height: 1.2; }}
    .brand-version {{ font-size: 0.7rem; color: {p['text_muted']}; font-weight: 400; }}

    /* ── Sidebar section titles ── */
    .sidebar-section-title {{
        font-size: 0.7rem; font-weight: 600;
        color: {p['text_muted']};
        letter-spacing: 0.08em; text-transform: uppercase;
        padding: 0 1rem; margin-bottom: 0.6rem;
    }}

    /* ── Pipeline steps ── */
    .pipeline-step {{
        display: flex; align-items: center; gap: 12px;
        padding: 0.65rem 1rem;
        border-radius: 8px;
        margin: 0 0.4rem 0.25rem 0.4rem;
        transition: background 0.15s ease;
        border: 1px solid transparent;
    }}
    .pipeline-step.idle  {{ background: transparent; }}
    .pipeline-step.active {{
        background: {p['accent_bg']};
        border-color: {p['accent_border']};
    }}
    .pipeline-step.done  {{ background: {p['accent_bg']}; opacity: 0.8; }}

    .step-dot {{
        width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
    }}
    .step-dot.idle   {{ background: {p['border']}; }}
    .step-dot.active {{ background: {p['accent']}; box-shadow: 0 0 0 3px {p['accent_bg']}; }}
    .step-dot.done   {{ background: {p['accent']}; }}

    .step-name        {{ font-size: 0.875rem; font-weight: 500; color: {p['text_secondary']}; line-height: 1.3; }}
    .step-name.active {{ color: {p['accent']}; }}
    .step-desc        {{ font-size: 0.75rem; color: {p['text_muted']}; margin-top: 1px; }}
    .step-check       {{ margin-left: auto; color: {p['accent']}; font-size: 0.85rem; font-weight: 600; }}

    /* ── Sidebar history ── */
    .history-item {{
        display: flex; align-items: center; gap: 8px;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        margin: 0 0.4rem 0.15rem 0.4rem;
        transition: background 0.15s;
    }}
    .history-item:hover {{ background: {p['accent_bg']}; }}
    .history-dot {{ font-size: 0.55rem; color: {p['text_muted']}; }}
    .history-text {{
        font-size: 0.8rem; color: {p['text_muted']};
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}

    /* ── Sidebar footer ── */
    .sidebar-footer {{
        padding: 0 1rem;
        border-top: 1px solid {p['border']};
        padding-top: 1.2rem;
    }}
    .sidebar-footer-text {{
        font-size: 0.75rem; color: {p['text_faint']}; line-height: 1.7;
    }}

    /* ── Theme toggle button ── */
    .theme-toggle-wrap {{
        padding: 0 0.4rem;
        margin-bottom: 0.5rem;
    }}

    /* ── Page header ── */
    .page-header {{ margin-bottom: 2.5rem; }}
    .page-header-eyebrow {{
        font-size: 0.75rem; font-weight: 600;
        color: {p['accent']};
        letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.5rem;
    }}
    .page-header-title {{
        font-size: 1.85rem; font-weight: 700;
        color: {p['text_primary']};
        line-height: 1.25; margin-bottom: 0.6rem;
    }}
    .page-header-subtitle {{
        font-size: 0.95rem; color: {p['text_muted']};
        line-height: 1.6; max-width: 600px;
    }}

    /* ── Input label ── */
    .input-label {{
        font-size: 0.8rem; font-weight: 500;
        color: {p['text_secondary']};
        margin-bottom: 0.5rem; letter-spacing: 0.01em;
    }}

    /* ── Text input override ── */
    .stTextInput > label {{ display: none !important; }}
    .stTextInput > div > div > input {{
        background: {p['input_bg']} !important;
        border: 1px solid {p['border']} !important;
        border-radius: 10px !important;
        color: {p['text_primary']} !important;
        font-size: 0.975rem !important;
        padding: 0.8rem 1.1rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.15s, box-shadow 0.15s !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {p['accent']} !important;
        box-shadow: 0 0 0 3px {p['accent_bg']} !important;
        outline: none !important;
    }}
    .stTextInput > div > div > input::placeholder {{
        color: {p['text_faint']} !important;
        font-style: italic;
    }}

    /* ── Run button ── */
    .stButton > button {{
        background: {p['accent']} !important;
        color: {p['btn_text']} !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.78rem 1.4rem !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
    }}
    .stButton > button:hover {{
        background: {p['accent_hover']} !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(0,180,216,0.35) !important;
    }}
    .stButton > button:active {{
        transform: translateY(0) !important;
        box-shadow: none !important;
    }}

    /* ── Progress bar ── */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {p['accent_hover']}, {p['accent']}, {p['accent_light']}) !important;
        border-radius: 999px !important;
    }}
    .stProgress > div > div {{
        background: {p['border']} !important;
        border-radius: 999px !important;
    }}

    /* ── Status dot pulse ── */
    .status-line {{
        display: flex; align-items: center; gap: 8px;
        font-size: 0.85rem; color: {p['text_muted']};
        padding: 0.6rem 0;
    }}
    .status-dot-pulse {{
        width: 7px; height: 7px;
        background: {p['accent']};
        border-radius: 50%; flex-shrink: 0;
        animation: pulse 1.2s ease-in-out infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50%       {{ opacity: 0.4; transform: scale(0.85); }}
    }}

    /* ── Success bar ── */
    .success-bar {{
        display: flex; align-items: center; gap: 10px;
        background: {p['success_bg']};
        border: 1px solid {p['success_border']};
        border-radius: 10px;
        padding: 0.75rem 1.1rem;
        font-size: 0.875rem; color: {p['accent']};
        font-weight: 500; margin-bottom: 1.5rem;
    }}

    /* ── Metrics ── */
    [data-testid="metric-container"] {{
        background: {p['metric_bg']} !important;
        border: 1px solid {p['border']} !important;
        border-radius: 10px !important;
        padding: 0.85rem 1rem !important;
    }}
    [data-testid="metric-container"] label {{
        color: {p['text_muted']} !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    [data-testid="metric-container"] [data-testid="stMetricValue"] {{
        color: {p['text_primary']} !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
    }}

    /* ── Result cards ── */
    .result-card {{
        background: {p['card_bg']};
        border: 1px solid {p['border']};
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 1.25rem;
        transition: box-shadow 0.2s;
    }}
    .result-card:hover {{
        box-shadow: 0 4px 20px rgba(0,180,216,0.08);
    }}
    .result-card-header {{
        display: flex; align-items: center; gap: 10px;
        padding: 1rem 1.4rem;
        border-bottom: 1px solid {p['border']};
        background: {'rgba(0,0,0,0.15)' if T == 'dark' else 'rgba(0,0,0,0.02)'};
    }}
    .result-card-accent {{
        width: 3px; height: 20px; border-radius: 2px; flex-shrink: 0;
    }}
    .accent-research {{ background: {p['accent']}; }}
    .accent-insights  {{ background: {p['accent_light']}; }}
    .accent-report    {{ background: {p['accent_lighter']}; }}

    .result-card-title {{
        font-size: 0.82rem; font-weight: 600;
        color: {p['text_muted']};
        letter-spacing: 0.05em; text-transform: uppercase;
    }}
    .result-card-badge {{
        margin-left: auto;
        font-size: 0.7rem; font-weight: 500;
        color: {p['accent']};
        background: {p['accent_bg']};
        padding: 2px 8px; border-radius: 999px;
        border: 1px solid {p['accent_border']};
    }}
    .result-card-body {{ padding: 1.3rem 1.4rem; }}
    .result-card-content {{
        font-size: 0.925rem; line-height: 1.85;
        color: {p['text_secondary']};
        white-space: pre-wrap; word-break: break-word;
    }}

    /* ── Download button ── */
    [data-testid="stDownloadButton"] > button {{
        background: transparent !important;
        color: {p['accent']} !important;
        border: 1px solid {p['accent_border']} !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.15s !important;
        width: auto !important;
    }}
    [data-testid="stDownloadButton"] > button:hover {{
        background: {p['accent_bg_hover']} !important;
        border-color: {p['accent']} !important;
    }}

    /* ── Alerts ── */
    [data-testid="stAlert"] {{
        border-radius: 10px !important;
        border: none !important;
        font-size: 0.9rem !important;
    }}

    /* ── Expander ── */
    [data-testid="stExpander"] {{
        background: {p['card_bg']} !important;
        border: 1px solid {p['border']} !important;
        border-radius: 10px !important;
    }}
    .streamlit-expanderHeader {{
        color: {p['text_secondary']} !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }}

    /* ── Divider ── */
    hr {{ border-color: {p['border']} !important; margin: 1.5rem 0 !important; }}

    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown(
        f"""
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

    # ── Theme Toggle ──
    st.markdown('<div class="sidebar-section-title">Appearance</div>', unsafe_allow_html=True)
    toggle_label = f"{p['toggle_icon']}  {'Light Mode' if T == 'dark' else 'Dark Mode'}"
    if st.button(toggle_label, key="theme_toggle", use_container_width=True):
        st.session_state.theme = "light" if T == "dark" else "dark"
        st.rerun()

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # ── Pipeline steps ──
    st.markdown('<div class="sidebar-section-title">Pipeline</div>', unsafe_allow_html=True)
    for name, desc in pipeline_steps:
        state = st.session_state.step_states.get(name, "idle")
        check = "✓" if state == "done" else ("›" if state == "active" else "")
        name_cls = "step-name active" if state == "active" else "step-name"
        st.markdown(
            f"""
            <div class="pipeline-step {state}">
                <div class="step-dot {state}"></div>
                <div class="step-info">
                    <div class="{name_cls}">{name}</div>
                    <div class="step-desc">{desc}</div>
                </div>
                <div class="step-check">{check}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Recent topics ──
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
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Sidebar footer ──
    st.markdown(
        f"""
        <div class="sidebar-footer">
            <div class="sidebar-footer-text">
                Powered by Claude (Anthropic)<br>
                Web Search via Tavily API
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Main Content ───────────────────────────────────────────────────────────────

# Page header
st.markdown(
    f"""
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

# Input
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

    if topic not in st.session_state.history:
        st.session_state.history.append(topic)

    st.session_state.step_states = {name: "idle" for name, _ in pipeline_steps}
    st.session_state.last_result = None

    try:
        sys.path.insert(0, ".")
        from exceptions import AuthenticationError, ValidationError
        from orchestrator import run_pipeline
    except Exception as e:
        st.error(f"Import error: {e}")
        st.stop()

    start_time = time.time()
    progress = st.progress(0, text="Initialising pipeline…")
    status_ph = st.empty()

    def show_status(msg: str):
        status_ph.markdown(
            f'<div class="status-line"><div class="status-dot-pulse"></div>{msg}</div>',
            unsafe_allow_html=True,
        )

    try:
        st.session_state.step_states["Researcher"] = "active"
        progress.progress(15, text="Researcher is gathering information…")
        show_status("Researcher is gathering facts and data…")

        result = run_pipeline(topic)

        st.session_state.step_states["Researcher"] = "done"
        st.session_state.step_states["Analyst"]    = "active"
        progress.progress(55, text="Analyst is extracting insights…")
        show_status("Analyst is identifying key insights…")

        st.session_state.step_states["Analyst"] = "done"
        st.session_state.step_states["Writer"]  = "active"
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
    status_ph.empty()
    progress.empty()
    st.session_state.elapsed = elapsed

# ── Show Results ───────────────────────────────────────────────────────────────
if st.session_state.last_result:
    result  = st.session_state.last_result
    elapsed = st.session_state.get("elapsed", "–")

    # Success bar
    st.markdown(
        f'<div class="success-bar">✓ &nbsp;Pipeline completed in {elapsed}s — all three agents ran successfully</div>',
        unsafe_allow_html=True,
    )

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⏱ Time",     f"{elapsed}s")
    c2.metric("📋 Notes",   f"{len(result.research_notes.content):,} ch")
    c3.metric("💡 Insights",f"{len(result.insights.content):,} ch")
    c4.metric("📄 Report",  f"{len(result.final_report.content):,} ch")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # Research Notes
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

    # Key Insights
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

    # Final Report
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

    # Errors
    if result.errors:
        with st.expander("⚠ Warnings"):
            for err in result.errors:
                st.warning(err)

    # Download
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    topic_for_file = st.session_state.history[-1] if st.session_state.history else "report"
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c for c in topic_for_file[:40] if c.isalnum() or c in " -_").strip().replace(" ", "_")
    filename   = f"report_{safe_topic}_{timestamp}.txt"

    report_text = (
        f"MULTI-AGENT RESEARCH ASSISTANT\n"
        f"{'=' * 60}\n"
        f"Topic:     {topic_for_file}\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Duration:  {elapsed}s\n\n"
        f"{'=' * 60}\n"
        f"RESEARCH NOTES\n{'=' * 60}\n"
        f"{result.research_notes.content}\n\n"
        f"{'=' * 60}\n"
        f"KEY INSIGHTS\n{'=' * 60}\n"
        f"{result.insights.content}\n\n"
        f"{'=' * 60}\n"
        f"FINAL REPORT\n{'=' * 60}\n"
        f"{result.final_report.content}\n"
    )

    st.download_button(
        label="⬇  Download Report (.txt)",
        data=report_text,
        file_name=filename,
        mime="text/plain",
        key="dl_btn",
    )

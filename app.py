"""
Multi-Agent Research Assistant — Streamlit Web UI (Phase 2)
Warm earthy palette: Tea Green / Beige / Cornsilk / Papaya Whip / Light Bronze
Light & Dark themes.

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

# ── Session State ──────────────────────────────────────────────────────────────
pipeline_steps = [
    ("Researcher", "Gathers facts & live data"),
    ("Analyst",    "Extracts key insights"),
    ("Writer",     "Drafts the final report"),
]
if "theme"       not in st.session_state: st.session_state.theme       = "light"
if "step_states" not in st.session_state: st.session_state.step_states = {n: "idle" for n, _ in pipeline_steps}
if "history"     not in st.session_state: st.session_state.history     = []
if "last_result" not in st.session_state: st.session_state.last_result = None

T = st.session_state.theme

# ── Palette — 5 source colors ──────────────────────────────────────────────────
# Tea Green   #ccd5ae  rgb(204,213,174)
# Beige       #e9edc9  rgb(233,237,201)
# Cornsilk    #fefae0  rgb(254,250,224)
# Papaya Whip #faedcd  rgb(250,237,205)
# Light Bronze#d4a373  rgb(212,163,115)

themes = {
    "light": {
        # backgrounds
        "app_bg":          "#fefae0",   # Cornsilk — main canvas
        "sidebar_bg":      "#e9edc9",   # Beige — sidebar
        "card_bg":         "#faedcd",   # Papaya Whip — cards
        "input_bg":        "#fefae0",   # Cornsilk — inputs
        "metric_bg":       "#faedcd",   # Papaya Whip
        # borders
        "border":          "#d4c9a8",   # slightly darker Papaya Whip
        "border_light":    "#e9dfc5",
        # text
        "text_primary":    "#3b2f1e",   # deep warm brown
        "text_secondary":  "#6b5344",   # medium warm brown
        "text_muted":      "#9c7e63",   # lighter warm brown
        "text_faint":      "#c9aa8c",   # faintest
        # accent — Light Bronze as primary
        "accent":          "#d4a373",   # Light Bronze
        "accent_hover":    "#be8d5e",   # darker bronze
        "accent_light":    "#ccd5ae",   # Tea Green — secondary accent
        "accent_lighter":  "#a8b98a",   # darker Tea Green
        "accent_bg":       "rgba(212,163,115,0.12)",
        "accent_bg_hover": "rgba(212,163,115,0.20)",
        "accent_border":   "rgba(212,163,115,0.35)",
        "success_bg":      "rgba(204,213,174,0.30)",
        "success_border":  "rgba(172,185,140,0.50)",
        "success_color":   "#6a7f4a",   # deep Tea Green for text
        "btn_text":        "#fefae0",   # Cornsilk on Bronze button
        "scrollbar_thumb": "#d4c9a8",
        "header_overlay":  "rgba(254,250,224,0.6)",
        "toggle_icon":     "🌙",
        "toggle_label":    "Dark Mode",
    },
    "dark": {
        # backgrounds — same hue family but very dark / desaturated
        "app_bg":          "#1e1c14",   # near-black warm
        "sidebar_bg":      "#171612",   # deeper warm dark
        "card_bg":         "#252318",   # earthy dark card
        "input_bg":        "#1e1c14",
        "metric_bg":       "#252318",
        # borders
        "border":          "#3a3720",   # muted olive border
        "border_light":    "#302e1c",
        # text
        "text_primary":    "#fefae0",   # Cornsilk — brightest in dark
        "text_secondary":  "#e9edc9",   # Beige
        "text_muted":      "#9c8a6e",   # muted warm
        "text_faint":      "#5c5240",
        # accent — Light Bronze still as primary (works great on dark too)
        "accent":          "#d4a373",   # Light Bronze
        "accent_hover":    "#e0b584",   # lighter bronze on dark
        "accent_light":    "#ccd5ae",   # Tea Green
        "accent_lighter":  "#b0bf90",   # deeper Tea Green
        "accent_bg":       "rgba(212,163,115,0.12)",
        "accent_bg_hover": "rgba(212,163,115,0.18)",
        "accent_border":   "rgba(212,163,115,0.28)",
        "success_bg":      "rgba(204,213,174,0.10)",
        "success_border":  "rgba(204,213,174,0.25)",
        "success_color":   "#ccd5ae",   # Tea Green text in dark
        "btn_text":        "#1e1c14",   # dark on bronze button
        "scrollbar_thumb": "#3a3720",
        "header_overlay":  "rgba(30,28,20,0.0)",
        "toggle_icon":     "☀️",
        "toggle_label":    "Light Mode",
    },
}

p = themes[T]

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Lora:wght@400;500;600&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}}

/* ── App background ── */
.stApp {{ background-color: {p['app_bg']} !important; }}

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
    width: 34px; height: 34px;
    background: {p['accent']};
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}}
.brand-name  {{ font-size: 0.95rem; font-weight: 600; color: {p['text_primary']}; line-height: 1.2; }}
.brand-version {{ font-size: 0.7rem; color: {p['text_muted']}; font-weight: 400; }}

/* ── Sidebar section titles ── */
.sidebar-section-title {{
    font-size: 0.68rem; font-weight: 700;
    color: {p['text_muted']};
    letter-spacing: 0.10em; text-transform: uppercase;
    padding: 0 1rem; margin-bottom: 0.65rem;
}}

/* ── Pipeline steps ── */
.pipeline-step {{
    display: flex; align-items: center; gap: 12px;
    padding: 0.65rem 1rem; border-radius: 8px;
    margin: 0 0.4rem 0.25rem 0.4rem;
    transition: background 0.15s ease;
    border: 1px solid transparent;
}}
.pipeline-step.idle   {{ background: transparent; }}
.pipeline-step.active {{ background: {p['accent_bg']}; border-color: {p['accent_border']}; }}
.pipeline-step.done   {{ background: {p['accent_bg']}; opacity: 0.75; }}

.step-dot {{
    width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}}
.step-dot.idle   {{ background: {p['border']}; }}
.step-dot.active {{ background: {p['accent']}; box-shadow: 0 0 0 3px {p['accent_bg']}; }}
.step-dot.done   {{ background: {p['accent_light']}; }}

.step-name        {{ font-size: 0.875rem; font-weight: 500; color: {p['text_secondary']}; line-height: 1.3; }}
.step-name.active {{ color: {p['accent']}; font-weight: 600; }}
.step-desc        {{ font-size: 0.75rem; color: {p['text_muted']}; margin-top: 1px; }}
.step-check       {{ margin-left: auto; color: {p['accent_light']}; font-size: 0.85rem; font-weight: 700; }}

/* ── Sidebar history ── */
.history-item {{
    display: flex; align-items: center; gap: 8px;
    padding: 0.45rem 1rem; border-radius: 6px;
    margin: 0 0.4rem 0.1rem 0.4rem;
    transition: background 0.15s;
}}
.history-item:hover {{ background: {p['accent_bg']}; }}
.history-dot  {{ font-size: 0.5rem; color: {p['text_muted']}; }}
.history-text {{ font-size: 0.8rem; color: {p['text_muted']}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}

/* ── Sidebar footer ── */
.sidebar-footer {{
    padding: 1.2rem 1rem 0;
    border-top: 1px solid {p['border']};
}}
.sidebar-footer-text {{ font-size: 0.75rem; color: {p['text_faint']}; line-height: 1.8; }}

/* ── Theme toggle ── */
.stButton > button {{
    background: {p['accent']} !important;
    color: {p['btn_text']} !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.4rem !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    background: {p['accent_hover']} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(212,163,115,0.40) !important;
}}
.stButton > button:active {{
    transform: translateY(0) !important;
    box-shadow: none !important;
}}

/* ── Page header ── */
.page-header {{ margin-bottom: 2.5rem; }}
.page-header-eyebrow {{
    font-size: 0.72rem; font-weight: 700;
    color: {p['accent']};
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.5rem;
}}
.page-header-title {{
    font-family: 'Lora', Georgia, serif;
    font-size: 2rem; font-weight: 600;
    color: {p['text_primary']};
    line-height: 1.2; margin-bottom: 0.65rem;
}}
.page-header-subtitle {{
    font-size: 0.95rem; color: {p['text_muted']};
    line-height: 1.65; max-width: 580px;
}}

/* ── Input label ── */
.input-label {{
    font-size: 0.8rem; font-weight: 600;
    color: {p['text_secondary']};
    margin-bottom: 0.5rem; letter-spacing: 0.02em;
}}

/* ── Text input ── */
.stTextInput > label {{ display: none !important; }}
.stTextInput > div > div > input {{
    background: {p['input_bg']} !important;
    border: 1.5px solid {p['border']} !important;
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

/* ── Progress bar ── */
.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, {p['accent_hover']}, {p['accent']}, {p['accent_light']}) !important;
    border-radius: 999px !important;
}}
.stProgress > div > div {{
    background: {p['border']} !important;
    border-radius: 999px !important;
    height: 6px !important;
}}

/* ── Status line ── */
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
    0%,100% {{ opacity:1; transform:scale(1); }}
    50%      {{ opacity:0.4; transform:scale(0.8); }}
}}

/* ── Success bar ── */
.success-bar {{
    display: flex; align-items: center; gap: 10px;
    background: {p['success_bg']};
    border: 1px solid {p['success_border']};
    border-radius: 10px;
    padding: 0.75rem 1.2rem;
    font-size: 0.875rem; color: {p['success_color']};
    font-weight: 600; margin-bottom: 1.5rem;
}}

/* ── Metrics ── */
[data-testid="metric-container"] {{
    background: {p['metric_bg']} !important;
    border: 1.5px solid {p['border']} !important;
    border-radius: 10px !important;
    padding: 0.85rem 1rem !important;
}}
[data-testid="metric-container"] label {{
    color: {p['text_muted']} !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {p['text_primary']} !important;
    font-size: 1.25rem !important;
    font-weight: 700 !important;
}}

/* ── Result cards ── */
.result-card {{
    background: {p['card_bg']};
    border: 1.5px solid {p['border']};
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 1.25rem;
    transition: box-shadow 0.2s, transform 0.2s;
}}
.result-card:hover {{
    box-shadow: 0 6px 24px rgba(212,163,115,0.15);
    transform: translateY(-1px);
}}
.result-card-header {{
    display: flex; align-items: center; gap: 10px;
    padding: 1rem 1.4rem;
    border-bottom: 1.5px solid {p['border']};
    background: {'rgba(0,0,0,0.06)' if T == 'dark' else 'rgba(212,163,115,0.06)'};
}}
.result-card-accent {{
    width: 4px; height: 22px; border-radius: 3px; flex-shrink: 0;
}}
.accent-research {{ background: {p['accent']}; }}        /* Light Bronze */
.accent-insights  {{ background: {p['accent_light']}; }} /* Tea Green    */
.accent-report    {{ background: {p['accent_lighter']}; }} /* darker Tea Green */

.result-card-title {{
    font-size: 0.78rem; font-weight: 700;
    color: {p['text_muted']};
    letter-spacing: 0.07em; text-transform: uppercase;
}}
.result-card-badge {{
    margin-left: auto;
    font-size: 0.68rem; font-weight: 600;
    color: {p['accent']};
    background: {p['accent_bg']};
    padding: 3px 9px; border-radius: 999px;
    border: 1px solid {p['accent_border']};
    letter-spacing: 0.02em;
}}
.result-card-body {{ padding: 1.3rem 1.4rem; }}
.result-card-content {{
    font-size: 0.94rem; line-height: 1.9;
    color: {p['text_secondary']};
    white-space: pre-wrap; word-break: break-word;
    font-family: 'Inter', sans-serif;
}}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {{
    background: transparent !important;
    color: {p['accent']} !important;
    border: 1.5px solid {p['accent_border']} !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.4rem !important;
    transition: all 0.15s !important;
    width: auto !important;
    font-family: 'Inter', sans-serif !important;
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
    border: 1.5px solid {p['border']} !important;
    border-radius: 10px !important;
}}
.streamlit-expanderHeader {{
    color: {p['text_secondary']} !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
}}

/* ── Divider ── */
hr {{ border-color: {p['border']} !important; margin: 1.5rem 0 !important; }}

/* ── Colour swatch strip ── */
.swatch-strip {{
    display: flex; gap: 6px;
    padding: 0 1rem;
    margin-bottom: 1rem;
}}
.swatch {{
    width: 20px; height: 20px;
    border-radius: 5px;
    border: 1px solid {p['border']};
    flex-shrink: 0;
    cursor: default;
    transition: transform 0.15s;
}}
.swatch:hover {{ transform: scale(1.25); }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown(f"""
    <div class="brand-wrap">
        <div class="brand-icon">🔬</div>
        <div>
            <div class="brand-name">Research Assistant</div>
            <div class="brand-version">Phase 2 · Multi-Agent</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Colour palette swatch strip
    st.markdown("""
    <div class="swatch-strip">
        <div class="swatch" style="background:#ccd5ae;" title="Tea Green"></div>
        <div class="swatch" style="background:#e9edc9;" title="Beige"></div>
        <div class="swatch" style="background:#fefae0;" title="Cornsilk"></div>
        <div class="swatch" style="background:#faedcd;" title="Papaya Whip"></div>
        <div class="swatch" style="background:#d4a373;" title="Light Bronze"></div>
    </div>""", unsafe_allow_html=True)

    # Theme toggle
    st.markdown('<div class="sidebar-section-title">Appearance</div>', unsafe_allow_html=True)
    if st.button(f"{p['toggle_icon']}  {p['toggle_label']}", key="theme_toggle", use_container_width=True):
        st.session_state.theme = "light" if T == "dark" else "dark"
        st.rerun()

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # Pipeline
    st.markdown('<div class="sidebar-section-title">Pipeline</div>', unsafe_allow_html=True)
    for name, desc in pipeline_steps:
        state    = st.session_state.step_states.get(name, "idle")
        check    = "✓" if state == "done" else ("›" if state == "active" else "")
        name_cls = "step-name active" if state == "active" else "step-name"
        st.markdown(f"""
        <div class="pipeline-step {state}">
            <div class="step-dot {state}"></div>
            <div class="step-info">
                <div class="{name_cls}">{name}</div>
                <div class="step-desc">{desc}</div>
            </div>
            <div class="step-check">{check}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # History
    if st.session_state.history:
        st.markdown('<div class="sidebar-section-title">Recent Topics</div>', unsafe_allow_html=True)
        for h in reversed(st.session_state.history[-6:]):
            label = h[:34] + "…" if len(h) > 34 else h
            st.markdown(f"""
            <div class="history-item">
                <div class="history-dot">●</div>
                <div class="history-text">{label}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
    <div class="sidebar-footer">
        <div class="sidebar-footer-text">
            Powered by Claude (Anthropic)<br>
            Web Search via Tavily API
        </div>
    </div>""", unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="page-header">
    <div class="page-header-eyebrow">Multi-Agent AI</div>
    <div class="page-header-title">Research Assistant</div>
    <div class="page-header-subtitle">
        Enter any topic and three specialized AI agents collaborate to gather
        information, extract insights, and write a polished report.
    </div>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="input-label">Research Topic</div>', unsafe_allow_html=True)
col_in, col_btn = st.columns([5, 1])
with col_in:
    topic_input = st.text_input(
        "topic", label_visibility="collapsed",
        placeholder="e.g. Artificial Intelligence in Healthcare",
        key="topic_field",
    )
with col_btn:
    run_clicked = st.button("Run →", key="run_btn", use_container_width=True)

st.markdown("---")

# ── Run pipeline ───────────────────────────────────────────────────────────────
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
    progress   = st.progress(0, text="Initialising pipeline…")
    status_ph  = st.empty()

    def show_status(msg):
        status_ph.markdown(
            f'<div class="status-line"><div class="status-dot-pulse"></div>{msg}</div>',
            unsafe_allow_html=True)

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

    except Exception as e:
        from exceptions import AuthenticationError, ValidationError
        if isinstance(e, ValidationError):
            st.error(f"Invalid topic: {e}")
        elif isinstance(e, AuthenticationError):
            st.error("**Authentication Error** — check `ANTHROPIC_API_KEY` in your `.env` file.")
        else:
            st.error(f"Unexpected error: {e}")
        st.stop()

    elapsed = round(time.time() - start_time, 1)
    status_ph.empty()
    progress.empty()
    st.session_state.elapsed = elapsed

# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.last_result:
    result  = st.session_state.last_result
    elapsed = st.session_state.get("elapsed", "–")

    st.markdown(
        f'<div class="success-bar">✓ &nbsp;Pipeline completed in {elapsed}s — all three agents ran successfully</div>',
        unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⏱ Time",      f"{elapsed}s")
    c2.metric("📋 Notes",    f"{len(result.research_notes.content):,} ch")
    c3.metric("💡 Insights", f"{len(result.insights.content):,} ch")
    c4.metric("📄 Report",   f"{len(result.final_report.content):,} ch")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    for card_class, icon, title, badge, content in [
        ("accent-research", "📋", "Research Notes", "Researcher Agent", result.research_notes.content),
        ("accent-insights",  "💡", "Key Insights",   "Analyst Agent",    result.insights.content),
        ("accent-report",    "📄", "Final Report",   "Writer Agent",     result.final_report.content),
    ]:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-card-header">
                <div class="result-card-accent {card_class}"></div>
                <div class="result-card-title">{title}</div>
                <div class="result-card-badge">{badge}</div>
            </div>
            <div class="result-card-body">
                <div class="result-card-content">{content}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    if result.errors:
        with st.expander("⚠ Warnings"):
            for err in result.errors:
                st.warning(err)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    topic_for_file = st.session_state.history[-1] if st.session_state.history else "report"
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c for c in topic_for_file[:40] if c.isalnum() or c in " -_").strip().replace(" ", "_")

    report_text = (
        f"MULTI-AGENT RESEARCH ASSISTANT\n{'='*60}\n"
        f"Topic:     {topic_for_file}\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Duration:  {elapsed}s\n\n"
        f"{'='*60}\nRESEARCH NOTES\n{'='*60}\n{result.research_notes.content}\n\n"
        f"{'='*60}\nKEY INSIGHTS\n{'='*60}\n{result.insights.content}\n\n"
        f"{'='*60}\nFINAL REPORT\n{'='*60}\n{result.final_report.content}\n"
    )

    st.download_button(
        label="⬇  Download Report (.txt)",
        data=report_text,
        file_name=f"report_{safe_topic}_{timestamp}.txt",
        mime="text/plain",
        key="dl_btn",
    )

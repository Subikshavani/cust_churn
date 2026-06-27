from __future__ import annotations

import streamlit as st

from src.pages import (
    dashboard_page,
    explainability_page,
    prediction_page,
    segmentation_page,
    revenue_risk_page,
    retention_simulator_page,
)
from src.styles import CSS
from src.utils import get_dashboard_data, get_metrics_report

st.set_page_config(
    page_title="Telco Churn Intelligence Platform",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def load_metrics():
    return get_metrics_report()


def load_dashboard_data():
    return get_dashboard_data()


st.sidebar.markdown("<div class='sidebar-brand-title'>Telco Churn Intelligence</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-brand-subtitle'>Commercial-grade customer analytics for telecom teams.</div>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Executive Dashboard",
        "🔮 Churn Prediction",
        "🧠 Explainable AI",
        "👥 Customer Segmentation",
        "💰 Revenue Risk Analysis",
        "🎯 Retention Simulator",
    ],
)

metrics = load_metrics()
df = load_dashboard_data()

st.sidebar.markdown("---")
is_dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)

if not is_dark_mode:
    st.markdown("""
        <style>
        /* ════════════════════════════════════════════════
           PURPLE LIGHT MODE — fully hardcoded, safe for deployment
           ════════════════════════════════════════════════ */

        /* ── App background: soft lavender ── */
        html, body { background-color: #f5f3ff !important; color: #1e1b4b !important; }
        .stApp {
            background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 50%, #faf5ff 100%) !important;
            color: #1e1b4b !important;
        }

        /* ── Force DARK text on every element ── */
        .stApp *,
        .stMarkdown, .stMarkdown *,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] *,
        [data-testid="stText"],
        [data-testid="stMetricValue"],
        [data-testid="stMetricLabel"],
        [data-testid="stMetricDelta"],
        .stCaption,
        .stRadio label, .stSelectbox label,
        .stSlider label, .stToggle label,
        .stCheckbox label,
        p, span, h1, h2, h3, h4, h5, h6, label, li, a,
        div, td, th {
            color: #1e1b4b !important;
        }

        /* ── Sidebar: light violet ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ede9fe 0%, #ddd6fe 100%) !important;
            border-right: 1px solid rgba(109,40,217,0.2) !important;
        }
        [data-testid="stSidebar"] * { color: #1e1b4b !important; }

        /* ── Sidebar brand title: purple accent ── */
        .sidebar-brand-title { color: #5b21b6 !important; }
        .sidebar-brand-subtitle { color: #4c1d95 !important; opacity: 1 !important; }

        /* ── Section titles ── */
        .section-title { color: #4c1d95 !important; }
        .brand-title   { color: #1e1b4b !important; }
        .brand-subtitle{ color: #3b0764 !important; opacity: 1 !important; }

        /* ── KPI card: white frosted with dark text ── */
        .kpi-card {
            background: rgba(255,255,255,0.88) !important;
            border: 1px solid rgba(109,40,217,0.22) !important;
            box-shadow: 0 4px 20px rgba(109,40,217,0.1) !important;
        }
        .kpi-card * { color: #1e1b4b !important; }
        .kpi-value  { color: #1e1b4b !important; font-weight: 800 !important; }
        .kpi-label  { color: #4c1d95 !important; }
        .kpi-card:hover {
            border-color: #7c3aed !important;
            box-shadow: 0 8px 28px rgba(124,58,237,0.18) !important;
        }

        /* ── Glass card ── */
        .glass-card {
            background: rgba(255,255,255,0.82) !important;
            border: 1px solid rgba(109,40,217,0.22) !important;
            box-shadow: 0 4px 24px rgba(109,40,217,0.1) !important;
            backdrop-filter: blur(12px) !important;
        }
        .glass-card * { color: #1e1b4b !important; }

        /* ── Form ── */
        [data-testid="stForm"] {
            background: rgba(255,255,255,0.82) !important;
            border: 1px solid rgba(109,40,217,0.22) !important;
            border-radius: 22px !important;
        }
        [data-testid="stForm"] * { color: #1e1b4b !important; }

        /* ── Input / select boxes ── */
        [data-baseweb="input"] input,
        [data-baseweb="select"] div,
        [data-baseweb="textarea"] textarea {
            background: #ffffff !important;
            color: #1e1b4b !important;
            border-color: rgba(109,40,217,0.35) !important;
        }

        /* ── Badges ── */
        .badge-low   { background: rgba(52,211,153,0.18) !important; color: #065f46 !important; }
        .badge-medium{ background: rgba(245,158,11,0.18) !important; color: #78350f !important; }
        .badge-high  { background: rgba(248,113,113,0.18) !important; color: #7f1d1d !important; }

        /* ── Primary button ── */
        button[kind="primary"] {
            background: linear-gradient(90deg, #7c3aed, #a855f7) !important;
            color: #ffffff !important;
            font-weight: 800 !important;
        }

        /* ── DataFrames / Tables: dark text, lavender bg ── */
        [data-testid="stDataFrame"] th,
        [data-testid="stDataFrame"] td {
            color: #1e1b4b !important;
            background: rgba(237,233,254,0.7) !important;
            border-color: rgba(109,40,217,0.15) !important;
        }

        /* ── Charts: dark axis text, dark legend box ── */
        .js-plotly-plot .plotly text,
        .js-plotly-plot .plotly .xtitle,
        .js-plotly-plot .plotly .ytitle,
        .js-plotly-plot .plotly .gtitle,
        .js-plotly-plot .plotly .xtick text,
        .js-plotly-plot .plotly .ytick text {
            fill: #1e1b4b !important;
            color: #1e1b4b !important;
        }
        .js-plotly-plot .plotly .bg {
            fill: rgba(237,233,254,0.55) !important;
        }
        .js-plotly-plot .plotly .legend rect.bg {
            fill: #1e1b4b !important;
            stroke: rgba(109,40,217,0.5) !important;
        }
        .js-plotly-plot .plotly .legend text {
            fill: #f5f3ff !important;
        }
        .js-plotly-plot .plotly .gridlayer path,
        .js-plotly-plot .plotly .zerolinelayer path {
            stroke: rgba(109,40,217,0.15) !important;
        }
        [data-testid="stPlotlyChart"] > div,
        [data-testid="stPlotlyChart"] .modebar {
            background: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
if page == "🏠 Executive Dashboard":
    dashboard_page(df)
elif page == "🔮 Churn Prediction":
    prediction_page()
elif page == "🧠 Explainable AI":
    explainability_page(df)
elif page == "👥 Customer Segmentation":
    segmentation_page(df)
elif page == "💰 Revenue Risk Analysis":
    revenue_risk_page(df)
elif page == "🎯 Retention Simulator":
    retention_simulator_page()

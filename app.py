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
st.sidebar.caption(f"Best model: {metrics.get('best_model', 'Unknown')}")

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

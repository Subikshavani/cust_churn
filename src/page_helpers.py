from __future__ import annotations

from typing import Dict

import streamlit as st


PAGE_TITLES = {
    "dashboard": "Executive Dashboard",
    "predict": "Customer Churn Prediction",
    "explain": "Explainable AI",
    "segment": "Customer Segmentation",
    "retention": "Retention Strategy",
}


def apply_brand_header(title: str, subtitle: str) -> None:
    st.markdown(f"<div class='brand-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='brand-subtitle'>{subtitle}</div>", unsafe_allow_html=True)

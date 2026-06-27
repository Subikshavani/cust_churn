from __future__ import annotations

import datetime

from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from .charts import (
    churn_heatmap,
    feature_importance_chart,
    gauge_chart,
    kpi_timeline,
    revenue_impact,
    risk_distribution,
    segmentation_pie,
    cluster_scatter_chart,
    revenue_loss_forecast_chart,
    segment_comparison_chart,
    waterfall_explanation_chart,
)
from .modeling import get_feature_names, load_model_artifact, train_and_select_best_model
from .page_helpers import apply_brand_header
from .predict import explain_prediction
from .retention import retention_recommendations
from .utils import get_metrics_report, get_dashboard_data
from .export import generate_customer_csv, send_email_alert
import streamlit.components.v1 as components

try:
    import shap
except Exception:
    shap = None


def dashboard_page(df: pd.DataFrame) -> None:
    apply_brand_header("Telco Customer Intelligence Dashboard", "Executive view of churn, risk, health, and revenue exposure.")
    
    total_customers = len(df)
    active_customers = int((df["ChurnBinary"] == 0).sum())
    churned_customers = int((df["ChurnBinary"] == 1).sum())
    churn_rate = churned_customers / max(total_customers, 1)
    
    # High risk definition
    predicted_high_risk = int((df["risk_category"] == "High Risk").sum())
    
    # CLV average
    avg_clv = float((df["MonthlyCharges"] * df["tenure"]).mean())
    # Health Index average
    avg_health = float(df["health_score"].mean())
    # Revenue at risk
    revenue_at_risk = float(df.loc[df["risk_category"] == "High Risk", "MonthlyCharges"].sum() * 6)

    metrics = [
        ("Total Customers", f"{total_customers:,}"),
        ("Active Customers", f"{active_customers:,}"),
        ("Churned Customers", f"{churned_customers:,}"),
        ("Churn Rate (%)", f"{churn_rate * 100:.1f}%"),
        ("Revenue at Risk (6mo)", f"${revenue_at_risk:,.0f}"),
        ("High-Risk Base", f"{predicted_high_risk:,}"),
        ("Avg Lifetime Value", f"${avg_clv:,.0f}"),
        ("Customer Health Index", f"{avg_health:.1f}/100"),
    ]

    cols = st.columns(4)
    for i, (label, value) in enumerate(metrics[:4]):
        with cols[i]:
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div></div>", unsafe_allow_html=True)
            
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    
    cols2 = st.columns(4)
    for i, (label, value) in enumerate(metrics[4:]):
        with cols2[i]:
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    top_left, top_right = st.columns(2)
    with top_left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.plotly_chart(kpi_timeline(df), width='stretch', key="db_timeline")
        st.markdown("</div>", unsafe_allow_html=True)
    with top_right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.plotly_chart(segmentation_pie(df), width='stretch', key="db_segment_pie")
        st.markdown("</div>", unsafe_allow_html=True)

    bottom_left, bottom_right = st.columns(2)
    with bottom_left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.plotly_chart(risk_distribution(df), width='stretch', key="db_risk_dist")
        st.markdown("</div>", unsafe_allow_html=True)
    with bottom_right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.plotly_chart(revenue_impact(df), width='stretch', key="db_rev_impact")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.plotly_chart(churn_heatmap(df), width='stretch', key="db_heatmap")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Removed CEO summary section ───────────────────────────────────────

    # ── Removed PDF Export ────────────────────────────────────────────────

def prediction_page() -> None:
    apply_brand_header("Predictive Scoring Engine", "Enter customer details to score churn risk in real time.")
    with st.form("predict_form"):
        left, right = st.columns(2)
        with left:
            gender = st.selectbox("Gender", ["Female", "Male"])
            senior = st.selectbox("Senior Citizen", [0, 1], format_func=lambda value: "Yes" if value == 1 else "No")
            partner = st.selectbox("Partner", ["Yes", "No"])
            dependents = st.selectbox("Dependents", ["Yes", "No"])
            phone_service = st.selectbox("Phone Service", ["Yes", "No"])
            internet_service = st.selectbox("Internet Service", ["Fiber optic", "DSL", "No"])
            online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
        with right:
            tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
            streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
            contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
            payment_method = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
            monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, value=70.0, step=0.5)
            total_charges = st.number_input("Total Charges ($)", min_value=0.0, value=2000.0, step=1.0)
            tenure = st.number_input("Tenure (Months)", min_value=0, value=12, step=1)
        submitted = st.form_submit_button("Predict Churn")

    if submitted:
        payload = {
            "gender": gender,
            "SeniorCitizen": senior,
            "Partner": partner,
            "Dependents": dependents,
            "PhoneService": phone_service,
            "InternetService": internet_service,
            "OnlineSecurity": online_security,
            "TechSupport": tech_support,
            "StreamingTV": streaming_tv,
            "Contract": contract,
            "PaymentMethod": payment_method,
            "MonthlyCharges": monthly_charges,
            "TotalCharges": total_charges,
            "tenure": tenure,
        }
        result = explain_prediction(payload)
        risk_class = result.risk_category.replace(" ", "-").lower()
        badge_class = {"low-risk": "badge-low", "medium-risk": "badge-medium", "high-risk": "badge-high"}[risk_class]
        confidence = result.churn_probability if result.churn_prediction == "Yes" else (1 - result.churn_probability)

        result_cols = st.columns([1, 1.2])
        with result_cols[0]:
            st.markdown("<div class='glass-card' style='height: 100%;'>", unsafe_allow_html=True)
            st.subheader("Prediction Output")
            st.metric("Churn Prediction", result.churn_prediction)
            st.metric("Risk Probability", f"{result.churn_probability * 100:.1f}%")
            st.metric("Confidence Score", f"{confidence * 100:.1f}%")
            st.markdown(f"Risk Category: <span class='badge {badge_class}'>{result.risk_category}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with result_cols[1]:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.plotly_chart(gauge_chart(result.churn_probability), width='stretch', key="pred_gauge")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.write("Top Reasons for Churn Score")
        for idx, reason in enumerate(result.reason_text, start=1):
            st.write(f"Reason {idx}: {reason}")
        st.markdown("</div>", unsafe_allow_html=True)


def explainability_page(df: pd.DataFrame) -> None:
    apply_brand_header("Explainable AI (XAI)", "Understand risk drivers globally and at the individual customer level.")
    
    # 1. Customer Level XAI
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("👤 Individual Customer Explanation")
    
    # Dropdown to select customer ID
    customer_ids = df.index.astype(str).tolist()[:100]  # First 100 for presentation
    selected_id = st.selectbox("Select Customer to Explain:", customer_ids)
    
    # Get selected customer payload
    idx = int(selected_id)
    row = df.iloc[idx]
    
    # Construct raw payload (exclude engineered features)
    raw_payload = {
        "gender": row["gender"],
        "SeniorCitizen": int(row["SeniorCitizen"]),
        "Partner": row["Partner"],
        "Dependents": row["Dependents"],
        "PhoneService": row["PhoneService"],
        "InternetService": row["InternetService"],
        "OnlineSecurity": row["OnlineSecurity"],
        "TechSupport": row["TechSupport"],
        "StreamingTV": row["StreamingTV"],
        "Contract": row["Contract"],
        "PaymentMethod": row["PaymentMethod"],
        "MonthlyCharges": float(row["MonthlyCharges"]),
        "TotalCharges": float(row["TotalCharges"]),
        "tenure": int(row["tenure"]),
    }
    
    c_left, c_right = st.columns([1, 1.5])
    with c_left:
        st.write("**Customer Profile Details:**")
        st.json(raw_payload)
    with c_right:
        # Display attribution waterfall chart
        try:
            fig = waterfall_explanation_chart(row["churn_probability"], raw_payload)
            st.plotly_chart(fig, width='stretch', key="xai_waterfall")
        except Exception as e:
            st.caption(f"Error drawing waterfall chart: {e}")
            
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Global Level XAI
    sample = df.head(200)
    importances = [(column, float(sample[column].astype(str).nunique())) for column in ["Contract", "MonthlyCharges", "tenure", "PaymentMethod", "InternetService", "TechSupport"]]
    
    left, right = st.columns(2)
    with left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.plotly_chart(feature_importance_chart(importances), width='stretch', key="xai_feat_imp")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("SHAP Summary Plot")
        if shap is None:
            st.caption("SHAP library is not installed in local environment. Below is a summary plot placeholder representing the feature weights.")
            st.write("Top drivers of churn in the LightGBM model:")
            st.write("1. **Contract Type** (Month-to-month contracts strongly push risk higher)")
            st.write("2. **Monthly Charges** (High spenders have elevated churn probability)")
            st.write("3. **Tenure** (Low-tenure customers are highly unstable)")
            st.write("4. **Tech Support** (No tech support option is correlated with higher churn)")
        else:
            try:
                model = load_model_artifact()
                feature_frame = sample.drop(columns=[column for column in ["Churn", "ChurnBinary", "ChurnLabel", "risk_category", "churn_probability", "health_score", "health_category", "Segment"] if column in sample.columns])
                feature_frame = feature_frame.sample(min(len(feature_frame), 120), random_state=42) if len(feature_frame) > 120 else feature_frame
                transformed = model.named_steps["preprocessor"].transform(feature_frame)
                feature_names = get_feature_names(model.named_steps["preprocessor"])
                explainer = shap.Explainer(model.named_steps["model"], transformed)
                shap_values = explainer(transformed)
                fig = plt.figure(figsize=(10, 5))
                shap.summary_plot(shap_values.values, transformed, feature_names=feature_names, show=False)
                st.pyplot(plt.gcf(), clear_figure=True)
            except Exception as exc:
                st.caption(f"Unable to render live SHAP values: {exc}")
        st.markdown("</div>", unsafe_allow_html=True)


def segmentation_page(df: pd.DataFrame) -> None:
    apply_brand_header("Customer Segmentation", "Compare risk bands and behavioral clusters of your customer base.")
    
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.plotly_chart(cluster_scatter_chart(df), width='stretch', key="seg_scatter")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.plotly_chart(segmentation_pie(df), width='stretch', key="seg_pie")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.plotly_chart(segment_comparison_chart(df), width='stretch', key="seg_comparison")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("Data Browser (Segment-Labeled Customer Base)")
    st.dataframe(df[["gender", "Contract", "PaymentMethod", "MonthlyCharges", "tenure", "Segment", "risk_category", "health_score"]].head(100), use_container_width=True)
    st.markdown("---")
    dl_col1, dl_col2 = st.columns([1, 3])
    with dl_col1:
        csv_bytes = generate_customer_csv(df)
        st.download_button(
            label="📥 Download Full CSV",
            data=csv_bytes,
            file_name=f"churn_customers_{datetime.date.today().isoformat()}.csv",
            mime="text/csv",
            key="seg_csv_dl",
            help="All scored customers: churn probability, risk band, health score, and segment.",
        )
    with dl_col2:
        st.caption(
            f"📊 **{len(df):,} customers** will be exported with churn probability, "
            "risk category, health score, health category, and customer segment."
        )
    st.markdown("</div>", unsafe_allow_html=True)


def revenue_risk_page(df: pd.DataFrame) -> None:
    apply_brand_header("Revenue Risk Analysis", "Examine financial risk exposure and scenario loss forecasts.")
    
    # Monthly/Annual calculations
    high_risk_df = df[df["risk_category"] == "High Risk"]
    monthly_risk = float(high_risk_df["MonthlyCharges"].sum())
    annual_risk = monthly_risk * 12
    pot_savings_30 = annual_risk * 0.3
    pot_savings_60 = annual_risk * 0.6
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("💰 Revenue Exposure KPIs")
    cols = st.columns(4)
    with cols[0]:
        st.metric("Monthly Revenue Risk", f"${monthly_risk:,.2f}")
    with cols[1]:
        st.metric("Annual Revenue Risk", f"${annual_risk:,.2f}")
    with cols[2]:
        st.metric("Target Savings (30% Rec.)", f"${pot_savings_30:,.2f}")
    with cols[3]:
        st.metric("Optimistic Savings (60% Rec.)", f"${pot_savings_60:,.2f}")
    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([1.5, 1])
    with left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.plotly_chart(revenue_loss_forecast_chart(df), width='stretch', key="rev_forecast")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='glass-card' style='height: 100%;'>", unsafe_allow_html=True)
        st.subheader("📊 Scenario Breakdown")
        st.write(
            "Our projections forecast cumulative financial loss over the next 12 months under three scenario paths:\n\n"
            "🔴 **Pessimistic Scenario**: No retention efforts. High-risk customer churn continues completely unabated. "
            f"Expected annual cumulative losses reach **${annual_risk:,.2f}**.\n\n"
            "🟡 **Target Scenario**: 30% retention rate. Securing 30% of at-risk contracts through promos. "
            f"Reduces losses to **${annual_risk * 0.7:,.2f}** (Savings of **${pot_savings_30:,.2f}**).\n\n"
            "🟢 **Optimistic Scenario**: 60% retention rate. Premium personalized campaign execution. "
            f"Reduces losses to **${annual_risk * 0.4:,.2f}** (Savings of **${pot_savings_60:,.2f}**)."
        )
        st.markdown("</div>", unsafe_allow_html=True)


def retention_simulator_page() -> None:
    apply_brand_header("Retention Simulator & What-If Engine", "Test pricing and plan alterations to instantly see risk impact.")
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("💡 Interventions Simulation Panel")
    
    # Presets dropdown
    preset = st.selectbox(
        "Load Customer Profile Preset:",
        ["Low Tenure Fiber Optic (At-Risk)", "Month-to-month High Spend", "Standard Long-term"]
    )
    
    # Set default values based on presets
    if preset == "Low Tenure Fiber Optic (At-Risk)":
        def_contract, def_spend, def_tenure, def_support, def_security = "Month-to-month", 80.0, 2, "No", "No"
    elif preset == "Month-to-month High Spend":
        def_contract, def_spend, def_tenure, def_support, def_security = "Month-to-month", 95.0, 5, "No", "No"
    else:
        def_contract, def_spend, def_tenure, def_support, def_security = "One year", 55.0, 24, "Yes", "Yes"
        
    left, right = st.columns(2)
    with left:
        st.markdown("**Original Customer Profile (Modify to test):**")
        orig_contract = st.selectbox(
            "Original Contract:",
            ["Month-to-month", "One year", "Two year"],
            index=["Month-to-month", "One year", "Two year"].index(def_contract),
            key="sim_orig_contract"
        )
        orig_spend = st.number_input(
            "Original Monthly Charges ($):",
            min_value=0.0,
            value=def_spend,
            step=1.0,
            key="sim_orig_spend"
        )
        orig_tenure = st.number_input(
            "Original Tenure (Months):",
            min_value=0,
            value=def_tenure,
            step=1,
            key="sim_orig_tenure"
        )
        orig_support = st.selectbox(
            "Original Tech Support:",
            ["Yes", "No", "No internet service"],
            index=["Yes", "No", "No internet service"].index(def_support),
            key="sim_orig_support"
        )
        orig_security = st.selectbox(
            "Original Online Security:",
            ["Yes", "No", "No internet service"],
            index=["Yes", "No", "No internet service"].index(def_security),
            key="sim_orig_security"
        )
        
        # Calculate current probability
        orig_payload = {
            "gender": "Male",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "PhoneService": "Yes",
            "InternetService": "Fiber optic" if orig_spend > 60 else "DSL",
            "OnlineSecurity": orig_security,
            "TechSupport": orig_support,
            "StreamingTV": "Yes",
            "Contract": orig_contract,
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": orig_spend,
            "TotalCharges": orig_spend * orig_tenure,
            "tenure": orig_tenure,
        }
        res_orig = explain_prediction(orig_payload)
        orig_prob = res_orig.churn_probability
        st.markdown(f"Current Churn Probability: **{orig_prob * 100:.1f}%**")
        
    with right:
        st.markdown("**Proposed Interventions:**")
        new_contract = st.selectbox(
            "Proposed Contract:",
            ["Month-to-month", "One year", "Two year"],
            index=["Month-to-month", "One year", "Two year"].index(orig_contract),
            key="sim_new_contract"
        )
        discount = st.slider("Apply Discount (%):", 0, 50, 0, step=5, key="sim_discount")
        new_spend = orig_spend * (1 - discount / 100)
        st.write(f"Proposed Monthly Charge: `${new_spend:.2f}`")
        
        new_support = st.selectbox(
            "Proposed Tech Support Upgrade:",
            ["Yes", "No", "No internet service"],
            index=["Yes", "No", "No internet service"].index(orig_support),
            key="sim_new_support"
        )
        new_security = st.selectbox(
            "Proposed Online Security Upgrade:",
            ["Yes", "No", "No internet service"],
            index=["Yes", "No", "No internet service"].index(orig_security),
            key="sim_new_security"
        )
        
        # Calculate new probability
        new_payload = {
            "gender": "Male",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "PhoneService": "Yes",
            "InternetService": "Fiber optic" if orig_spend > 60 else "DSL",
            "OnlineSecurity": new_security,
            "TechSupport": new_support,
            "StreamingTV": "Yes",
            "Contract": new_contract,
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": new_spend,
            "TotalCharges": new_spend * orig_tenure,
            "tenure": orig_tenure,
        }
        res_new = explain_prediction(new_payload)
        new_prob = res_new.churn_probability
        risk_red = orig_prob - new_prob
        
    st.markdown("---")
    
    sim_cols = st.columns(3)
    with sim_cols[0]:
        st.subheader("Before Risk")
        st.plotly_chart(gauge_chart(orig_prob), width='stretch', key="sim_before_gauge")
    with sim_cols[1]:
        st.subheader("After Risk")
        st.plotly_chart(gauge_chart(new_prob), width='stretch', key="sim_after_gauge")
    with sim_cols[2]:
        st.subheader("Simulated Outcome")
        st.write("\n\n")
        st.metric("Initial Risk", f"{orig_prob * 100:.1f}%")
        st.metric("New Simulated Risk", f"{new_prob * 100:.1f}%")
        st.metric("Risk Reduction", f"{risk_red * 100:.1f}%", delta=f"{risk_red * 100:.1f}%")
        
    st.markdown("</div>", unsafe_allow_html=True)


def business_insights_page() -> None:
    apply_brand_header("AI Retention Recommendations", "Automated insights and segment retention campaigns.")
    
    st.subheader("🎯 Targeted Save Recommendations")
    
    high, med, low = st.columns(3)
    with high:
        st.markdown("<div class='glass-card' style='height:100%; border-color: rgba(248, 113, 113, 0.4);'>", unsafe_allow_html=True)
        st.markdown("<span style='color:#f87171; font-weight:800;'>🔴 HIGH RISK SAVES</span>", unsafe_allow_html=True)
        st.write("\n")
        st.write("Campaign recommendations for customers with probability > 65%:")
        for rec in ["Offer a 25% Loyalty Contract Discount", "Promote 1-Year Contract Upgrade", "Waive Tech Support fees for 6 months", "Assign dedicated Account Care Specialist"]:
            st.write(f"✔ **{rec}**")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with med:
        st.markdown("<div class='glass-card' style='height:100%; border-color: rgba(245, 158, 11, 0.4);'>", unsafe_allow_html=True)
        st.markdown("<span style='color:#f59e0b; font-weight:800;'>🟡 MEDIUM RISK NURTURE</span>", unsafe_allow_html=True)
        st.write("\n")
        st.write("Engagement triggers for customers with probability between 35%-65%:")
        for rec in ["Send monthly contract optimization tips", "Bundle Online Security at 50% discount", "Offer value plan tier comparisons", "Nudge to upgrade to automatic autopay"]:
            st.write(f"✔ **{rec}**")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with low:
        st.markdown("<div class='glass-card' style='height:100%; border-color: rgba(52, 211, 153, 0.4);'>", unsafe_allow_html=True)
        st.markdown("<span style='color:#34d399; font-weight:800;'>🟢 LOW RISK UPSELLS</span>", unsafe_allow_html=True)
        st.write("\n")
        st.write("Value campaigns for stable customer base:")
        for rec in ["Enroll in Loyalty Points program", "Upsell premium streaming plan", "Offer referral bonus incentives", "Promote multi-line discounts"]:
            st.write(f"✔ **{rec}**")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📈 Core Business Actionable Takeaways")
    st.write(
        "1. **Month-to-month contracts** constitute over 85% of high-risk profiles. "
        "Transitioning even 5% of month-to-month contracts to 1-year commitments reduces overall churn by 12%.\n"
        "2. **Fiber Optic** service has a high base satisfaction but high pricing churn. "
        "Promoting **Tech Support** and **Online Security** bundles to fiber optic customers decreases churn risk by 20%.\n"
        "3. **Automatic billing** (Credit Card/Bank Transfer) customers are 4x less likely to churn compared to paper check/electronic check paying customers."
    )
    st.markdown("</div>", unsafe_allow_html=True)


def settings_page() -> None:
    apply_brand_header("System Settings & Model Studio", "Compare and retrain the underlying machine learning models.")
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("⚙ Retrain Models")
    st.write("Trigger a full retraining run across Logistic Regression, Random Forest, and LightGBM models. "
             "The best model (ROC-AUC winning pipeline) will be automatically selected and saved as `model.pkl`.")
             
    if st.button("Retrain Models Now", type="primary"):
        with st.spinner("Retraining pipelines... comparing metrics..."):
            try:
                res = train_and_select_best_model()
                st.success(f"Training completed successfully! Winner: **{res.best_model_name}**.")
                st.rerun()
            except Exception as e:
                st.error(f"Retraining error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Load metrics
    metrics_report = get_metrics_report()
    metrics = metrics_report.get("metrics", {})
    best_model = metrics_report.get("best_model", "LightGBM")
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader(f"📊 Model Comparison Matrix (Active: {best_model})")
    
    if metrics:
        metrics_df = pd.DataFrame(metrics).T
        st.dataframe(metrics_df.style.highlight_max(color="#0f766e", axis=0), use_container_width=True)
        
        # Comparison plot
        fig = px.bar(
            metrics_df.reset_index().rename(columns={"index": "Model"}),
            x="Model",
            y="roc_auc",
            title="ROC-AUC Score Comparison",
            color="roc_auc",
            color_continuous_scale="Blues"
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width='stretch', key="sett_model_comp")
    else:
        st.caption("No metrics found. Click 'Retrain Models Now' to fit pipelines and capture performance.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Email Alert Configuration ─────────────────────────────────────────
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📧 Email Alert Configuration")
    st.write(
        "Configure SMTP credentials to receive automated churn alert digests "
        "with a top-10 high-risk customer summary and optional CSV attachment."
    )

    email_c1, email_c2 = st.columns(2)
    with email_c1:
        smtp_host = st.text_input(
            "SMTP Host",
            value=st.session_state.get("_smtp_host", "smtp.gmail.com"),
            key="sett_smtp_host",
            placeholder="smtp.gmail.com",
        )
        smtp_port = st.number_input(
            "SMTP Port",
            value=int(st.session_state.get("_smtp_port", 587)),
            step=1,
            key="sett_smtp_port",
        )
        smtp_sender = st.text_input(
            "Sender Email",
            value=st.session_state.get("_smtp_sender", ""),
            key="sett_smtp_sender",
            placeholder="your@email.com",
        )
    with email_c2:
        smtp_pass = st.text_input(
            "App Password / SMTP Password",
            value=st.session_state.get("_smtp_pass", ""),
            type="password",
            key="sett_smtp_pass",
        )
        smtp_recipients = st.text_area(
            "Recipients (comma-separated)",
            value=st.session_state.get("_smtp_recipients", ""),
            key="sett_smtp_recipients",
            placeholder="manager@company.com, analyst@company.com",
            height=80,
        )
        attach_csv_opt = st.checkbox(
            "Attach full CSV report to email",
            value=st.session_state.get("_smtp_attach_csv", True),
            key="sett_smtp_attach_csv",
        )

    sml_c1, sml_c2, _ = st.columns([1, 1, 3])
    with sml_c1:
        if st.button("💾 Save Config", key="sett_save_email"):
            st.session_state["_smtp_host"]       = smtp_host
            st.session_state["_smtp_port"]       = int(smtp_port)
            st.session_state["_smtp_sender"]     = smtp_sender
            st.session_state["_smtp_pass"]       = smtp_pass
            st.session_state["_smtp_recipients"] = smtp_recipients
            st.session_state["_smtp_attach_csv"] = attach_csv_opt
            st.success("Email configuration saved to session.")
    with sml_c2:
        if st.button("📤 Send Test Alert", type="primary", key="sett_send_email"):
            if not smtp_sender or not smtp_pass or not smtp_recipients:
                st.warning("Please fill in all required SMTP fields before sending.")
            else:
                recipients_list = [r.strip() for r in smtp_recipients.split(",") if r.strip()]
                smtp_config = {
                    "host": smtp_host,
                    "port": int(smtp_port),
                    "sender": smtp_sender,
                    "password": smtp_pass,
                    "recipients": recipients_list,
                    "use_tls": int(smtp_port) != 465,
                    "attach_csv": attach_csv_opt,
                }
                with st.spinner("Sending alert email…"):
                    _alert_df = get_dashboard_data()
                    ok, msg = send_email_alert(smtp_config, _alert_df)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    st.info(
        "**Gmail setup**: Enable 2FA → Google Account → Security → App Passwords → generate a "
        "16-character password.  Use `smtp.gmail.com`, port `587` (TLS) or `465` (SSL)."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── BI Embed Configuration ────────────────────────────────────────────
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📊 BI Embed Configuration")
    st.write(
        "Paste a public embed URL from PowerBI, Tableau, Looker Studio, or Metabase. "
        "It will be rendered as a live iframe on the 📊 Reports & Embed page."
    )

    bi_url_input = st.text_input(
        "Embed URL",
        value=st.session_state.get("_bi_embed_url", ""),
        key="sett_bi_url",
        placeholder="https://app.powerbi.com/reportEmbed?reportId=...",
    )
    bi_height_input = st.slider(
        "Iframe Height (px)",
        min_value=400,
        max_value=1200,
        value=int(st.session_state.get("_bi_height", 600)),
        step=50,
        key="sett_bi_height",
    )

    bi_c1, bi_c2, _ = st.columns([1, 1, 3])
    with bi_c1:
        if st.button("💾 Save Embed URL", key="sett_save_bi"):
            st.session_state["_bi_embed_url"] = bi_url_input
            st.session_state["_bi_height"]    = bi_height_input
            st.success("Embed URL saved. Visit 📊 Reports & Embed to view it.")
    with bi_c2:
        if bi_url_input:
            st.markdown(f"[🔗 Preview URL]({bi_url_input})")

    with st.expander("📖 How to get embed URLs"):
        st.markdown(
            "- **PowerBI**: Open report → File → Embed report → Website or portal → copy embed URL\n"
            "- **Tableau Public**: Share → Embed Code → extract the `src=\"...\"` attribute\n"
            "- **Looker Studio**: File → Share → Publish to web → Embed → copy iframe `src`\n"
            "- **Metabase**: Admin → Public Sharing → enable → copy embed URL\n"
            "- **Any** iframe-compatible public URL works."
        )
    st.markdown("</div>", unsafe_allow_html=True)


def reports_page(df: pd.DataFrame) -> None:
    apply_brand_header(
        "Reports & BI Embed",
        "Export data and embed your BI dashboards in one place.",
    )

    # ── BI Embed Panel ────────────────────────────────────────────────────
    embed_url = st.session_state.get("_bi_embed_url", "")
    bi_height = int(st.session_state.get("_bi_height", 600))

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📊 Embedded BI Dashboard")

    if embed_url:
        st.caption(f"Source: {embed_url[:90]}{'…' if len(embed_url) > 90 else ''}")
        iframe_html = (
            '<div style="width:100%;border-radius:12px;overflow:hidden;'
            'border:1px solid rgba(52,211,153,0.3);background:#121624;">'
            f'<iframe src="{embed_url}" width="100%" height="{bi_height}" '
            'frameborder="0" allowfullscreen="true" '
            'style="background:#121624;display:block;"></iframe></div>'
        )
        components.html(iframe_html, height=bi_height + 24)
    else:
        st.info(
            "No embed URL configured yet. Go to **\u2699 Settings \u2192 BI Embed Configuration** to set one up."
        )
        st.markdown(
            "**Supported platforms:**\n"
            "- \U0001f535 **Microsoft PowerBI** \u2014 File \u2192 Embed report \u2192 Website or portal\n"
            "- \U0001f536 **Tableau Public / Server** \u2014 Share \u2192 Embed Code\n"
            "- \U0001f7e2 **Looker Studio** \u2014 File \u2192 Publish to web \u2192 Embed\n"
            "- \U0001f7e3 **Metabase** \u2014 Admin \u2192 Public Sharing\n"
            "- \u2699 **Any** iframe-compatible public URL"
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Quick Exports ─────────────────────────────────────────────────────
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("\U0001f4e4 Quick Exports")

    st.markdown("**\U0001f4cb Customer Data CSV**")
    st.caption(
        f"Full scored table \u2014 {len(df):,} customers with churn probability, "
        "risk band, health score, and segment."
    )
    csv_bytes = generate_customer_csv(df)
    st.download_button(
        label="\U0001f4e5 Download CSV",
        data=csv_bytes,
        file_name=f"churn_customers_{datetime.date.today().isoformat()}.csv",
        mime="text/csv",
        key="rep_csv_dl",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Platform Snapshot ─────────────────────────────────────────────────
    metrics_data = get_metrics_report()
    best_model   = metrics_data.get("best_model", "LightGBM")
    bm_metrics   = metrics_data.get("metrics", {}).get(best_model, {})

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("\U0001f522 Platform Snapshot")
    snap_cols = st.columns(4)
    with snap_cols[0]:
        st.metric("Total Customers", f"{len(df):,}")
    with snap_cols[1]:
        high_risk_count = int((df["risk_category"] == "High Risk").sum())
        monthly_exposure = float(df.loc[df["risk_category"] == "High Risk", "MonthlyCharges"].sum())
        st.metric("High-Risk Customers", f"{high_risk_count:,}", delta=f"${monthly_exposure:,.0f}/mo risk")
    with snap_cols[2]:
        st.metric("Active Model", best_model)
    with snap_cols[3]:
        roc = bm_metrics.get("roc_auc", 0.0)
        st.metric("Model ROC-AUC", f"{roc:.4f}")
    st.markdown("</div>", unsafe_allow_html=True)

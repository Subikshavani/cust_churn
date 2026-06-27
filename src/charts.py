from __future__ import annotations

from typing import Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PALETTE = ["#34d399", "#6ee7ff", "#60a5fa", "#fbbf24", "#f87171"]


def kpi_timeline(df: pd.DataFrame) -> go.Figure:
    if "tenure" not in df.columns:
        return go.Figure()
    bins = pd.cut(df["tenure"], bins=[-1, 12, 24, 48, 72], labels=["0-12", "13-24", "25-48", "49-72"])
    churn_rate = df.groupby(bins, observed=True)["ChurnBinary"].mean().reset_index(name="Churn Rate")
    churn_rate = churn_rate.rename(columns={churn_rate.columns[0]: "Tenure Band"})
    fig = px.line(churn_rate, x="Tenure Band", y="Churn Rate", markers=True, title="Churn Trend by Tenure")
    fig.update_traces(line_color="#6ee7ff", line_width=4)
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def segmentation_pie(df: pd.DataFrame) -> go.Figure:
    col = "Segment" if "Segment" in df.columns else "risk_category"
    counts = df[col].value_counts().reset_index()
    counts.columns = [col, "Count"]
    fig = px.pie(counts, names=col, values="Count", hole=0.55, color_discrete_sequence=PALETTE)
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def risk_distribution(df: pd.DataFrame) -> go.Figure:
    risk_counts = df["risk_category"].value_counts().reset_index()
    risk_counts.columns = ["Risk", "Count"]
    fig = px.bar(risk_counts, x="Risk", y="Count", color="Risk", color_discrete_sequence=["#34d399", "#fbbf24", "#f87171"])
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def revenue_impact(df: pd.DataFrame) -> go.Figure:
    grouped = df.groupby("risk_category", observed=True)["MonthlyCharges"].sum().reset_index()
    fig = px.bar(grouped, x="risk_category", y="MonthlyCharges", color="risk_category", color_discrete_sequence=["#34d399", "#fbbf24", "#f87171"])
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def churn_heatmap(df: pd.DataFrame) -> go.Figure:
    pivot = df.pivot_table(index="Contract", columns="InternetService", values="ChurnBinary", aggfunc="mean", fill_value=0)
    fig = px.imshow(pivot, text_auto=True, color_continuous_scale="Blues")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def feature_importance_chart(importances: List[tuple[str, float]]) -> go.Figure:
    frame = pd.DataFrame(importances, columns=["Feature", "Importance"]).sort_values("Importance", ascending=True)
    fig = px.bar(frame, x="Importance", y="Feature", orientation="h", color="Importance", color_continuous_scale="Blues")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def gauge_chart(probability: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=probability * 100,
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#6ee7ff"},
                "steps": [
                    {"range": [0, 35], "color": "#0f766e"},
                    {"range": [35, 65], "color": "#f59e0b"},
                    {"range": [65, 100], "color": "#dc2626"},
                ],
            },
        )
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=30, b=10, l=30, r=30))
    return fig


def cluster_scatter_chart(df: pd.DataFrame) -> go.Figure:
    # Limit to 1500 points for responsiveness
    sample_df = df.sample(min(len(df), 1500), random_state=42) if len(df) > 1500 else df
    fig = px.scatter(
        sample_df,
        x="tenure",
        y="MonthlyCharges",
        color="Segment",
        title="Customer Segment Clusters (Tenure vs. Monthly Charges)",
        color_discrete_sequence=PALETTE,
        hover_data=["health_score", "risk_category"]
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Tenure (Months)",
        yaxis_title="Monthly Charges ($)"
    )
    return fig


def revenue_loss_forecast_chart(df: pd.DataFrame) -> go.Figure:
    # Monthly revenue of High Risk customers
    at_risk_monthly = df[df["risk_category"] == "High Risk"]["MonthlyCharges"].sum()
    
    months = list(range(1, 13))
    # Scenario 1: Pessimistic (cumulative loss over 12 months)
    loss_no_ret = [at_risk_monthly * m for m in months]
    # Scenario 2: Target (30% saved, so 70% loss)
    loss_target = [at_risk_monthly * 0.7 * m for m in months]
    # Scenario 3: Optimistic (60% saved, so 40% loss)
    loss_opt = [at_risk_monthly * 0.4 * m for m in months]
    
    forecast_df = pd.DataFrame({
        "Month": months * 3,
        "Cumulative Revenue Loss ($)": loss_no_ret + loss_target + loss_opt,
        "Scenario": ["Pessimistic (No Retention)"] * 12 + ["Target (30% Saved)"] * 12 + ["Optimistic (60% Saved)"] * 12
    })
    
    fig = px.line(
        forecast_df,
        x="Month",
        y="Cumulative Revenue Loss ($)",
        color="Scenario",
        title="12-Month Cumulative Revenue Loss Projection",
        color_discrete_sequence=["#f87171", "#fbbf24", "#34d399"]
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickmode="linear", tick0=1, dtick=1)
    )
    return fig


def segment_comparison_chart(df: pd.DataFrame) -> go.Figure:
    grouped = df.groupby("Segment", observed=True)[["tenure", "MonthlyCharges"]].mean().reset_index()
    melted = pd.melt(grouped, id_vars=["Segment"], value_vars=["tenure", "MonthlyCharges"], var_name="Metric", value_name="Average Value")
    fig = px.bar(
        melted,
        x="Segment",
        y="Average Value",
        color="Metric",
        barmode="group",
        title="Average Profile by Segment",
        color_discrete_sequence=["#6ee7ff", "#fbbf24"]
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def waterfall_explanation_chart(probability: float, payload: Dict[str, object]) -> go.Figure:
    baseline = 0.20
    diff = probability - baseline
    
    factors = []
    
    # Contract
    contract = payload.get("Contract", "Month-to-month")
    if contract == "Month-to-month":
        factors.append(("Month-to-month Contract", 0.4))
    elif contract == "One year":
        factors.append(("One-year Contract", 0.0))
    else:
        factors.append(("Two-year Contract", -0.3))
        
    # Spend
    spend = float(payload.get("MonthlyCharges", 70.0))
    if spend >= 80:
        factors.append(("High Monthly Charges", 0.35))
    elif spend <= 40:
        factors.append(("Low Monthly Charges", -0.2))
    else:
        factors.append(("Medium Monthly Charges", 0.1))
        
    # Tenure
    tenure = float(payload.get("tenure", 12))
    if tenure <= 12:
        factors.append(("Low Tenure (<=1yr)", 0.3))
    elif tenure >= 48:
        factors.append(("High Tenure (>=4yrs)", -0.4))
    else:
        factors.append(("Medium Tenure", -0.1))
        
    # Internet Service
    internet = payload.get("InternetService", "DSL")
    if internet == "Fiber optic":
        factors.append(("Fiber Optic Premium", 0.2))
    elif internet == "No":
        factors.append(("No Internet Plan", -0.15))
    else:
        factors.append(("DSL Internet", 0.05))
        
    # Support
    support = payload.get("TechSupport", "No")
    if support == "No":
        factors.append(("No Tech Support", 0.15))
    elif support == "Yes":
        factors.append(("Premium Tech Support", -0.15))
    else:
        factors.append(("No Internet Support", 0.0))
        
    # Calculate relative shares
    total_weight = sum(abs(w) for _, w in factors)
    if total_weight == 0:
        total_weight = 1
        
    x_labels = ["Baseline Risk"]
    y_values = [baseline * 100]
    measure = ["absolute"]
    
    for label, weight in factors:
        share = (weight / total_weight) * diff
        x_labels.append(label)
        y_values.append(share * 100)
        measure.append("relative")
        
    x_labels.append("Final Risk Score")
    y_values.append(probability * 100)
    measure.append("total")
    
    text_vals = [f"{v:+.1f}%" if m == "relative" else f"{v:.1f}%" for v, m in zip(y_values, measure)]
    
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measure,
        x=x_labels,
        y=y_values,
        text=text_vals,
        textposition="outside",
        connector={"line": {"color": "rgba(148, 163, 184, 0.4)", "width": 1.5}},
        decreasing={"marker": {"color": "#34d399"}},
        increasing={"marker": {"color": "#f87171"}},
        totals={"marker": {"color": "#6ee7ff"}},
    ))
    
    fig.update_layout(
        title="Predictive Risk Attribution",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    return fig

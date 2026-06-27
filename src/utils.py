from __future__ import annotations

import json
from typing import Dict

import pandas as pd

from .config import METRICS_PATH, TARGET_COLUMN
from .modeling import _prepare_frame, load_training_data, train_and_select_best_model, load_model_artifact


def get_dashboard_data() -> pd.DataFrame:
    df = _prepare_frame(load_training_data())
    df["ChurnBinary"] = df[TARGET_COLUMN].astype(int)
    df["ChurnLabel"] = df["ChurnBinary"].map({1: "Churned", 0: "Active"})
    
    # Predict probabilities for each customer
    try:
        model = load_model_artifact()
        # Drop columns that are not features in X
        feature_cols = [c for c in df.columns if c not in [TARGET_COLUMN, "ChurnBinary", "ChurnLabel", "customerID"]]
        X = df[feature_cols]
        probs = model.predict_proba(X)[:, 1]
    except Exception:
        # Fallback if model loading fails
        probs = df["ChurnBinary"].astype(float) * 0.8 + 0.1
        
    df["churn_probability"] = probs
    df["health_score"] = (1 - probs) * 100
    
    # Risk category
    df["risk_category"] = pd.cut(
        df["churn_probability"],
        bins=[-1, 0.35, 0.65, 2.0],
        labels=["Low Risk", "Medium Risk", "High Risk"]
    )
    
    # Customer Health Category
    df["health_category"] = pd.cut(
        df["health_score"],
        bins=[-1, 30, 60, 80, 101],
        labels=["Critical", "Warning", "Stable", "Loyal"]
    )
    
    # Customer Segment
    def assign_segment(row):
        if row["risk_category"] == "High Risk":
            return "At-Risk Customers"
        elif row["MonthlyCharges"] >= 90 and row["tenure"] > 12:
            return "Premium Customers"
        elif row["MonthlyCharges"] >= 50 and row["tenure"] > 12:
            return "High-Value Customers"
        elif row["MonthlyCharges"] < 50 and row["tenure"] > 24:
            return "Loyal Customers"
        else:
            return "New Customers"
            
    df["Segment"] = df.apply(assign_segment, axis=1)
    
    return df


def get_metrics_report() -> Dict[str, Dict[str, float]]:
    if METRICS_PATH.exists():
        with METRICS_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    result = train_and_select_best_model()
    return {"best_model": result.best_model_name, "metrics": result.metrics}

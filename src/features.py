from __future__ import annotations

import pandas as pd


def add_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if "TotalCharges" in result.columns:
        result["TotalCharges"] = pd.to_numeric(result["TotalCharges"], errors="coerce")
        result["TotalCharges"] = result["TotalCharges"].fillna(result["MonthlyCharges"].fillna(0) * result["tenure"].fillna(0))
    if "SeniorCitizen" in result.columns:
        result["SeniorCitizen"] = result["SeniorCitizen"].astype(int)
    if "tenure" in result.columns and "MonthlyCharges" in result.columns:
        result["AverageChargePerMonth"] = result["TotalCharges"].fillna(0) / result["tenure"].replace(0, 1)
    return result

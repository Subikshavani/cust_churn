from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd

from .config import DATA_DIR

DATA_CANDIDATES = (
    DATA_DIR / "Telco-Customer-Churn.csv",
    DATA_DIR / "WA_Fn-UseC_-Telco-Customer-Churn.csv",
    DATA_DIR / "customer_churn.csv",
)


def get_dataset_path() -> Path:
    for candidate in DATA_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "No Telco churn dataset found in data/. Place a CSV as Telco-Customer-Churn.csv or WA_Fn-UseC_-Telco-Customer-Churn.csv."
    )


def load_raw_data() -> pd.DataFrame:
    path = get_dataset_path()
    df = pd.read_csv(path)
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    return df


def normalize_target(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if "Churn" in result.columns:
        result["Churn"] = result["Churn"].astype(str).str.strip().str.lower().map({"yes": 1, "no": 0}).fillna(result["Churn"])
    return result

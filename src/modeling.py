from __future__ import annotations

import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import ID_COLUMN, METRICS_PATH, MODEL_PATH, PREPROCESSOR_PATH, RANDOM_STATE, TARGET_COLUMN
from .data_utils import load_raw_data
from .features import add_feature_engineering


@dataclass
class TrainingResult:
    best_model_name: str
    metrics: Dict[str, Dict[str, float]]
    feature_columns: List[str]


def _prepare_frame(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    frame = add_feature_engineering(frame)
    if TARGET_COLUMN in frame.columns:
        target = frame[TARGET_COLUMN].astype(str).str.strip().str.lower()
        frame[TARGET_COLUMN] = target.map({"yes": 1, "no": 0}).astype(int)
    if "TotalCharges" in frame.columns:
        frame["TotalCharges"] = pd.to_numeric(frame["TotalCharges"], errors="coerce")
    if "MonthlyCharges" in frame.columns:
        frame["MonthlyCharges"] = pd.to_numeric(frame["MonthlyCharges"], errors="coerce")
    if "tenure" in frame.columns:
        frame["tenure"] = pd.to_numeric(frame["tenure"], errors="coerce")
    if ID_COLUMN in frame.columns:
        frame = frame.drop(columns=[ID_COLUMN])
    return frame


def _create_demo_dataset(n_rows: int = 5000) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_STATE)
    data = pd.DataFrame(
        {
            "customerID": [f"demo-{i:05d}" for i in range(n_rows)],
            "gender": rng.choice(["Male", "Female"], size=n_rows),
            "SeniorCitizen": rng.integers(0, 2, size=n_rows),
            "Partner": rng.choice(["Yes", "No"], size=n_rows),
            "Dependents": rng.choice(["Yes", "No"], size=n_rows),
            "tenure": rng.integers(0, 73, size=n_rows),
            "PhoneService": rng.choice(["Yes", "No"], size=n_rows, p=[0.9, 0.1]),
            "InternetService": rng.choice(["DSL", "Fiber optic", "No"], size=n_rows, p=[0.35, 0.45, 0.20]),
            "OnlineSecurity": rng.choice(["Yes", "No", "No internet service"], size=n_rows),
            "TechSupport": rng.choice(["Yes", "No", "No internet service"], size=n_rows),
            "StreamingTV": rng.choice(["Yes", "No", "No internet service"], size=n_rows),
            "Contract": rng.choice(["Month-to-month", "One year", "Two year"], size=n_rows, p=[0.6, 0.2, 0.2]),
            "PaymentMethod": rng.choice(["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"], size=n_rows),
            "MonthlyCharges": np.round(rng.uniform(20, 120, size=n_rows), 2),
        }
    )
    service_multiplier = np.where(data["InternetService"] == "Fiber optic", 1.25, np.where(data["InternetService"] == "DSL", 1.05, 0.8))
    data["TotalCharges"] = np.round(data["MonthlyCharges"] * data["tenure"] * service_multiplier + rng.normal(0, 50, size=n_rows).clip(-100, 100), 2)
    base_risk = (
        0.95 * (data["Contract"] == "Month-to-month").astype(float)
        + 0.65 * (data["PaymentMethod"] == "Electronic check").astype(float)
        + 0.55 * (data["InternetService"] == "Fiber optic").astype(float)
        + 0.5 * (data["MonthlyCharges"] > 80).astype(float)
        + 0.75 * (data["tenure"] < 12).astype(float)
        + 0.4 * (data["SeniorCitizen"] == 1).astype(float)
        - 0.55 * (data["Partner"] == "Yes").astype(float)
        - 0.45 * (data["Dependents"] == "Yes").astype(float)
        - 0.4 * (data["Contract"] == "Two year").astype(float)
    )
    prob = 1 / (1 + np.exp(-(base_risk - 1.2)))
    data[TARGET_COLUMN] = np.where(rng.random(n_rows) < prob, "Yes", "No")
    return data


def load_training_data() -> pd.DataFrame:
    try:
        return load_raw_data()
    except FileNotFoundError:
        return _create_demo_dataset()


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_features = X.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = [column for column in X.columns if column not in numeric_features]

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )


def evaluate_model(model_name: str, pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="X does not have valid feature names*")
        probabilities = pipeline.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    return {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
    }


def train_and_select_best_model() -> TrainingResult:
    df = _prepare_frame(load_training_data())
    y = df[TARGET_COLUMN].astype(int)
    X = df.drop(columns=[TARGET_COLUMN])

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    preprocessor = build_preprocessor(X_train)
    models = {
        "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, class_weight="balanced_subsample"),
        "LightGBM": LGBMClassifier(
            n_estimators=500,
            learning_rate=0.03,
            num_leaves=31,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=RANDOM_STATE,
        ),
    }

    metrics: Dict[str, Dict[str, float]] = {}
    fitted_pipelines: Dict[str, Pipeline] = {}
    best_model_name = ""
    best_score = -1.0

    for name, estimator in models.items():
        pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", estimator)])
        pipeline.fit(X_train, y_train)
        metrics[name] = evaluate_model(name, pipeline, X_test, y_test)
        fitted_pipelines[name] = pipeline
        if metrics[name]["roc_auc"] > best_score:
            best_score = metrics[name]["roc_auc"]
            best_model_name = name

    best_pipeline = fitted_pipelines[best_model_name]
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, MODEL_PATH)
    joblib.dump(best_pipeline.named_steps["preprocessor"], PREPROCESSOR_PATH)
    with METRICS_PATH.open("w", encoding="utf-8") as handle:
        json.dump({"best_model": best_model_name, "metrics": metrics}, handle, indent=2)

    feature_columns = X.columns.tolist()
    return TrainingResult(best_model_name=best_model_name, metrics=metrics, feature_columns=feature_columns)


def load_model_artifact():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    train_and_select_best_model()
    return joblib.load(MODEL_PATH)


def get_feature_names(preprocessor: ColumnTransformer) -> List[str]:
    output_names: List[str] = []
    for name, transformer, columns in preprocessor.transformers_:
        if name == "num":
            output_names.extend(columns)
        elif name == "cat":
            encoder = transformer.named_steps["encoder"]
            output_names.extend(list(encoder.get_feature_names_out(columns)))
    return output_names

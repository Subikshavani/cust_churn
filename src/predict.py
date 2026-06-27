from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from .config import MODEL_PATH, TARGET_COLUMN
from .modeling import _prepare_frame, get_feature_names, load_model_artifact, train_and_select_best_model


@dataclass
class PredictionResult:
    churn_prediction: str
    churn_probability: float
    risk_category: str
    reason_text: List[str]
    feature_importance: List[Tuple[str, float]]


def _risk_category(probability: float) -> str:
    if probability < 0.35:
        return "Low Risk"
    if probability < 0.65:
        return "Medium Risk"
    return "High Risk"


def _explanation_rules(payload: Dict[str, object]) -> List[str]:
    reasons: List[str] = []
    if payload.get("Contract") == "Month-to-month":
        reasons.append("Month-to-month Contract")
    if float(payload.get("MonthlyCharges", 0)) >= 80:
        reasons.append("High Monthly Charges")
    if float(payload.get("tenure", 0)) <= 12:
        reasons.append("Low Tenure")
    if payload.get("InternetService") == "Fiber optic":
        reasons.append("Fiber Optic Service Premium")
    if payload.get("PaymentMethod") == "Electronic check":
        reasons.append("Electronic Check Payment Method")
    if payload.get("OnlineSecurity") == "No":
        reasons.append("No Online Security")
    return reasons[:3] if reasons else ["Stable customer profile"]


def explain_prediction(payload: Dict[str, object]) -> PredictionResult:
    def _do_predict():
        model = load_model_artifact()
        frame = pd.DataFrame([payload])
        frame = _prepare_frame(frame)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="X does not have valid feature names*")
            probability = float(model.predict_proba(frame)[:, 1][0])
        prediction = "Yes" if probability >= 0.5 else "No"
        category = _risk_category(probability)

        preprocessor = model.named_steps["preprocessor"]
        feature_names = get_feature_names(preprocessor)
        estimator = model.named_steps["model"]
        importance_values = getattr(estimator, "feature_importances_", None)
        if importance_values is None and hasattr(estimator, "coef_"):
            importance_values = np.abs(estimator.coef_[0])
        if importance_values is None:
            feature_importance = [(name, 0.0) for name in feature_names[:10]]
        else:
            top_indices = np.argsort(np.abs(importance_values))[::-1][:10]
            feature_importance = [(feature_names[index], float(abs(importance_values[index]))) for index in top_indices]

        return PredictionResult(
            churn_prediction=prediction,
            churn_probability=probability,
            risk_category=category,
            reason_text=_explanation_rules(payload),
            feature_importance=feature_importance,
        )

    try:
        return _do_predict()
    except Exception:
        # If prediction fails due to incompatible model or feature mismatch on cloud, retrain and retry
        train_and_select_best_model()
        return _do_predict()

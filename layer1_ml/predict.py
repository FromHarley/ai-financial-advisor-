"""
Layer 1 · Runtime inference + SHAP explanation.

OWNER: Alex Harley
BRANCH: layer1-ml

This module is called by `app.py` at runtime. It exposes:

- predict_risk_tier(profile: dict) -> dict
- render_shap_plot(shap_values, profile) -> None  (draws to st.pyplot)
"""

from pathlib import Path

import joblib
import numpy as np
import shap
import matplotlib.pyplot as plt
import streamlit as st

MODEL_PATH = Path(__file__).parent / "model.pkl"

# Cache the loaded bundle so we don't re-read from disk on every Streamlit rerun
_bundle = None


def _load_bundle():
    global _bundle
    if _bundle is None:
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def predict_risk_tier(profile: dict) -> dict:
    """
    Predict risk tier for a single investor profile.

    Args:
        profile: dict with keys: age, annual_income_usd, savings_rate_pct,
                 debt_to_income_ratio, investment_horizon_years, investment_experience

    Returns:
        dict with keys: tier, confidence, shap_values, top_factors
    """
    bundle = _load_bundle()
    model = bundle["model"]
    feature_cols = bundle["feature_cols"]
    label_inv = bundle["label_inv"]
    exp_map = bundle["exp_map"]

    # Build 7-feature vector matching FEATURE_COLS order from training
    row = [
        profile["age"],
        max(0, 65 - profile["age"]),                       # years_to_retirement
        profile["annual_income_usd"],
        profile["savings_rate_pct"],
        profile["debt_to_income_ratio"],
        profile["investment_horizon_years"],
        exp_map[profile["investment_experience"]],
    ]

    X_single = np.array([row])

    # Predict
    pred_class = int(model.predict(X_single)[0])
    pred_proba = model.predict_proba(X_single)[0]
    tier = label_inv[pred_class]
    confidence = float(pred_proba[pred_class])

    # SHAP explanation
    explainer = shap.TreeExplainer(model)
    shap_exp = explainer(X_single)

    # Extract top 3 features by absolute SHAP value for the predicted class
    sv = shap_exp.values[0, :, pred_class]
    indexed = sorted(
        zip(feature_cols, sv),
        key=lambda x: abs(x[1]),
        reverse=True,
    )
    top_factors = [
        {
            "feature": feat,
            "impact": float(impact),
            "direction": "up" if impact > 0 else "down",
        }
        for feat, impact in indexed[:3]
    ]

    return {
        "tier": tier,
        "confidence": confidence,
        "shap_values": shap_exp,
        "top_factors": top_factors,
    }


def render_shap_plot(shap_values, profile: dict) -> None:
    """
    Draw a SHAP waterfall plot into the Streamlit UI.

    Args:
        shap_values: The SHAP Explanation object from predict_risk_tier.
        profile: The original profile dict (for context).
    """
    bundle = _load_bundle()
    label_inv = bundle["label_inv"]

    # Determine which class was predicted
    model = bundle["model"]
    exp_map = bundle["exp_map"]
    row = [
        profile["age"],
        max(0, 65 - profile["age"]),
        profile["annual_income_usd"],
        profile["savings_rate_pct"],
        profile["debt_to_income_ratio"],
        profile["investment_horizon_years"],
        exp_map[profile["investment_experience"]],
    ]
    X_single = np.array([row])
    pred_class = int(model.predict(X_single)[0])

    fig, ax = plt.subplots(figsize=(8, 5))
    try:
        shap.plots.waterfall(shap_values[0, :, pred_class], max_display=7, show=False)
    except Exception:
        # Fallback for older SHAP versions
        feature_cols = bundle["feature_cols"]
        shap.plots.waterfall(
            shap.Explanation(
                values=shap_values.values[0, :, pred_class],
                base_values=shap_values.base_values[0, pred_class],
                data=X_single[0],
                feature_names=feature_cols,
            ),
            max_display=7,
            show=False,
        )

    st.pyplot(plt.gcf())
    plt.close("all")

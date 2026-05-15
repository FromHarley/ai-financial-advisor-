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

# Human-readable feature names for SHAP plots and UI display.
# Keys must match FEATURE_COLS in train.py exactly.
FEATURE_DISPLAY_NAMES = {
    "age": "Age",
    "years_to_retirement": "Years to Retirement",
    "annual_income_usd": "Annual Income",
    "savings_rate_pct": "Savings Rate",
    "debt_to_income_ratio": "Debt-to-Income Ratio",
    "investment_horizon_years": "Investment Horizon",
    "experience_encoded": "Experience Level",
}

# Detailed explanations for each feature: what it is, how it's scored,
# and how it influences the risk tier and ETF selection.
FEATURE_EXPLANATIONS = {
    "age": {
        "what": "Your current age in years.",
        "scoring": "Entered directly. Used alongside a retirement assumption of age 65 to derive years-to-retirement.",
        "influence": "Younger investors have longer time horizons, which the model associates with higher risk tolerance. Older investors trend toward lower-risk, income-focused portfolios.",
    },
    "years_to_retirement": {
        "what": "Estimated years until retirement (65 minus your age, floored at 0).",
        "scoring": "Engineered feature — calculated automatically from your age. Not entered directly.",
        "influence": "The single strongest predictor. More years to retirement means more time to recover from market downturns, pushing the model toward higher-risk tiers with growth-oriented ETFs.",
    },
    "annual_income_usd": {
        "what": "Your gross annual income in US dollars.",
        "scoring": "Entered directly as a dollar amount.",
        "influence": "Higher income signals greater capacity to absorb losses. The model tilts toward riskier tiers for higher earners. In ETF selection, higher income also unlocks more diversified picks like sector tilts and emerging markets.",
    },
    "savings_rate_pct": {
        "what": "The percentage of your income you save each year.",
        "scoring": "Entered as a percentage (0–50%). Higher rates indicate stronger financial discipline.",
        "influence": "A high savings rate suggests a financial cushion, nudging the model toward medium or high risk. Low savers tend to get conservative, capital-preservation portfolios.",
    },
    "debt_to_income_ratio": {
        "what": "Your total monthly debt payments divided by your monthly income.",
        "scoring": "Entered as a decimal (0.0–1.0). A ratio of 0.3 means 30% of income goes to debt.",
        "influence": "High debt-to-income ratios push the model toward lower-risk tiers — more debt means less room for volatile investments. Low ratios free up risk capacity.",
    },
    "investment_horizon_years": {
        "what": "How many years you plan to stay invested before withdrawing.",
        "scoring": "Entered directly in years (1–50).",
        "influence": "Longer horizons strongly push toward higher-risk tiers. A 30-year horizon favors growth ETFs (QQQ, small-caps) while a 5-year horizon favors bonds and short-duration funds.",
    },
    "experience_encoded": {
        "what": "Your self-reported investing experience level.",
        "scoring": "Beginner = 0, Intermediate = 1, Advanced = 2. Encoded numerically for the model.",
        "influence": "Advanced investors are more likely to receive higher-risk tiers and get access to thematic/sector ETFs (semiconductors, biotech, clean energy). Beginners get simpler, broad-market picks.",
    },
}

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
            "display_name": FEATURE_DISPLAY_NAMES.get(feat, feat),
            "impact": float(impact),
            "direction": "up" if impact > 0 else "down",
            "explanation": FEATURE_EXPLANATIONS.get(feat, {}),
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

    feature_cols = bundle["feature_cols"]
    display_names = [FEATURE_DISPLAY_NAMES.get(f, f) for f in feature_cols]

    # Build a clean SHAP Explanation with human-readable feature names
    explanation_obj = shap.Explanation(
        values=shap_values.values[0, :, pred_class],
        base_values=shap_values.base_values[0, pred_class],
        data=X_single[0],
        feature_names=display_names,
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    shap.plots.waterfall(explanation_obj, max_display=7, show=False)
    st.pyplot(plt.gcf())
    plt.close("all")

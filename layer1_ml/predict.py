"""
Layer 1 · Runtime inference + SHAP explanation.

OWNER: [TBD at kickoff]
BRANCH: layer1-ml

This module is called by `app.py` at runtime. It must expose:

- predict_risk_tier(profile: dict) -> dict
- render_shap_plot(shap_values, profile) -> None  (draws to st.pyplot)

The contract is in §6 of the blueprint. Do NOT change the signatures
without discussing at a meeting.

What you need to do:

1. Load the trained model from `model.pkl` (use joblib or pickle).
2. In predict_risk_tier(), encode the incoming profile the same way you
   encoded training data, call model.predict() + model.predict_proba(),
   and run the SHAP explainer on the single row.
3. Return a dict matching the contract below.
4. In render_shap_plot(), draw the SHAP waterfall plot into the Streamlit
   UI using st.pyplot(fig).

Stub behavior: returns a fake "Medium" tier so the app runs end-to-end
before real implementation. Replace this with the real pipeline.
"""

from pathlib import Path

# TODO: import joblib
# TODO: import shap
# TODO: import matplotlib.pyplot as plt
# TODO: import streamlit as st

MODEL_PATH = Path(__file__).parent / "model.pkl"


def predict_risk_tier(profile: dict) -> dict:
    """
    Predict risk tier for a single investor profile.

    Args:
        profile: dict with keys:
            - age (int)
            - annual_income_usd (int)
            - savings_rate_pct (float)
            - debt_to_income_ratio (float)
            - investment_horizon_years (int)
            - investment_experience (str: 'Beginner' | 'Intermediate' | 'Advanced')

    Returns:
        dict with keys:
            - tier (str: 'Low' | 'Medium' | 'High')
            - confidence (float, 0.0-1.0)
            - shap_values (object — SHAP explanation for render_shap_plot)
            - top_factors (list of dicts: [{"feature": str, "impact": float, "direction": str}])
    """
    # TODO: load model from MODEL_PATH if not already loaded (cache it)
    # TODO: build feature vector from profile in the same order as FEATURE_COLS in train.py
    # TODO: model.predict() and model.predict_proba()
    # TODO: shap.TreeExplainer(model).shap_values(X_single)
    # TODO: extract top 3 features by absolute SHAP value
    # TODO: return the structured dict

    # --- STUB RESPONSE so the app runs end-to-end before real implementation ---
    return {
        "tier": "Medium",
        "confidence": 0.73,
        "shap_values": None,
        "top_factors": [
            {"feature": "investment_horizon_years", "impact": 0.12, "direction": "up"},
            {"feature": "debt_to_income_ratio", "impact": -0.08, "direction": "down"},
            {"feature": "age", "impact": 0.05, "direction": "up"},
        ],
    }


def render_shap_plot(shap_values, profile: dict) -> None:
    """
    Draw a SHAP waterfall (or force) plot into the Streamlit UI.

    Args:
        shap_values: The SHAP values object returned from predict_risk_tier.
        profile: The original profile dict (for feature labels).

    Returns:
        None — this renders directly to Streamlit with st.pyplot().
    """
    # TODO: fig, ax = plt.subplots()
    # TODO: shap.plots.waterfall(shap_values, show=False)
    # TODO: st.pyplot(fig)

    import streamlit as st
    st.caption("⚠️ SHAP plot renderer not yet implemented. Assigned to: [TBD]")

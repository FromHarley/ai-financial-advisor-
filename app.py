"""
AI Financial Advisor — Streamlit entry point.

This file is the integration point. Each AI layer lives in its own module
and exposes a single public function with an agreed signature (see §6 of
the blueprint). When all the layers are implemented, the flow here should
just work end-to-end.

DO NOT put layer-specific logic in this file. If you find yourself writing
SHAP code or Claude prompts here, stop and put it in the right module.
"""

import os
from dotenv import load_dotenv
import streamlit as st

# Layer imports — each module exposes its public function
from layer1_ml.predict import predict_risk_tier
from layer2_genai.claude_client import generate_explanation
from layer3_agentic.etf_agent import get_etf_recommendations
from layer4_respai.decision_log import log_decision
from voice_ux.transcribe import transcribe_profile
from voice_ux.speak import speak_button

# Load environment variables from .env
load_dotenv()


# ---------- Page config ----------
st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="💼",
    layout="wide",
)


# ---------- Sidebar ----------
with st.sidebar:
    st.title("💼 AI Financial Advisor")
    st.caption("Team Group 2 · MIS 02.303 · Spring 2026")
    st.divider()

    input_mode = st.radio(
        "Input mode",
        ["🎤 Voice", "⌨️ Keyboard"],
        help="Voice is our stretch feature. Keyboard is the fallback — always works.",
    )

    st.divider()
    st.caption("**API keys loaded:**")
    st.caption(f"• Anthropic: {'✅' if os.getenv('ANTHROPIC_API_KEY') else '❌'}")
    st.caption(f"• OpenAI: {'✅' if os.getenv('OPENAI_API_KEY') else '❌ (voice disabled)'}")


# ---------- Session state init ----------
# Streamlit re-runs the whole script on every interaction, so we keep
# state in st.session_state to avoid losing progress.
if "profile" not in st.session_state:
    st.session_state.profile = None
if "tier_result" not in st.session_state:
    st.session_state.tier_result = None
if "etfs" not in st.session_state:
    st.session_state.etfs = None
if "explanation" not in st.session_state:
    st.session_state.explanation = None
if "decision" not in st.session_state:
    st.session_state.decision = None


# ---------- Main layout ----------
st.title("Autonomous Financial Advisor")
st.markdown(
    "Tell us about yourself and we'll recommend an ETF portfolio that matches "
    "your risk profile. You stay in control — nothing is finalized until you approve."
)


# ---------- Step 1: Profile input ----------
st.header("Step 1 · Tell us about you")

if input_mode == "🎤 Voice":
    st.info(
        "Click the microphone and describe yourself: your age, income, how much "
        "you save, whether you have debt, how long you want to invest for, and "
        "your experience level."
    )
    profile = transcribe_profile()  # Voice layer — returns dict or None
else:
    # Keyboard fallback form
    with st.form("keyboard_profile"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=18, max_value=100, value=30)
            income = st.number_input(
                "Annual income (USD)", min_value=0, value=60000, step=1000
            )
            savings = st.slider(
                "Savings rate (% of income)", min_value=0.0, max_value=50.0, value=10.0
            )
        with col2:
            dti = st.slider(
                "Debt-to-income ratio",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.05,
                help="Total monthly debt payments divided by monthly income.",
            )
            horizon = st.number_input(
                "Investment horizon (years)", min_value=1, max_value=50, value=20
            )
            experience = st.selectbox(
                "Investment experience",
                ["Beginner", "Intermediate", "Advanced"],
            )

        submitted = st.form_submit_button("Analyze my profile", type="primary")
        if submitted:
            st.session_state.profile = {
                "age": age,
                "annual_income_usd": income,
                "savings_rate_pct": savings,
                "debt_to_income_ratio": dti,
                "investment_horizon_years": horizon,
                "investment_experience": experience,
            }
            # Clear downstream state so we re-run the pipeline
            st.session_state.tier_result = None
            st.session_state.etfs = None
            st.session_state.explanation = None
            st.session_state.decision = None

    if input_mode == "🎤 Voice" and profile:
        st.session_state.profile = profile


# ---------- Step 2: Run the pipeline ----------
if st.session_state.profile and st.session_state.tier_result is None:
    with st.spinner("Analyzing your profile..."):
        # Layer 1: ML + SHAP
        st.session_state.tier_result = predict_risk_tier(st.session_state.profile)

    with st.spinner("Finding ETFs that match your tier..."):
        # Layer 3: Agentic
        st.session_state.etfs = get_etf_recommendations(
            st.session_state.tier_result["tier"]
        )

    with st.spinner("Writing your personalized explanation..."):
        # Layer 2: Claude
        st.session_state.explanation = generate_explanation(
            profile=st.session_state.profile,
            tier=st.session_state.tier_result["tier"],
            top_factors=st.session_state.tier_result.get("top_factors", []),
            etfs=st.session_state.etfs,
        )


# ---------- Step 3: Results display ----------
if st.session_state.tier_result:
    st.header("Step 2 · Your risk tier")

    tier = st.session_state.tier_result["tier"]
    confidence = st.session_state.tier_result.get("confidence", None)

    # Big tier display
    tier_colors = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
    st.markdown(f"### {tier_colors.get(tier, '⚪')} **{tier} risk**")
    if confidence is not None:
        st.caption(f"Model confidence: {confidence:.1%}")

    # SHAP explanation
    with st.expander("Why did the model predict this tier?", expanded=True):
        st.markdown(
            "The chart below shows which features pushed your prediction up or down. "
            "This is our explainability layer — we show the math, not just the answer."
        )
        # Layer 1 is responsible for rendering the SHAP plot inside this expander.
        # It should use st.pyplot() on a matplotlib figure or st.image() on a saved png.
        shap_values = st.session_state.tier_result.get("shap_values")
        if shap_values is not None:
            from layer1_ml.predict import render_shap_plot
            render_shap_plot(shap_values, st.session_state.profile)
        else:
            st.caption("⚠️ SHAP plot not available — Layer 1 stub not yet implemented.")


if st.session_state.etfs:
    st.header("Step 3 · Your ETF recommendations")

    # ETF cards
    cols = st.columns(len(st.session_state.etfs))
    for col, etf in zip(cols, st.session_state.etfs):
        with col:
            st.markdown(f"### {etf.get('ticker', '?')}")
            st.caption(etf.get("name", ""))
            price = etf.get("current_price")
            if price is not None:
                st.metric("Current price", f"${price:.2f}")
            st.caption(etf.get("rationale", ""))


if st.session_state.explanation:
    st.header("Step 4 · Plain-English explanation")
    st.info(st.session_state.explanation)

    # Voice layer speaks this back if voice mode is on
    if input_mode == "🎤 Voice":
        speak_button(st.session_state.explanation)


# ---------- Step 5: Human-in-the-loop approval ----------
if st.session_state.explanation and st.session_state.decision is None:
    st.header("Step 5 · Your decision")
    st.markdown(
        "**Nothing is logged until you approve.** This is the human-in-the-loop "
        "checkpoint — we never act on a recommendation without your explicit OK."
    )

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("✅ Accept", type="primary", use_container_width=True):
            log_decision(
                profile=st.session_state.profile,
                tier=st.session_state.tier_result["tier"],
                etfs=st.session_state.etfs,
                explanation=st.session_state.explanation,
                user_decision="accept",
            )
            st.session_state.decision = "accept"
            st.rerun()
    with col2:
        if st.button("❌ Reject", use_container_width=True):
            log_decision(
                profile=st.session_state.profile,
                tier=st.session_state.tier_result["tier"],
                etfs=st.session_state.etfs,
                explanation=st.session_state.explanation,
                user_decision="reject",
            )
            st.session_state.decision = "reject"
            st.rerun()


if st.session_state.decision == "accept":
    st.success("Recommendation accepted and logged. Thank you!")
elif st.session_state.decision == "reject":
    st.warning("Recommendation rejected and logged. Feel free to try again.")


# ---------- Responsible AI panel ----------
with st.expander("📋 Responsible AI — Model Card & Bias Audit"):
    st.markdown("**Model card:** see `layer4_respai/model_card.md` in the repo.")
    st.markdown("**Bias audit findings:**")
    # Layer 4 renders the bias chart + writeup here
    from layer4_respai.bias_audit import render_bias_audit_summary
    render_bias_audit_summary()


# ---------- Footer ----------
st.divider()
st.caption(
    "⚠️ This tool is a class project. It is **not financial advice.** "
    "It does not execute trades, hold funds, or produce legally binding recommendations."
)

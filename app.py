"""
AI Financial Advisor — Streamlit entry point.

This file is the integration point. Each AI layer lives in its own module
and exposes a single public function with an agreed signature.
"""

import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd

# Layer imports
from layer1_ml.predict import predict_risk_tier
from layer2_genai.claude_client import generate_explanation
from layer3_agentic.etf_agent import get_etf_recommendations
from layer4_respai.decision_log import log_decision

load_dotenv()


# ---------- Page config ----------
st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------- Custom CSS ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #dce8f5;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: #1b3a5c;
        border-right: 1px solid #2a5280;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e0e8f0 !important;
    }
    section[data-testid="stSidebar"] .stCaption p {
        color: #a0b8cc !important;
    }

    /* ---- All text dark for readability ---- */
    .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2,
    .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    .stMarkdown span, .stMarkdown div, .stMarkdown label {
        color: #1a2a3a !important;
    }

    /* ---- Hero ---- */
    .hero-section {
        background: linear-gradient(135deg, #1b3a5c 0%, #2a5280 100%);
        border-radius: 12px;
        padding: 40px 36px;
        margin-bottom: 28px;
        color: white;
        border: 1px solid #1b3a5c;
    }
    .hero-section * { color: white !important; }
    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 8px;
        letter-spacing: -0.3px;
    }
    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.85;
        line-height: 1.6;
        max-width: 640px;
    }

    /* ---- Step headers ---- */
    .step-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 18px;
        margin-top: 4px;
    }
    .step-number {
        background: #2a5280;
        color: white !important;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        flex-shrink: 0;
    }
    .step-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a2a3a !important;
    }

    /* ---- Section card ---- */
    .section-box {
        background: #ffffff;
        border: 1px solid #b0c4d8;
        border-radius: 10px;
        padding: 24px 28px;
        margin-bottom: 20px;
    }

    /* ---- Tier badge ---- */
    .tier-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 14px 24px;
        border-radius: 8px;
        font-size: 1.3rem;
        font-weight: 700;
    }
    .tier-low {
        background: #d4edda;
        color: #155724 !important;
        border: 1px solid #a3d5b1;
    }
    .tier-medium {
        background: #fff3cd;
        color: #856404 !important;
        border: 1px solid #ffc107;
    }
    .tier-high {
        background: #f8d7da;
        color: #721c24 !important;
        border: 1px solid #f5c6cb;
    }

    /* ---- ETF cards ---- */
    .etf-card {
        background: #ffffff;
        border: 1px solid #b0c4d8;
        border-top: 4px solid #2a5280;
        border-radius: 10px;
        padding: 24px 18px;
        text-align: center;
        transition: box-shadow 0.15s ease;
    }
    .etf-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    .etf-ticker {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a2a3a !important;
        margin-bottom: 2px;
    }
    .etf-name {
        font-size: 0.78rem;
        color: #556677 !important;
        margin-bottom: 14px;
        min-height: 2.4em;
        line-height: 1.4;
    }
    .etf-category {
        display: inline-block;
        background: #dce8f5;
        color: #1b3a5c !important;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 4px;
        margin-bottom: 14px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .etf-price {
        font-size: 1.7rem;
        font-weight: 700;
        color: #28a745 !important;
        margin-bottom: 2px;
    }
    .etf-price-label {
        font-size: 0.7rem;
        color: #888 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }
    .etf-rationale {
        font-size: 0.75rem;
        color: #667788 !important;
        margin-top: 10px;
        line-height: 1.4;
        font-style: italic;
    }

    /* ---- Explanation box ---- */
    .explanation-box {
        background: #ffffff;
        border-left: 4px solid #2a5280;
        border-radius: 0 10px 10px 0;
        padding: 22px 26px;
        font-size: 1rem;
        line-height: 1.7;
        color: #1a2a3a !important;
        border: 1px solid #b0c4d8;
        border-left: 4px solid #2a5280;
    }

    /* ---- Decision ---- */
    .decision-section {
        background: #ffffff;
        border: 2px solid #b0c4d8;
        border-radius: 10px;
        padding: 24px;
        text-align: center;
    }
    .decision-section p { color: #1a2a3a !important; }

    /* ---- Footer ---- */
    .app-footer {
        background: #1b3a5c;
        border-radius: 10px;
        padding: 20px 24px;
        text-align: center;
        font-size: 0.82rem;
        margin-top: 32px;
    }
    .app-footer, .app-footer * { color: #c0d0e0 !important; }
    .app-footer strong { color: #ffffff !important; }

    /* ---- Responsive ---- */
    @media (max-width: 768px) {
        .hero-section { padding: 28px 20px 24px; }
        .hero-title { font-size: 1.5rem; }
        .step-title { font-size: 1.05rem; }
        .section-box { padding: 18px 16px; }
        .etf-card { padding: 16px 12px; }
    }

    /* ---- Streamlit overrides ---- */
    /* Buttons */
    .stButton > button[kind="primary"] {
        background: #2a5280 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 1rem;
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #1b3a5c !important;
    }

    /* Sliders — override red to blue */
    .stSlider [data-testid="stThumbValue"] { color: #2a5280 !important; }
    div[data-baseweb="slider"] div[role="slider"] {
        background: #2a5280 !important;
        border-color: #2a5280 !important;
    }
    div[data-baseweb="slider"] div[data-testid="stTickBar"] > div {
        background: #2a5280 !important;
    }

    /* Form */
    div[data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #b0c4d8;
        border-radius: 10px;
        padding: 24px 28px;
    }

    /* Labels */
    .stNumberInput label, .stSlider label, .stSelectbox label {
        color: #1a2a3a !important;
        font-weight: 500 !important;
    }

    /* Expander */
    div[data-testid="stExpander"] {
        border: 1px solid #b0c4d8;
        border-radius: 10px;
        overflow: hidden;
        background: #ffffff;
    }
    div[data-testid="stExpander"] summary span {
        color: #1a2a3a !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### AI Financial Advisor")
    st.caption("Team Group 2 · MIS 02.303 · Spring 2026")
    st.divider()

    st.markdown("**API Status**")
    anthropic_ok = bool(os.getenv("ANTHROPIC_API_KEY"))
    openai_ok = bool(os.getenv("OPENAI_API_KEY"))
    st.markdown(f"Anthropic: {'✅ Connected' if anthropic_ok else '❌ Missing'}")
    st.markdown(f"OpenAI: {'✅ Connected' if openai_ok else '⚪ Optional'}")

    st.divider()
    st.markdown("**Team**")
    st.caption("Alex Harley · Daniel Duffy")
    st.caption("Anurag Luhar · Kimberly Ting")


# ---------- Session state ----------
for key in ["profile", "tier_result", "etfs", "explanation", "decision"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ---------- Hero ----------
st.markdown("""
<div class="hero-section">
    <div class="hero-title">Autonomous Financial Advisor</div>
    <div class="hero-subtitle">
        Tell us about yourself and we'll recommend an ETF portfolio that matches
        your risk profile. You stay in control — nothing is finalized until you approve.
    </div>
</div>
""", unsafe_allow_html=True)


# ---------- Step 1: Profile input ----------
st.markdown("""
<div class="step-header">
    <div class="step-number">1</div>
    <div class="step-title">Tell us about you</div>
</div>
""", unsafe_allow_html=True)

with st.form("keyboard_profile"):
    col1, col2 = st.columns(2, gap="large")
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

    submitted = st.form_submit_button("Analyze my profile", type="primary",
                                       use_container_width=True)
    if submitted:
        st.session_state.profile = {
            "age": age,
            "annual_income_usd": income,
            "savings_rate_pct": savings,
            "debt_to_income_ratio": dti,
            "investment_horizon_years": horizon,
            "investment_experience": experience,
        }
        st.session_state.tier_result = None
        st.session_state.etfs = None
        st.session_state.explanation = None
        st.session_state.decision = None


# ---------- Step 2: Run the pipeline ----------
if st.session_state.profile and st.session_state.tier_result is None:
    with st.spinner("Analyzing your profile..."):
        st.session_state.tier_result = predict_risk_tier(st.session_state.profile)

    with st.spinner("Finding ETFs that match your tier..."):
        st.session_state.etfs = get_etf_recommendations(
            st.session_state.tier_result["tier"]
        )

    with st.spinner("Writing your personalized explanation..."):
        st.session_state.explanation = generate_explanation(
            profile=st.session_state.profile,
            tier=st.session_state.tier_result["tier"],
            top_factors=st.session_state.tier_result.get("top_factors", []),
            etfs=st.session_state.etfs,
        )


# ---------- Step 3: Risk tier ----------
if st.session_state.tier_result:
    st.markdown("""
    <div class="step-header">
        <div class="step-number">2</div>
        <div class="step-title">Your risk tier</div>
    </div>
    """, unsafe_allow_html=True)

    tier = st.session_state.tier_result["tier"]
    confidence = st.session_state.tier_result.get("confidence", None)

    tier_class = {"Low": "tier-low", "Medium": "tier-medium", "High": "tier-high"}
    tier_icon = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}

    conf_text = f" · {confidence:.0%} confidence" if confidence is not None else ""
    st.markdown(f"""
    <div class="section-box">
        <div class="tier-badge {tier_class.get(tier, '')}">
            {tier_icon.get(tier, '⚪')} {tier} Risk{conf_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Why did the model predict this tier?", expanded=False):
        st.markdown(
            "The chart below shows which features pushed your prediction up or down. "
            "This is our explainability layer — we show the math, not just the answer."
        )
        shap_values = st.session_state.tier_result.get("shap_values")
        if shap_values is not None:
            from layer1_ml.predict import render_shap_plot
            render_shap_plot(shap_values, st.session_state.profile)
        else:
            st.caption("SHAP plot not available.")


# ---------- Step 4: ETF recommendations ----------
if st.session_state.etfs:
    st.markdown("""
    <div class="step-header">
        <div class="step-number">3</div>
        <div class="step-title">Your ETF recommendations</div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(st.session_state.etfs), gap="medium")
    for col, etf in zip(cols, st.session_state.etfs):
        with col:
            price = etf.get("current_price")
            price_str = f"${price:,.2f}" if price is not None else "—"
            category = etf.get("category", "")
            st.markdown(f"""
            <div class="etf-card">
                <div class="etf-ticker">{etf.get('ticker', '?')}</div>
                <div class="etf-name">{etf.get('name', '')}</div>
                <div class="etf-category">{category}</div>
                <div class="etf-price">{price_str}</div>
                <div class="etf-price-label">Current Price</div>
                <div class="etf-rationale">{etf.get('rationale', '')}</div>
            </div>
            """, unsafe_allow_html=True)


# ---------- Step 5: Explanation ----------
if st.session_state.explanation:
    st.markdown("""
    <div class="step-header">
        <div class="step-number">4</div>
        <div class="step-title">Plain-English explanation</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="explanation-box">
        {st.session_state.explanation}
    </div>
    """, unsafe_allow_html=True)


# ---------- Step 6: Human-in-the-loop ----------
if st.session_state.explanation and st.session_state.decision is None:
    st.markdown("""
    <div class="step-header">
        <div class="step-number">5</div>
        <div class="step-title">Your decision</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="decision-section">
        <p>
            <strong>Nothing is logged until you approve.</strong> This is the human-in-the-loop
            checkpoint — we never act on a recommendation without your explicit OK.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
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
with st.expander("Responsible AI — Model Card & Bias Audit"):

    # Model card summary — using native Streamlit so it actually renders
    st.markdown("### Model card summary")

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Overall accuracy", "81.0%")
    mc2.metric("Weighted F1", "81.2%")
    mc3.metric("Training samples", "2,000")

    st.markdown("#### Top SHAP features (global)")
    st.markdown(
        "Investment horizon and age are the strongest predictors. "
        "See `model_card.md` for full details."
    )

    st.markdown("#### Bias audit findings")
    bias_df = pd.DataFrame({
        "Age group": ["Under 30", "30–54", "55–69"],
        "Accuracy": ["0.842", "0.810", "0.795"],
        "Gap vs overall": ["+ 0.032", "+ 0.000", "- 0.015"],
    })
    st.dataframe(bias_df, use_container_width=True, hide_index=True)
    st.caption("No group exceeded the ±0.05 disparity threshold.")

    st.markdown("#### LLM guardrails")
    st.markdown("""
- Only mentions ETF tickers provided in the input context
- No return figures cited
- Hedged language enforced via system prompt
- Disclaimer appended to every explanation
- Human approval required before any action
    """)

    st.divider()
    st.markdown("#### Bias audit — tier distribution by age band")
    from layer4_respai.bias_audit import render_bias_audit_summary
    render_bias_audit_summary()


# ---------- Footer ----------
st.markdown("""
<div class="app-footer">
    This tool is a class project. It is <strong>not financial advice.</strong>
    It does not execute trades, hold funds, or produce legally binding recommendations.
    <br><br>
    Built by Group 2 · MIS 02.303 · Rowan University · Spring 2026
</div>
""", unsafe_allow_html=True)

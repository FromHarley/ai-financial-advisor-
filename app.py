"""
AI Financial Advisor — Streamlit entry point.

This file is the integration point. Each AI layer lives in its own module
and exposes a single public function with an agreed signature.
"""

import os
from dotenv import load_dotenv
import streamlit as st

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
    /* ---- Global ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide default Streamlit header/footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid #334155;
    }

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li {
        color: #cbd5e1;
    }

    /* ---- Cards ---- */
    .advisor-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        transition: box-shadow 0.2s ease;
    }

    .advisor-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* ---- Hero header ---- */
    .hero-section {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
        border-radius: 20px;
        padding: 40px 36px;
        margin-bottom: 32px;
        color: white;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
        color: white;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        line-height: 1.6;
        max-width: 640px;
    }

    /* ---- Step headers ---- */
    .step-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        margin-top: 8px;
    }

    .step-number {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.95rem;
        flex-shrink: 0;
    }

    .step-title {
        font-size: 1.35rem;
        font-weight: 600;
        color: #0f172a;
    }

    /* ---- Risk tier badge ---- */
    .tier-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 16px 28px;
        border-radius: 14px;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .tier-low {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        color: #065f46;
    }

    .tier-medium {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        color: #92400e;
    }

    .tier-high {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        color: #991b1b;
    }

    /* ---- ETF cards ---- */
    .etf-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .etf-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }

    .etf-ticker {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
    }

    .etf-name {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 12px;
        min-height: 2.4em;
    }

    .etf-price {
        font-size: 1.6rem;
        font-weight: 700;
        color: #16a34a;
        margin-bottom: 4px;
    }

    .etf-rationale {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 8px;
        line-height: 1.4;
    }

    /* ---- Explanation box ---- */
    .explanation-box {
        background: linear-gradient(135deg, #eff6ff, #dbeafe);
        border: 1px solid #bfdbfe;
        border-radius: 14px;
        padding: 24px 28px;
        font-size: 1.05rem;
        line-height: 1.7;
        color: #1e3a5f;
    }

    /* ---- Decision buttons ---- */
    .decision-section {
        background: #f8fafc;
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        padding: 28px;
        text-align: center;
    }

    /* ---- Footer ---- */
    .app-footer {
        background: #f1f5f9;
        border-radius: 12px;
        padding: 16px 24px;
        text-align: center;
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 40px;
    }

    /* ---- Responsive ---- */
    @media (max-width: 768px) {
        .hero-section {
            padding: 28px 20px;
        }

        .hero-title {
            font-size: 1.6rem;
        }

        .hero-subtitle {
            font-size: 0.95rem;
        }

        .step-title {
            font-size: 1.1rem;
        }

        .advisor-card {
            padding: 16px;
        }

        .etf-card {
            padding: 14px;
        }
    }

    /* ---- Streamlit overrides ---- */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        border: none;
        border-radius: 10px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 1rem;
        transition: transform 0.1s ease;
    }

    .stButton > button[kind="primary"]:hover {
        transform: scale(1.02);
    }

    .stButton > button[kind="primary"]:active {
        transform: scale(0.98);
    }

    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        overflow: hidden;
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
    <div class="tier-badge {tier_class.get(tier, '')}">
        {tier_icon.get(tier, '⚪')} {tier} Risk{conf_text}
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
            st.markdown(f"""
            <div class="etf-card">
                <div class="etf-ticker">{etf.get('ticker', '?')}</div>
                <div class="etf-name">{etf.get('name', '')}</div>
                <div class="etf-price">{price_str}</div>
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
        <p style="color: #475569; font-size: 0.95rem; margin-bottom: 4px;">
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
    st.markdown("**Model card:** see `layer4_respai/model_card.md` in the repo.")
    st.markdown("**Bias audit findings:**")
    from layer4_respai.bias_audit import render_bias_audit_summary
    render_bias_audit_summary()


# ---------- Footer ----------
st.markdown("""
<div class="app-footer">
    This tool is a class project. It is <strong>not financial advice.</strong>
    It does not execute trades, hold funds, or produce legally binding recommendations.
    <br>
    <span style="color: #94a3b8;">Built by Group 2 · MIS 02.303 · Rowan University · Spring 2026</span>
</div>
""", unsafe_allow_html=True)

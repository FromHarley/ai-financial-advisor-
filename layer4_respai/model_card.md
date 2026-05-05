# Model Card — AI Financial Advisor

**Team:** Group 2 (Harley, Duffy, Luhar, Ting)
**Course:** MIS 02.303 — AI in Business, Spring 2026
**Date:** May 5, 2026
**Version:** 1.0

---

## 1. Intended use

This system is a class project designed to demonstrate an end-to-end AI application combining machine learning, generative AI, agentic AI, and responsible AI practices. It is **not** a production financial advisor and should not be used to make real investment decisions.

**Intended users:** The instructor, classmates, and potential employers evaluating the team's work.

**Intended use cases:**
- Educational demonstration of multi-layer AI systems
- Portfolio artifact for team members' future job applications

**Out-of-scope uses:**
- Any real financial advice
- Automated trading
- Recommendations for real money decisions
- Use by minors or anyone relying on it for material financial choices

---

## 2. Model details

**Layer 1 — Risk Tier Classifier**
- Architecture: XGBClassifier (XGBoost)
- Training data: `financial_risk_profiles.csv` (2,000 labeled investor profiles)
- Features: age, annual income, savings rate, debt-to-income ratio, investment horizon, investment experience
- Target: risk_tier ∈ {Low, Medium, High}
- Explainability: SHAP (TreeExplainer) applied to each prediction at runtime

**Layer 2 — Language Model**
- Provider: Anthropic
- Model: Claude Opus 4.7
- Usage: Generates 2–3 sentence plain-English explanation of each recommendation
- Rationale for choice: Claude produces warmer, clearer natural language than alternatives we tested for user-facing financial prose. The assignment explicitly leaves LLM choice to the team.

**Layer 3 — Agentic Component**
- Not a trained model — deterministic rule-based agent
- Data source: yfinance (live ETF prices)
- Fallback: cached last-known-good prices on fetch failure

---

## 3. Performance metrics

- Overall accuracy: 81.0%
- Model: XGBoost (n_estimators=300, max_depth=5, learning_rate=0.05)
- Class imbalance: handled via compute_class_weight balanced (from y_train)
- Features (7): age, years_to_retirement, annual_income_usd, savings_rate_pct, debt_to_income_ratio, investment_horizon_years, experience_encoded
- Training set size: 1,600 (80% split)
- Test set size: 400 (20% split)
- Per-class F1: Low 0.65, Medium 0.86, High 0.75

---

## 4. Known limitations

- **Training data is synthetic or semi-synthetic.** The dataset's provenance means the model's predictions reflect the patterns in this specific dataset, which may not generalize to real investors.
- **Features do not include demographic information.** The model cannot directly detect disparate impact across gender, race, or education because those columns are absent from training.
- **Claude outputs are not deterministic.** The same input can produce different explanations. We mitigate this with tight prompting and hedged language.
- **yfinance is a third-party data source.** Prices may be stale, delayed, or unavailable. The agent falls back to cached data in that case.
- **No backtesting.** We do not claim the recommended ETFs would have produced any specific historical return.

---

## 5. Bias audit

*To be filled in by the Layer 4 owner after running the audit.*

**Method:** Because our training data lacks direct demographic fields, we audit using an age-band proxy. We bin training ages into the CFPB's standard buckets (under 30, 30–54, 55–69, 70+) and compare the distribution of predicted tiers across buckets.

**Findings:** Younger profiles are assigned higher-risk tiers more frequently (Under 30: 53.9% High, 0.3% Low), while older profiles skew toward lower-risk tiers (55–69: 26.2% Low, 3.9% High). The 30–54 band is predominantly Medium (66.8%). The 70+ band has zero profiles in the dataset — a real gap, not a model output. The model is reproducing the age-horizon relationship present in the source labels, not inventing a pattern.

**Honest caveat:** This is a proxy, not a true demographic fairness test. We cannot directly measure disparate impact across gender, race, or education with the data we have. A production system handling real investor money would need richer demographic data and a full fairness-audit framework.

---

## 6. Human oversight

Every recommendation requires explicit user approval before it is logged. The user sees:
1. Their predicted risk tier with confidence score
2. The SHAP plot showing which features drove the prediction
3. The recommended ETFs with current prices
4. The Claude-generated plain-English explanation

The user must click **Accept** or **Reject** (or speak "accept"/"reject" in voice mode) before any decision is written to the log file `decisions.csv`. There is no autonomous action at any point.

---

## 7. Ethical considerations

- **Not financial advice.** Every output displayed to the user includes a disclaimer, and Claude's system prompt enforces the disclaimer on every response.
- **No real money handled.** The system only produces recommendations; it cannot execute trades.
- **Guardrails against hallucinated tickers.** Claude's prompt explicitly restricts it to the ETF list it was given. A post-check flags any ticker in the output that wasn't in the input list.
- **Privacy.** User profile data entered via voice is transcribed via OpenAI Whisper and the transcript is not stored beyond the session. Decision logs contain profile data and are stored locally only.

---

## 8. Contact

For questions about this model card: Alexander Harley (Project Lead), Rowan University.

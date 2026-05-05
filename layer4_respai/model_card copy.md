# `model_card.md` — Reference for Claude Code

## What this file is

`model_card.md` is the **public-facing accountability document** for the AI Financial Advisor. A model card is the standard fairness/transparency artifact for any deployed ML system — it tells anyone (a user, a grader, an auditor, a future developer) what the system is, what it isn't, what it can do, what it can't do, what it knows, what it doesn't know, and what limits and ethics it operates under.

If someone is going to evaluate the project's responsible AI work but only has time to read one document, this is it. The model card is the single source of truth that summarizes everything Layer 4 produces.

## Where it lives

`layer4_respai/model_card.md`

## What it contains (8 sections)

### 1. Intended use
Defines who the system is for and who it is **not** for. Names the team, the course, the date. States plainly that this is a class project and not a real financial advisor. Explicitly lists out-of-scope uses: real financial advice, automated trading, recommendations for real money decisions, use by minors.

### 2. Model details
Documents every layer of the system that involves a model:

- **Layer 1 (Risk Tier Classifier):** Random Forest, scikit-learn 1.5.2, hyperparameters (`n_estimators=200, max_depth=10, class_weight="balanced", random_state=42`), training data, features, target, encoding, explainability method (SHAP TreeExplainer).
- **Layer 2 (Language Model):** Anthropic Claude Sonnet 4.5, model id `claude-sonnet-4-5-20250929`, configurable via env var, rationale for choosing it.
- **Layer 3 (Agent):** Documented as deterministic rule-based, not a trained model. Lists the data source (yfinance) and the cache fallback.

### 3. Performance metrics
Real numbers from the held-out test split:

- Training set: 1,600 profiles
- Test set: 400 profiles
- Overall accuracy: **81.0%**
- Per-class precision/recall/F1 table
- Full confusion matrix
- A short paragraph reading the matrix — calling out the dangerous error mode (Low ↔ High confusion) doesn't happen, and that Low recall is the weakest class

### 4. Known limitations
Eight named limitations:

1. Synthetic/semi-synthetic training data
2. No demographic features in the data
3. No 70+ profiles in the dataset
4. Class imbalance (Medium dominates at 64%)
5. Non-deterministic Claude outputs
6. Third-party data risks (yfinance availability)
7. No backtesting — we make no claims about historical returns
8. Each is acknowledged plainly, not minimized

### 5. Bias audit
Summarizes the audit run by `bias_audit.py`. Includes:
- The method (CFPB age-band proxy)
- Sample sizes by band
- Tier distribution by band as a markdown table
- The observed pattern (younger → higher risk, older → lower risk)
- An honest caveat that age is a proxy, not a true protected-class fairness test

### 6. Human oversight
Describes the Accept/Reject gate built into the app. Explains that no decision is logged until the user explicitly clicks. States that Layer 3's "agent" only recommends — it never places trades or moves money.

### 7. Ethical considerations
Lists five ethical guardrails:

- The "not financial advice" disclaimer, enforced both in Claude's system prompt and as a runtime check
- No real money is handled
- A hallucinated-ticker safety check — Claude is restricted to the ETF list it was given, with a code-level check that flags any unknown ticker
- Hedged language requirements ("may suggest" rather than "will return")
- Privacy notes about session-only data and local-only decision logs

### 8. Contact
Team identification.

## Why this design

A model card is a recognized format in the ML community (originating from a 2018 Google paper by Mitchell et al.). Following this format gives the project a defensible answer to *"how do you know your AI isn't doing harm?"* and signals that the team understands the standard practice rather than inventing an ad-hoc accountability document.

The model card pulls together outputs from across the project:

- Section 3 (Performance metrics) → from `layer1_ml/metrics.txt`
- Section 5 (Bias audit) → from `bias_audit_findings.txt` and `bias_audit_chart.png`
- Sections 6 and 7 → reference behaviors built into `decision_log.py`, `claude_client.py`, and the app

So if any of those sources change, the model card needs to be updated to match. There's no automated link between them — it's the team's responsibility to keep them in sync.

## Where it gets read

- **Directly:** open the file in any text editor or Markdown viewer.
- **In the Streamlit app:** the model card is referenced from the "📋 Responsible AI — Model Card & Bias Audit" expandable section. Currently, the app shows the bias audit chart and findings; the full model card is meant to be read from the repo file directly.
- **In the presentation:** likely shown as a screenshot or referenced as the artifact that summarizes the team's responsible AI work.

## Maintenance — when to update

Update the model card when **any of the following change**:

- Layer 1 is re-trained (numbers in Section 3 will be stale)
- The bias audit is re-run (numbers in Section 5 will be stale)
- The Claude model id changes (Section 2)
- The training data is updated (Sections 2 and 4)
- Any of the safety guardrails in Layer 2 or Layer 4 are changed (Sections 6 and 7)

Right now the model card is in sync with: 81.0% test accuracy, the most recent bias audit numbers, Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`), and the current Accept/Reject gate.

## How to talk about this in the presentation

The model card is the artifact you point to when a grader asks any of these:

- *"What does your AI actually do?"* → Section 2 (Model details)
- *"How do you know it works?"* → Section 3 (Performance metrics)
- *"What are its weaknesses?"* → Section 4 (Known limitations)
- *"Did you check for bias?"* → Section 5 (Bias audit)
- *"What stops it from giving someone bad advice?"* → Sections 6 (Human oversight) and 7 (Ethical considerations)

One sentence summary for the slide: *"Our model card documents intended use, real test metrics, eight named limitations, the fairness audit, the human-in-the-loop gate, and our ethical guardrails — all in one document a grader can read end-to-end."*

## Owner

Per the project README, Layer 4 is owned by **Alex Harley** (Project Lead).

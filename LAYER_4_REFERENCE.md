# Layer 4 — Responsible AI · Reference for Claude Code

## What this layer is

Layer 4 is the **Responsible AI** layer of the AI Financial Advisor project (Group 2, Rowan University, MIS 02.303, Spring 2026). It's the layer that makes the system trustworthy — not by adding more AI, but by adding **oversight, transparency, and a fairness audit** around the AI that's already there.

The other three layers do the work: Layer 1 trains an ML model, Layer 2 calls Claude to write explanations, Layer 3 picks ETFs. Layer 4 holds them accountable. Without Layer 4, the project would just be "an AI app." With Layer 4, it's "an AI app you can defend in front of a class."

## What's in Layer 4

The folder `layer4_respai/` contains:

- **`decision_log.py`** — Code that logs every Accept or Reject decision the user makes, with a timestamp and full audit trail.
- **`bias_audit.py`** — Code that runs an offline fairness audit on the trained ML model and saves a chart + findings to disk.
- **`bias_audit_chart.png`** — The chart produced by the audit (predicted risk tier distribution by age band).
- **`bias_audit_findings.txt`** — Plain-language findings written when the audit was run.
- **`model_card.md`** — The full model card documenting intended use, performance, limitations, bias findings, ethical considerations, and human oversight design.
- **`__init__.py`** — Empty file that marks this as a Python package.

## What each piece does

### `decision_log.py` — Human-in-the-loop gate

This is the core of Responsible AI in this project. Every recommendation must pass through a human checkpoint before it gets logged. The user sees:

1. Their predicted risk tier with confidence
2. The SHAP chart showing which features drove the prediction
3. The recommended ETFs with current prices
4. Claude's plain-English explanation

Then they have to click **Accept** or **Reject**. Nothing gets written to the audit trail until they do.

The log file (`decisions.csv`) stores: timestamp, user decision (accept/reject), predicted tier, the full input profile as JSON, the recommended ETFs as JSON, and the explanation text. This proves three things on demand:

1. Every recommendation was shown to the user before any action was committed.
2. The user had a real choice (Accept vs. Reject).
3. We can trace any logged decision back to its exact inputs.

### `bias_audit.py` — Fairness audit (offline)

The course rubric requires a fairness audit. Our training data has no demographic columns (no gender, no race, no education) — only financial features. So we run an audit using an **age-band proxy**.

The script:

1. Loads the trained Random Forest model (from Layer 1).
2. Loads the full 2,000-row training dataset.
3. Bins every age into the CFPB's standard age bands (Under 30, 30–54, 55–69, 70+).
4. Runs the model across the entire dataset.
5. For each age band, computes the share of profiles predicted into each risk tier (Low / Medium / High).
6. Saves a stacked bar chart to `bias_audit_chart.png`.
7. Writes plain-language findings to `bias_audit_findings.txt`.

The audit runs **once, offline, before submission**. The Streamlit app does NOT re-run the audit on every page load — it just reads the chart and findings from disk. This is the right design because audits should be reproducible artifacts, not live-recomputed numbers that could change between runs.

### `model_card.md` — Public-facing accountability document

A model card is the standard fairness/transparency artifact for any deployed ML system. Ours has eight sections:

1. **Intended use** — What this is and isn't for. Class project. Not real financial advice.
2. **Model details** — Architecture (Random Forest), hyperparameters, training data, encoding, explainability method (SHAP).
3. **Performance metrics** — 81% test accuracy, per-class precision/recall/F1, confusion matrix.
4. **Known limitations** — Synthetic training data, missing demographic features, class imbalance, no 70+ profiles in dataset, non-deterministic LLM outputs, third-party data risks.
5. **Bias audit** — Method, sample sizes by band, tier distribution by band, findings, and an honest caveat that age is a proxy, not a true demographic test.
6. **Human oversight** — How the Accept/Reject gate works.
7. **Ethical considerations** — Disclaimers, no-real-money scope, hallucinated-ticker safety check, hedged language requirements, privacy.
8. **Contact** — Team identification.

## Why this design

The project's grading rubric weights "Responsible AI" heavily. The audit, the model card, and the human-in-the-loop gate are the three artifacts a grader will look for. Skipping any of them would lose points; building them well gives the project a defensible answer to *"how do you know your AI isn't doing harm?"*

The decision log specifically gives us a real answer to *"what stops this from giving someone bad financial advice?"* The answer: nothing gets recorded as a "decision" without the user's explicit click. The system is structurally incapable of acting autonomously — it can only recommend.

## Real numbers from the most recent audit run

These are the actual values that came out of running `python -m layer4_respai.bias_audit` on the trained model:

**Test set performance (n=400):**
- Overall accuracy: **81.0%**
- Per-class F1: Low 0.65, Medium 0.86, High 0.75
- The model never confuses Low with High — most errors are off-by-one to the adjacent tier.

**Bias audit — sample sizes by age band:**
- Under 30: 343 profiles
- 30–54: 1,093 profiles
- 55–69: 564 profiles
- 70+: 0 profiles (gap in the dataset, called out explicitly in findings)

**Bias audit — predicted tier distribution by band:**

| Age band | Low | Medium | High |
|---|---|---|---|
| Under 30 | 0.3% | 45.8% | 53.9% |
| 30–54 | 8.4% | 66.8% | 24.8% |
| 55–69 | 26.2% | 69.9% | 3.9% |
| 70+ | — | — | — |

**The pattern:** Younger profiles get assigned higher-risk tiers. Older profiles get assigned lower-risk tiers. This is consistent with the relationship between age and investment-horizon-based risk in the source labels — the model is **reproducing** the labeling pattern, not inventing one. Whether that's "bias" depends on whether the original labels are themselves fair, which is a question we can't fully answer for a synthetic teaching dataset. Honesty about that limitation is part of the audit.

## How to talk about Layer 4 in the presentation

One sentence summary: **"We ship a model card with real metrics and a bias audit using age-band as a fairness proxy, plus a hard human-in-the-loop gate — nothing is logged until the user clicks Accept or Reject."**

Three-sentence version:

1. We use SHAP and a model card to make the ML system's reasoning legible to users and to a future auditor.
2. We ran a fairness audit using age-band as a demographic proxy and documented honestly that this is a proxy, not a true protected-class test, because our training data lacks those columns.
3. We built a human-in-the-loop gate so no recommendation gets recorded as a "decision" without the user's explicit Accept or Reject click — the system is structurally incapable of acting autonomously.

## What still needs to happen

For a fully complete Layer 4 submission:

- Confirm the bias audit chart and findings files exist in the folder (run `python -m layer4_respai.bias_audit` if not).
- Verify the model card numbers match the most recent training run.
- Make sure the decision log file gets created when the app is used — it should appear at `layer4_respai/decisions.csv` after the first Accept or Reject click.
- During the presentation, demo at least one Accept and one Reject to show the gate works in both directions.

## Owner

Per the project README, Layer 4 is owned by **Alex Harley** (Project Lead). There was an earlier inconsistency between README and START_HERE on this — confirm with the team which assignment is final before submission.

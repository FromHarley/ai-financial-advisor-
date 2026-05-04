# `bias_audit.py` — Reference for Claude Code

## What this file is

`bias_audit.py` is the script that runs the **fairness audit** required by the course rubric. It checks whether the trained ML model (from Layer 1) treats different groups of people differently — and if it does, it documents that pattern honestly so anyone reading the project can see what the model is doing across populations.

Because our training data lacks direct demographic columns (no gender, no race, no education), the audit uses an **age-band proxy**. It bins all 2,000 training-set ages into the four CFPB-standard age bands and compares how the trained model assigns risk tiers across those bands. This isn't a perfect fairness test, and the script's findings call that out explicitly — but it's the most honest fairness signal we can extract from the data we have.

## Where it lives

`layer4_respai/bias_audit.py`

## What it does

The script has two public functions:

1. **`run_bias_audit()`** — The full audit. Run this once before submission. It loads the trained model and the training data, runs the model across every profile, computes the predicted-tier distribution for each age band, and writes two artifacts to disk:
   - `bias_audit_chart.png` — a stacked bar chart of tier distribution per band
   - `bias_audit_findings.txt` — a plain-language summary of what the audit found

2. **`render_bias_audit_summary()`** — Called by `app.py` to display the chart and findings inside the Streamlit UI. This function does **not** re-run the audit — it just reads the two files from disk and renders them. This is intentional: audits should be reproducible artifacts, not numbers that quietly change every time someone opens the app.

## How the audit is performed (step by step)

1. **Load the trained Random Forest** from `layer1_ml/model.pkl`. Bundled with the model are the feature columns and the encoder for `investment_experience`, so the audit uses identical preprocessing to training.
2. **Load all 2,000 profiles** from `data/financial_risk_profiles.csv`.
3. **Bin every profile's age** into one of four CFPB bands using `_band_for_age()`:
   - Under 30 (ages 0–29)
   - 30–54
   - 55–69
   - 70+ (70–200)
4. **Run the model** across the full dataset to get a predicted tier for each profile.
5. **Compute a cross-tab** of age band × predicted tier, normalized as percentages within each band (so each row sums to 100%).
6. **Plot a stacked bar chart**, with bands on the x-axis and tier-share on the y-axis, using a fixed color scheme (Low = green, Medium = orange, High = red) for visual consistency.
7. **Generate findings text** via `_generate_findings()`, which calls out:
   - Sample sizes per band
   - Tier distribution per band
   - The observed pattern (which band gets the most High predictions, which gets the most Low)
   - An honest caveat that age is a proxy, not a true demographic test

## Why this design

The standard fairness frameworks (demographic parity, equalized odds, etc.) require demographic data the project doesn't have. Rather than skip the audit or fake demographic data, the script does what it can with what's available and is upfront about the limitation.

The choice of CFPB age bands matters: they're the same bands used in the source training dataset (`cfpb_financial_wellbeing.csv`) and are widely recognized in U.S. consumer-finance research. Using familiar bands makes the chart legible to a non-technical reader.

The output artifacts (`bias_audit_chart.png` and `bias_audit_findings.txt`) get committed to the repo. The Streamlit app reads them from disk at runtime. This separation matters:

- **Reproducibility:** the artifacts capture exactly what the audit found at the time it was run. They don't quietly re-compute.
- **Performance:** the app stays fast — it's reading two static files, not re-running predictions on 2,000 rows on every page load.
- **Auditability:** if a grader wants to verify the audit, they can run `python -m layer4_respai.bias_audit` themselves and check that they get matching outputs.

## How to run it

From the project root, with the venv active:

```
python -m layer4_respai.bias_audit
```

Output:

- `layer4_respai/bias_audit_chart.png` (overwritten if it exists)
- `layer4_respai/bias_audit_findings.txt` (overwritten if it exists)
- Terminal output showing the findings text and confirmation messages

## What the most recent audit found

These are the actual numbers from the audit run on the trained model:

**Sample sizes by band:**
- Under 30: 343 profiles
- 30–54: 1,093 profiles
- 55–69: 564 profiles
- 70+: 0 profiles ← gap in the dataset, called out explicitly

**Tier distribution by band (% of band):**

| Age band | Low | Medium | High |
|---|---|---|---|
| Under 30 | 0.3% | 45.8% | 53.9% |
| 30–54 | 8.4% | 66.8% | 24.8% |
| 55–69 | 26.2% | 69.9% | 3.9% |
| 70+ | — | — | — |

**Observed pattern:** Younger profiles get assigned higher-risk tiers. Older profiles get assigned lower-risk tiers. This is consistent with how investment-horizon and age relate in the source labels — the model is **reproducing** the labeling pattern, not inventing one. Whether this is "bias" depends on whether the original labels are themselves a fair representation of recommended risk.

## Limitations (called out in the findings)

- Age is a **proxy**, not a true protected-class test. Age ≠ gender, race, or socioeconomic status.
- The audit cannot directly measure disparate impact on protected classes because the training data lacks those columns.
- The 70+ band is empty in the dataset, so the model has no learned behavior for that population — a real gap, not a result.
- A production deployment would need a richer dataset and a full fairness framework (demographic parity, equalized odds across protected slices).

## How to talk about this in the presentation

One sentence: *"Because our training data lacks demographic features, we audit fairness using an age-band proxy and document honestly that this is a proxy rather than a true protected-class test."*

Three-sentence version:

1. We binned all 2,000 training profiles into four CFPB age bands and ran the trained model across them, then computed how the predicted risk tiers were distributed within each band.
2. The model assigns roughly 54% of Under-30 profiles to High risk and 26% of 55–69 profiles to Low — consistent with the age-horizon relationship in the original labels, meaning the model is reproducing that pattern rather than discovering bias on its own.
3. We document explicitly that age is a proxy and that a production version would need richer demographic data and a full fairness framework — calling that limitation out is itself part of responsible AI practice.

## Owner

Per the project README, Layer 4 is owned by **Alex Harley** (Project Lead).

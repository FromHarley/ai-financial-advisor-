# `bias_audit_findings.txt` — Reference for Claude Code

## What this file is

`bias_audit_findings.txt` is the **plain-language written companion to the bias audit chart**. The chart shows the pattern visually; this file explains it in words. Together, they're the two outputs of running `bias_audit.py`. A grader reading this file alone (without the chart) should get the full story of what the audit found and how to interpret it.

## Where it lives

`layer4_respai/bias_audit_findings.txt`

## How it was made

This file is **generated automatically by `bias_audit.py`**, specifically by the helper function `_generate_findings()`. It's not hand-written. When you run the audit script, it:

1. Computes the cross-tab of age band × predicted tier.
2. Calls `_generate_findings()`, which formats the numbers into prose.
3. Writes the resulting text to this file, overwriting any previous version.

If you ever re-train the model or change the audit logic, **re-run `python -m layer4_respai.bias_audit`** to regenerate this file. Don't edit it by hand — the next audit run will silently wipe your edits.

## What the file contains

The findings text has four sections:

1. **Header and method:** A one-paragraph description of how the audit was performed. Mentions the four CFPB age bands, the 2,000-profile dataset, and the trained Random Forest classifier.

2. **Sample sizes by band:** Bullet list showing how many profiles fall into each age band. For the most recent audit run:
   - Under 30: 343 profiles
   - 30–54: 1,093 profiles
   - 55–69: 564 profiles
   - 70+: 0 profiles

3. **Tier distribution by band:** Bullet list showing the percentage of each band predicted into each risk tier:
   - Under 30: Low 0.3% · Medium 45.8% · High 53.9%
   - 30–54: Low 8.4% · Medium 66.8% · High 24.8%
   - 55–69: Low 26.2% · Medium 69.9% · High 3.9%
   - 70+: Low 0.0% · Medium 0.0% · High 0.0%

4. **Observed pattern (one paragraph):** Identifies which band gets the largest share of High and Low predictions, then explains *why* — pointing to the relationship between age and investment horizon in the source labels. Importantly, it states that the model is **reproducing** the pattern that exists in the labels, not discovering or inventing one. This is an honest framing.

5. **Honest caveat (one paragraph):** Explicitly calls out that the audit is a **proxy** analysis, not a true demographic fairness test. Age is not the same as gender, race, or socioeconomic status. The training data lacks those columns, so we cannot directly measure disparate impact on protected classes. A production deployment would need a richer dataset and a full fairness framework (demographic parity, equalized odds across protected slices). For a class project, the age-band view is the most honest fairness signal we can extract from the data we have.

## Why this design

The findings file is text, not Markdown rendered to HTML, because:

- **It's a plain artifact.** A grader can open it in any text editor.
- **It's the source of truth for the bias section of the model card.** The model card pulls from this file.
- **Streamlit can render it as Markdown.** The `render_bias_audit_summary()` function reads it with `Path.read_text()` and passes it to `st.markdown()`, so the bullet points and bold formatting still render visually in the app.

The "honest caveat" paragraph is the most important one in the file. Most student projects either skip the fairness audit entirely or run a fake one with surface-level numbers. By being explicit about what the audit *can't* tell us — that age is a proxy and we can't measure disparate impact on protected classes — the project shows it understands the limits of its own audit. That's a more sophisticated answer than overconfident claims of fairness would be.

## Where the file is read

- **The Streamlit app:** `bias_audit.py` defines `render_bias_audit_summary()`, which reads this file with `Path.read_text()` and passes it to `st.markdown()`. The findings appear inside the expandable "📋 Responsible AI — Model Card & Bias Audit" section at the bottom of the page.
- **The model card:** Section 5 of `model_card.md` summarizes these findings. The numbers in the model card should match this file — if they don't, the audit was re-run after the model card was last edited and someone needs to update the model card.

## Limitations the file calls out

- Age is a proxy, not a true demographic test.
- The audit cannot measure bias on protected classes (gender, race, education, etc.) because those columns aren't in the data.
- The 70+ band is empty — the model has no learned behavior for that population.
- A production system would need richer data and a full fairness framework.

## How to talk about this in the presentation

If asked: *"How do you know your model isn't biased?"*

The honest answer in three sentences:

1. We ran a fairness audit using age bands as a proxy and found that the model assigns younger profiles to higher-risk tiers and older profiles to lower-risk tiers, consistent with the age-horizon relationship in the source labels.
2. We can't measure disparate impact on protected classes — gender, race, education — because the training data doesn't include those columns, and we say that explicitly in the findings.
3. The fact that we don't claim our audit answers every fairness question is itself part of responsible AI practice — overclaiming a fairness audit is itself a form of bias, just at the meta-level.

## Owner

Per the project README, Layer 4 is owned by **Alex Harley** (Project Lead).

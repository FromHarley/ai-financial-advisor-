"""
Layer 4 · Bias audit.

OWNER: Alex Harley
BRANCH: layer4-respai

The spec requires a bias audit across at least one demographic slice. Our
challenge: the training data (financial_risk_profiles.csv) has no
demographic fields. Our approach, documented honestly in the model card:

1. Bin our training data's `age` into the same age buckets that CFPB uses
   (under 30, 30-54, 55-69, 70+).
2. Score each bucket with our trained model.
3. Compare the distribution of tiers produced by the model across age buckets.
4. Report whether the model disproportionately assigns one tier to any age group.
5. Be honest that this is a PROXY — not a true demographic fairness test.
   The CFPB data gives us population context; our model sees only age, not
   gender/race/education.

What you need to do:

1. Implement run_bias_audit() to produce a chart + write findings to
   `bias_audit_chart.png` and `bias_audit_findings.txt`.
2. Implement render_bias_audit_summary() to display both in the Streamlit UI.
3. Update the model_card.md with the findings text.
"""

from pathlib import Path

# TODO: import pandas as pd
# TODO: import matplotlib.pyplot as plt
# TODO: import streamlit as st

CHART_PATH = Path(__file__).parent / "bias_audit_chart.png"
FINDINGS_PATH = Path(__file__).parent / "bias_audit_findings.txt"


def run_bias_audit() -> None:
    """
    Run the full bias audit. Saves chart + findings text to disk.

    This is offline analysis — run it once before the final submission,
    commit the outputs, and let the UI read from disk at runtime.
    """
    # TODO: load data/financial_risk_profiles.csv
    # TODO: load the trained model from layer1_ml/model.pkl
    # TODO: bin ages into CFPB age groups
    # TODO: run model predictions for each row
    # TODO: groupby age_band, compute % of each tier predicted
    # TODO: plot stacked bar chart (age_band on x, tier % on y)
    # TODO: save to CHART_PATH
    # TODO: write a 2-paragraph finding to FINDINGS_PATH —
    #       be honest about what the proxy can and cannot show

    raise NotImplementedError(
        "Bias audit not yet run. Owner: Alex · Branch: layer4-respai"
    )


def render_bias_audit_summary() -> None:
    """Display the bias audit results in the Streamlit UI."""
    import streamlit as st

    if CHART_PATH.exists():
        st.image(str(CHART_PATH), caption="Risk tier distribution by age band")
    else:
        st.caption("⚠️ Bias audit chart not yet generated. Run `python -m layer4_respai.bias_audit`.")

    if FINDINGS_PATH.exists():
        st.markdown(FINDINGS_PATH.read_text())
    else:
        st.caption("⚠️ Bias audit findings not yet written.")


if __name__ == "__main__":
    run_bias_audit()

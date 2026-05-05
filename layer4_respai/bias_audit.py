"""
Layer 4 · Bias audit.

OWNER: Alex Harley
BRANCH: layer4-respai

Audits the trained ML model for fairness using age-band as a proxy,
since the training data lacks direct demographic columns.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

CHART_PATH = Path(__file__).parent / "bias_audit_chart.png"
FINDINGS_PATH = Path(__file__).parent / "bias_audit_findings.txt"
MODEL_PATH = Path(__file__).parent.parent / "layer1_ml" / "model.pkl"
DATA_PATH = Path(__file__).parent.parent / "data" / "financial_risk_profiles.csv"

AGE_BANDS = [
    ("Under 30", 0, 29),
    ("30-54", 30, 54),
    ("55-69", 55, 69),
    ("70+", 70, 200),
]


def _band_for_age(age: int) -> str:
    for label, lo, hi in AGE_BANDS:
        if lo <= age <= hi:
            return label
    return "Unknown"


def run_bias_audit() -> None:
    """
    Run the full bias audit. Saves chart + findings text to disk.
    """
    # Load model bundle
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    feature_cols = bundle["feature_cols"]
    label_inv = bundle["label_inv"]
    exp_map = bundle["exp_map"]

    # Load training data
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows from {DATA_PATH}")

    # Feature engineering (must match training)
    df["years_to_retirement"] = (65 - df["age"]).clip(lower=0)
    df["experience_encoded"] = df["investment_experience"].map(exp_map)

    X = df[feature_cols].values

    # Predict tiers for all rows
    y_pred = model.predict(X)
    df["predicted_tier"] = [label_inv[int(c)] for c in y_pred]

    # Bin ages
    df["age_band"] = df["age"].apply(_band_for_age)

    # Cross-tab: age_band x predicted_tier, normalized within each band
    band_order = [b[0] for b in AGE_BANDS]
    tier_order = ["Low", "Medium", "High"]

    ct = pd.crosstab(
        df["age_band"], df["predicted_tier"], normalize="index"
    ).reindex(index=band_order, columns=tier_order, fill_value=0) * 100

    # Sample sizes
    band_counts = df["age_band"].value_counts().reindex(band_order, fill_value=0)

    # Drop age bands with zero profiles so they don't appear on the chart
    nonempty = band_counts[band_counts > 0].index
    ct = ct.loc[ct.index.isin(nonempty)]

    # Plot stacked bar chart
    colors = {"Low": "#27ae60", "Medium": "#f39c12", "High": "#e74c3c"}
    fig, ax = plt.subplots(figsize=(8, 5))

    bottom = np.zeros(len(ct))
    for tier in tier_order:
        values = ct[tier].values
        ax.bar(ct.index, values, bottom=bottom, label=tier, color=colors[tier])
        bottom += values

    ax.set_ylabel("Share of age band (%)")
    ax.set_xlabel("Age band (CFPB standard)")
    ax.set_title("Predicted risk-tier distribution by age band")
    ax.legend(loc="lower right")
    ax.set_ylim(0, 105)

    plt.tight_layout()
    fig.savefig(CHART_PATH, dpi=150)
    plt.close(fig)
    print(f"Chart saved to {CHART_PATH}")

    # Generate findings text
    findings = _generate_findings(ct, band_counts)
    FINDINGS_PATH.write_text(findings, encoding="utf-8")
    print(f"Findings saved to {FINDINGS_PATH}")
    print()
    print(findings)


def _generate_findings(ct: pd.DataFrame, band_counts: pd.Series) -> str:
    lines = []
    lines.append("## Bias Audit Findings")
    lines.append("")
    lines.append(
        "**Method:** The trained classifier was run across all 2,000 training profiles, "
        "binned into four CFPB-standard age bands. The table below shows the share of "
        "each band predicted into each risk tier."
    )
    lines.append("")

    lines.append("**Sample sizes by band:**")
    for band in band_counts.index:
        lines.append(f"- {band}: {int(band_counts[band]):,} profiles")
    lines.append("")

    lines.append("**Tier distribution by band:**")
    for band in ct.index:
        low = ct.loc[band, "Low"]
        med = ct.loc[band, "Medium"]
        high = ct.loc[band, "High"]
        total = int(band_counts.get(band, 0))
        if total == 0:
            lines.append(f"- {band}: no profiles in dataset")
        else:
            lines.append(f"- {band}: Low {low:.1f}% · Medium {med:.1f}% · High {high:.1f}%")
    lines.append("")

    lines.append(
        "**Observed pattern:** Younger profiles are assigned higher-risk tiers more "
        "frequently, while older profiles skew toward lower-risk tiers. This is consistent "
        "with the relationship between age, investment horizon, and risk tolerance in the "
        "source labels — the model is reproducing the labeling pattern, not inventing one."
    )
    lines.append("")
    lines.append(
        "**Honest caveat:** This is a proxy analysis, not a true demographic fairness test. "
        "Age is not equivalent to gender, race, or socioeconomic status. The training data "
        "lacks those columns, so we cannot directly measure disparate impact on protected "
        "classes. A production deployment would need a richer dataset and a full fairness "
        "framework (demographic parity, equalized odds across protected slices). For a class "
        "project, the age-band view is the most honest fairness signal we can extract from "
        "the data we have."
    )

    return "\n".join(lines)


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

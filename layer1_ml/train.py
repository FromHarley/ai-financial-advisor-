"""
Layer 1 · Offline training script.

OWNER: [TBD at kickoff]
BRANCH: layer1-ml

Run this ONCE to produce `model.pkl`. After that, the app loads the
pickled model for inference in `predict.py`.

What you need to do:

1. Load `data/financial_risk_profiles.csv`.
2. Split into X (6 features) and y (risk_tier).
3. Train a RandomForestClassifier.
4. Evaluate: print accuracy, per-class precision/recall, confusion matrix.
5. Save the trained model (and any preprocessing) to `layer1_ml/model.pkl`.
6. Write the metrics into `layer4_respai/model_card.md` (or give them to Alex).

Usage:
    python -m layer1_ml.train

Required output: `layer1_ml/model.pkl` file exists after this script runs.
"""

from pathlib import Path

import joblib
import pandas as pd

# TODO: from sklearn.ensemble import RandomForestClassifier
# TODO: from sklearn.model_selection import train_test_split
# TODO: from sklearn.metrics import classification_report, confusion_matrix


DATA_PATH = Path(__file__).parent.parent / "data" / "financial_risk_profiles.csv"
MODEL_PATH = Path(__file__).parent / "model.pkl"

FEATURE_COLS = [
    "age",
    "annual_income_usd",
    "savings_rate_pct",
    "debt_to_income_ratio",
    "investment_horizon_years",
    "investment_experience",
]
TARGET_COL = "risk_tier"


def train():
    """Train the risk-tier classifier and save it to MODEL_PATH."""
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows from {DATA_PATH}")

    # TODO: handle categorical feature `investment_experience`
    #   (Beginner / Intermediate / Advanced) — ordinal encoding is fine
    # TODO: split into X, y
    # TODO: train/test split (stratify on y)
    # TODO: fit RandomForestClassifier(n_estimators=200, random_state=42)
    # TODO: evaluate on test set — print results
    # TODO: save {'model': model, 'feature_cols': FEATURE_COLS, ...} to MODEL_PATH

    raise NotImplementedError(
        "Layer 1 training not yet implemented. "
        "Assigned to: [TBD] · Branch: layer1-ml"
    )


if __name__ == "__main__":
    train()

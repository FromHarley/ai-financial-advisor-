"""
Layer 1 · Offline training script.

OWNER: Alex Harley
BRANCH: layer1-ml

Run this ONCE to produce `model.pkl`. After that, the app loads the
pickled model for inference in `predict.py`.

Usage:
    python -m layer1_ml.train
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix
from xgboost import XGBClassifier

DATA_PATH = Path(__file__).parent.parent / "data" / "financial_risk_profiles.csv"
MODEL_PATH = Path(__file__).parent / "model.pkl"

FEATURE_COLS = [
    "age",
    "years_to_retirement",
    "annual_income_usd",
    "savings_rate_pct",
    "debt_to_income_ratio",
    "investment_horizon_years",
    "experience_encoded",
]
TARGET_COL = "risk_tier"
LABEL_MAP = {"Low": 0, "Medium": 1, "High": 2}
LABEL_INV = {v: k for k, v in LABEL_MAP.items()}


def train():
    """Train the risk-tier classifier and save it to MODEL_PATH."""
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows from {DATA_PATH}")

    # Feature engineering
    df["years_to_retirement"] = (65 - df["age"]).clip(lower=0)
    exp_map = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
    df["experience_encoded"] = df["investment_experience"].map(exp_map)

    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].map(LABEL_MAP).values

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y,
    )
    print(f"Train: {len(X_train)} rows, Test: {len(X_test)} rows")

    # Class weights
    classes = np.unique(y_train)
    weights = compute_class_weight("balanced", classes=classes, y=y_train)
    weight_dict = dict(zip(classes, weights))
    sample_weights = np.array([weight_dict[label] for label in y_train])

    # Train XGBoost
    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(
        X_train, y_train,
        sample_weight=sample_weights,
        eval_set=[(X_test, y_test)],
        verbose=50,
    )

    # Evaluate
    y_pred = model.predict(X_test)
    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred, target_names=["Low", "Medium", "High"]))
    print("=== Confusion Matrix ===")
    print(confusion_matrix(y_test, y_pred))

    # Save bundle
    model_bundle = {
        "model": model,
        "feature_cols": FEATURE_COLS,
        "label_map": LABEL_MAP,
        "label_inv": LABEL_INV,
        "exp_map": exp_map,
        "notes": "XGBoost · class-weight balanced · age + years_to_retirement (engineered)",
    }
    joblib.dump(model_bundle, MODEL_PATH)
    print(f"\nSaved {MODEL_PATH} ({MODEL_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    train()

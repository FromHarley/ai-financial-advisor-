# Data

Two CSVs are included for this project. Do not modify these files — they are
the inputs to our ML training and our bias audit.

## `financial_risk_profiles.csv`

**Purpose:** Training data for Layer 1 (ML classifier).

**Rows:** 2,000

**Columns:**
- `age` (int) — investor age
- `annual_income_usd` (int) — annual income in USD
- `savings_rate_pct` (float) — savings as a percentage of income
- `debt_to_income_ratio` (float) — total debt / annual income
- `investment_horizon_years` (int) — how long they plan to invest for
- `investment_experience` (str) — "Beginner" | "Intermediate" | "Advanced"
- `investment_goal` (str) — e.g. "Retirement"
- **`risk_tier`** (str) — target label: "Low" | "Medium" | "High"

**Per the project spec:** "Ready to train — no preprocessing needed."

## `cfpb_financial_wellbeing.csv`

**Purpose:** Demographic reference data for Layer 4 (bias audit).

**Rows:** 2,000

**Columns:**
- `age` (int)
- `age_group` (str) — e.g. "55-69"
- `gender` (str)
- `income_group` (str) — e.g. "$30k-$60k"
- `education_level` (str) — e.g. "Bachelor's"
- `financial_wellbeing_score` (int)
- `has_emergency_fund` (0/1)
- `has_retirement_account` (0/1)
- `credit_score_band` (str)

**Important:** This is NOT training data. The model never sees demographic
fields. We use this file only to build an age-band proxy for the bias audit
(see `layer4_respai/bias_audit.py`).

## Why we don't have direct demographic training data

The training data deliberately excludes gender, race, and education. This
means we cannot directly measure disparate impact across those dimensions.
Our audit uses an age-band proxy and is explicit in the model card about
what the proxy can and cannot tell us. That honesty is part of the grade.

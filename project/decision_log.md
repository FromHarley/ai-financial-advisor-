# `decision_log.py` — Reference for Claude Code

## What this file is

`decision_log.py` is the **human-in-the-loop gate** for the AI Financial Advisor. It's the piece of code that turns the system from "an AI that makes recommendations" into "an AI that makes recommendations a human has to actually approve before anything is recorded." Without this file, Layer 4's claim of human oversight would be marketing, not architecture. With it, the claim is provable: every entry in the log file is, by definition, a decision a human clicked through.

## Where it lives

`layer4_respai/decision_log.py`

## What it does

The file exposes one public function, `log_decision()`, which is called by `app.py` after the user clicks either the **✅ Accept** button or the **❌ Reject** button at the bottom of the recommendation flow.

When called, it writes one row to a CSV file at `layer4_respai/decisions.csv` containing:

- **timestamp** — ISO-format datetime of when the decision was made
- **user_decision** — the string `"accept"` or `"reject"`
- **tier** — the risk tier the model predicted (Low / Medium / High)
- **profile_json** — the user's full input profile, serialized as JSON, so the inputs that produced the recommendation are preserved
- **etfs_json** — the ETF shortlist that was shown to the user, also as JSON
- **explanation** — the plain-English text that Claude (Layer 2) wrote for that recommendation

The function handles file creation automatically — if `decisions.csv` doesn't exist yet, it creates it with the right headers on the first call. After that, every subsequent call appends a new row.

## Why it's designed this way

The audit trail has to answer three questions if anyone ever asks:

1. **Was this recommendation shown to the user before anything happened?** Yes — the gate is between "show the recommendation" and "log it."
2. **Did the user have a real choice?** Yes — both Accept and Reject paths log a row, so we can show a Reject is just as recordable as an Accept.
3. **Can we reproduce this decision later?** Yes — the full input profile is in the row, so we could re-run Layer 1 on it and get the same prediction.

Storing the profile and ETFs as JSON strings (instead of flattening every field into its own column) keeps the CSV stable as the project evolves. If someone adds a new input feature later, the schema doesn't break.

## How it gets called

In `app.py`, the call looks roughly like:

```python
from layer4_respai.decision_log import log_decision

if accept_button_clicked:
    log_decision(
        profile=user_profile_dict,
        tier=predicted_tier,
        etfs=etf_recommendations,
        explanation=claude_explanation_text,
        user_decision="accept",
    )
```

The function returns nothing — it's fire-and-forget. The app just shows "Recommendation accepted and logged. Thank you!" once the call completes.

## What's in the file (technical)

- `from __future__ import annotations` — needed at the top for Python 3.9 compatibility (the project's type hints use newer syntax like `list[dict]` that 3.9 doesn't natively support).
- `LOG_PATH` constant pointing to `decisions.csv` in the same folder.
- `FIELDNAMES` list defining the CSV schema in a single place — important so the writer and any future reader stay in sync.
- The `log_decision()` function itself, which opens the file in append mode, writes the headers if the file is new, and writes one row per call.

## Limitations and known issues

- The log file is **local only**. It writes to disk in the project folder. In a real deployment, this would need to go to a database or cloud storage with proper access controls.
- The log is **not tamper-proof**. Anyone with file access can open `decisions.csv` and edit rows. A production system would need cryptographic signing or an append-only data store.
- There's **no user identity field** because the app currently has no authentication. Every row is implicitly "the user who was using the app at that timestamp." Adding a user ID would be a one-line schema change.
- The CSV grows forever. There's no rotation or archiving logic.

These limitations are documented in the model card under "Known limitations" and are appropriate for a class project — they would not be appropriate for a production financial system.

## How to demo this in the presentation

1. Fill out the form in the app, click Analyze, get a recommendation.
2. Click **✅ Accept**. Show the green "Recommendation accepted and logged" message.
3. Open Terminal and run `cat layer4_respai/decisions.csv` — show the row that just got written.
4. Repeat with a fresh profile and click **❌ Reject** instead. Show the new row.
5. The takeaway sentence: *"Nothing gets recorded as a decision until the user clicks. Both Accept and Reject are recorded — the system is structurally incapable of taking action without human input."*

## Owner

Per the project README, Layer 4 is owned by **Alex Harley** (Project Lead).

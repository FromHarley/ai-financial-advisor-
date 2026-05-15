"""
Layer 4 · Human-in-the-loop decision logging.

Nothing gets logged until the user explicitly clicks Accept or Reject.
This IS the human-in-the-loop gate — it's not a decoration.

The log file is our audit trail. It proves that:
1. Every recommendation was shown to the user before any action was "committed".
2. The user had a real choice (Accept vs Reject).
3. We can trace any logged decision back to its inputs.
4. User feedback is captured alongside each decision for post-demo analysis.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

LOG_PATH = Path(__file__).parent / "decisions.csv"

FIELDNAMES = [
    "timestamp",
    "user_decision",
    "tier",
    "profile_json",
    "etfs_json",
    "explanation",
    "feedback_rating",
    "feedback_text",
]


def log_decision(
    profile: dict,
    tier: str,
    etfs: list[dict],
    explanation: str,
    user_decision: str,
    feedback_rating: Optional[str] = None,
    feedback_text: Optional[str] = None,
) -> None:
    """
    Log a user decision and optional feedback to the audit trail.

    Args:
        profile: The user's financial profile.
        tier: The predicted risk tier.
        etfs: The ETF shortlist shown to the user.
        explanation: The Claude-generated explanation.
        user_decision: 'accept' | 'reject' — must be set by explicit user action.
        feedback_rating: Optional rating (e.g. "Very useful").
        feedback_text: Optional free-text feedback.

    Raises:
        ValueError: if user_decision is not 'accept' or 'reject'.
    """
    if user_decision not in ("accept", "reject"):
        raise ValueError(
            f"Invalid user_decision: {user_decision!r}. "
            "Must be 'accept' or 'reject' — no logging without explicit user input."
        )

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_decision": user_decision,
        "tier": tier,
        "profile_json": json.dumps(profile),
        "etfs_json": json.dumps([{k: v for k, v in e.items() if k != "_raw"} for e in etfs]),
        "explanation": explanation,
        "feedback_rating": feedback_rating or "",
        "feedback_text": (feedback_text or "").strip(),
    }

    file_exists = LOG_PATH.exists()
    with LOG_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

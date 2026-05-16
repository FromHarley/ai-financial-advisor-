"""
Layer 4 · Human-in-the-loop decision logging.

Nothing gets logged until the user explicitly clicks Accept or Reject.
This IS the human-in-the-loop gate — it's not a decoration.

Logs to Google Sheets for persistence across Streamlit Cloud reboots.
Falls back to a local CSV if Sheets credentials are not configured.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import streamlit as st

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


def _get_gsheet():
    """Return the first worksheet of the configured Google Sheet, or None."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(st.secrets["decisions_sheet"]["sheet_id"])
        return sheet.sheet1
    except Exception:
        return None


def _ensure_sheet_header(ws):
    """Add a header row if the sheet is empty."""
    try:
        if not ws.get_all_values():
            ws.append_row(FIELDNAMES)
    except Exception:
        pass


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
    Log a user decision and optional feedback.

    Writes to Google Sheets if configured, otherwise falls back to local CSV.
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

    # Try Google Sheets first
    ws = _get_gsheet()
    if ws is not None:
        try:
            _ensure_sheet_header(ws)
            ws.append_row([row[f] for f in FIELDNAMES])
            return
        except Exception:
            pass  # fall through to CSV

    # Fallback: local CSV
    file_exists = LOG_PATH.exists()
    with LOG_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

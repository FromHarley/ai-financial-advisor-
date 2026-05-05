"""
Layer 3 · The agent: fetch live ETF data, assemble shortlist.

OWNER: Kimberly Ting
BRANCH: layer3-agentic
"""

import json
from pathlib import Path
import yfinance as yf

from layer3_agentic.tier_mapping import get_etfs_for_tier

CACHE_PATH = Path(__file__).parent / "etf_cache.json"


def get_etf_recommendations(tier: str) -> list[dict]:
    base_etfs = get_etfs_for_tier(tier)
    rationale_template = _get_rationale_template(tier)
    results = []
    cache = _load_cache()

    for etf in base_etfs:
        ticker = etf["ticker"]
        price = _fetch_price(ticker)

        if price is None and ticker in cache:
            price = cache[ticker].get("price")

        results.append({
            "ticker": ticker,
            "name": etf["name"],
            "category": etf["category"],
            "current_price": price,
            "rationale": rationale_template.format(category=etf["category"]),
        })

        if price is not None:
            cache[ticker] = {"price": price, "name": etf["name"]}

    _save_cache(cache)
    return results


def _fetch_price(ticker: str) -> float | None:
    try:
        yf_ticker = yf.Ticker(ticker)
        hist = yf_ticker.history(period='5d')
        return round(float(hist['Close'].iloc[-1]), 2) if not hist.empty else None
    except Exception:
        return None


def _get_rationale_template(tier: str) -> str:
    return {
        "Low": "A {category} fund chosen for stability and capital preservation.",
        "Medium": "A {category} fund providing balanced growth exposure.",
        "High": "A {category} fund selected for higher long-term growth potential.",
    }.get(tier, "A {category} fund matching your risk profile.")


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    try:
        CACHE_PATH.write_text(json.dumps(cache, indent=2))
    except OSError:
        pass

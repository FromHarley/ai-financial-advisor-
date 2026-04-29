"""
Layer 3 · The agent: fetch live ETF data, assemble shortlist.

OWNER: [TBD at kickoff]
BRANCH: layer3-agentic

This is our "agentic" layer in the course's sense — the system autonomously
takes a tier and produces a concrete, actionable shortlist without a human
telling it which fund to pick.

What you need to do:

1. For each ETF in the tier's list, fetch the current price via yfinance.
2. Add a short rationale (one sentence) explaining why this fund fits the tier.
3. Cache successful fetches to `etf_cache.json` so demo day has a fallback
   if yfinance is down or rate-limited.
4. On fetch failure, fall back to cache silently (don't crash the app).

Safety scope (important for the presentation): THIS AGENT ONLY RECOMMENDS.
It does not place trades, move money, or execute anything. Document this
in the model card.
"""

import json
from pathlib import Path

# TODO: import yfinance as yf

from layer3_agentic.tier_mapping import get_etfs_for_tier

CACHE_PATH = Path(__file__).parent / "etf_cache.json"


def get_etf_recommendations(tier: str) -> list[dict]:
    """
    Return ETF recommendations for a given risk tier, with live prices
    and a rationale per fund.

    Args:
        tier: 'Low' | 'Medium' | 'High'

    Returns:
        List of dicts with keys: ticker, name, current_price, category, rationale.
    """
    base_etfs = get_etfs_for_tier(tier)
    rationale_template = _get_rationale_template(tier)

    results = []
    cache = _load_cache()

    for etf in base_etfs:
        ticker = etf["ticker"]
        price = _fetch_price(ticker)

        # Fall back to cache if live fetch failed
        if price is None and ticker in cache:
            price = cache[ticker].get("price")

        # Final fallback: None, so the UI shows "--"
        results.append({
            "ticker": ticker,
            "name": etf["name"],
            "category": etf["category"],
            "current_price": price,
            "rationale": rationale_template.format(category=etf["category"]),
        })

        # Update cache on successful fetch
        if price is not None:
            cache[ticker] = {"price": price, "name": etf["name"]}

    _save_cache(cache)
    return results


def _fetch_price(ticker: str) -> float | None:
    """Fetch the latest close price for a ticker, returning None on failure."""
    # TODO: yf_ticker = yf.Ticker(ticker)
    # TODO: hist = yf_ticker.history(period='5d')
    # TODO: return float(hist['Close'].iloc[-1]) if not hist.empty else None
    # TODO: wrap in try/except and return None on any exception

    # --- STUB ---
    stub_prices = {
        "BND": 72.10, "SCHD": 27.45, "VTIP": 48.90,
        "VTI": 265.30, "VEA": 51.20,
        "QQQ": 485.70, "IWM": 215.40, "VUG": 380.15,
    }
    return stub_prices.get(ticker)


def _get_rationale_template(tier: str) -> str:
    """One-liner rationale per tier. Keep it short — Claude elaborates in Layer 2."""
    return {
        "Low": "A {category} fund chosen for stability and capital preservation.",
        "Medium": "A {category} fund providing balanced growth exposure.",
        "High": "A {category} fund selected for higher long-term growth potential.",
    }.get(tier, "A {category} fund matching your risk profile.")


def _load_cache() -> dict:
    """Load the ETF price cache from disk. Returns empty dict if missing."""
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    """Persist the ETF price cache to disk for demo-day fallback."""
    try:
        CACHE_PATH.write_text(json.dumps(cache, indent=2))
    except OSError:
        pass  # Caching is best-effort; don't crash the app

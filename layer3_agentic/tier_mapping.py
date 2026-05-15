"""
Layer 3 · Tier → ETF mapping rules.

Expanded ETF universe with profile-aware selection. Each tier has a broader
pool of ETFs organized by sub-category. The agent selects 4-5 ETFs per
recommendation based on the user's profile (horizon, income, experience)
so that two people with the same tier but different profiles get different
portfolios.
"""

from __future__ import annotations

from typing import Optional

# ---------------------------------------------------------------------------
# Full ETF universe by tier
# ---------------------------------------------------------------------------

LOW_RISK_POOL = {
    "core_bonds": [
        {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "category": "Bonds"},
        {"ticker": "AGG", "name": "iShares Core U.S. Aggregate Bond ETF", "category": "Bonds"},
    ],
    "short_duration": [
        {"ticker": "VTIP", "name": "Vanguard Short-Term Inflation-Protected Securities", "category": "Inflation-Protected"},
        {"ticker": "SHV", "name": "iShares Short Treasury Bond ETF", "category": "Short-Term Treasury"},
        {"ticker": "VGSH", "name": "Vanguard Short-Term Treasury ETF", "category": "Short-Term Treasury"},
    ],
    "dividend": [
        {"ticker": "SCHD", "name": "Schwab U.S. Dividend Equity ETF", "category": "Dividend Equity"},
        {"ticker": "VYM", "name": "Vanguard High Dividend Yield ETF", "category": "Dividend Equity"},
        {"ticker": "DVY", "name": "iShares Select Dividend ETF", "category": "Dividend Equity"},
    ],
    "defensive": [
        {"ticker": "XLU", "name": "Utilities Select Sector SPDR Fund", "category": "Utilities"},
        {"ticker": "VNQ", "name": "Vanguard Real Estate ETF", "category": "Real Estate"},
        {"ticker": "XLP", "name": "Consumer Staples Select Sector SPDR Fund", "category": "Consumer Staples"},
    ],
}

MEDIUM_RISK_POOL = {
    "us_broad": [
        {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "category": "US Broad Market"},
        {"ticker": "SPY", "name": "SPDR S&P 500 ETF Trust", "category": "US Large-Cap"},
        {"ticker": "ITOT", "name": "iShares Core S&P Total U.S. Stock Market ETF", "category": "US Broad Market"},
    ],
    "international": [
        {"ticker": "VEA", "name": "Vanguard FTSE Developed Markets ETF", "category": "International Developed"},
        {"ticker": "VXUS", "name": "Vanguard Total International Stock ETF", "category": "International Equity"},
        {"ticker": "EFA", "name": "iShares MSCI EAFE ETF", "category": "International Developed"},
    ],
    "bond_ballast": [
        {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "category": "Bonds"},
        {"ticker": "BNDX", "name": "Vanguard Total International Bond ETF", "category": "International Bonds"},
    ],
    "balanced_growth": [
        {"ticker": "VIG", "name": "Vanguard Dividend Appreciation ETF", "category": "Dividend Growth"},
        {"ticker": "DGRO", "name": "iShares Core Dividend Growth ETF", "category": "Dividend Growth"},
        {"ticker": "RSP", "name": "Invesco S&P 500 Equal Weight ETF", "category": "US Equal Weight"},
    ],
    "sector_tilt": [
        {"ticker": "XLK", "name": "Technology Select Sector SPDR Fund", "category": "Technology"},
        {"ticker": "XLV", "name": "Health Care Select Sector SPDR Fund", "category": "Healthcare"},
        {"ticker": "XLF", "name": "Financial Select Sector SPDR Fund", "category": "Financials"},
    ],
}

HIGH_RISK_POOL = {
    "large_cap_growth": [
        {"ticker": "QQQ", "name": "Invesco QQQ Trust (Nasdaq-100)", "category": "Large-Cap Growth"},
        {"ticker": "VUG", "name": "Vanguard Growth ETF", "category": "US Growth"},
        {"ticker": "MGK", "name": "Vanguard Mega Cap Growth ETF", "category": "Mega-Cap Growth"},
    ],
    "small_mid_cap": [
        {"ticker": "IWM", "name": "iShares Russell 2000 ETF", "category": "Small-Cap"},
        {"ticker": "VXF", "name": "Vanguard Extended Market ETF", "category": "Mid/Small-Cap"},
        {"ticker": "IJR", "name": "iShares Core S&P Small-Cap ETF", "category": "Small-Cap"},
    ],
    "sector_momentum": [
        {"ticker": "XLK", "name": "Technology Select Sector SPDR Fund", "category": "Technology"},
        {"ticker": "SOXX", "name": "iShares Semiconductor ETF", "category": "Semiconductors"},
        {"ticker": "XBI", "name": "SPDR S&P Biotech ETF", "category": "Biotech"},
    ],
    "emerging_markets": [
        {"ticker": "VWO", "name": "Vanguard FTSE Emerging Markets ETF", "category": "Emerging Markets"},
        {"ticker": "EEM", "name": "iShares MSCI Emerging Markets ETF", "category": "Emerging Markets"},
    ],
    "thematic": [
        {"ticker": "ARKK", "name": "ARK Innovation ETF", "category": "Innovation/Thematic"},
        {"ticker": "ICLN", "name": "iShares Global Clean Energy ETF", "category": "Clean Energy"},
        {"ticker": "BOTZ", "name": "Global X Robotics & AI ETF", "category": "Robotics & AI"},
    ],
}


# ---------------------------------------------------------------------------
# Profile-aware selection logic
# ---------------------------------------------------------------------------

def get_etfs_for_tier(tier: str, profile: Optional[dict] = None) -> list[dict]:
    """
    Return a personalized ETF shortlist (4-5 funds) for a risk tier.

    If a profile is provided, the selection adapts based on:
    - Investment horizon (short vs long)
    - Income level (higher income → more diversification)
    - Experience level (beginner → simpler picks, advanced → sector tilts)

    If no profile is provided, returns sensible defaults (backward-compatible).
    """
    if tier == "Low":
        return _select_low(profile)
    elif tier == "Medium":
        return _select_medium(profile)
    elif tier == "High":
        return _select_high(profile)
    else:
        raise ValueError(f"Unknown tier: {tier}. Expected Low/Medium/High.")


def _pick(pool: list[dict], index: int = 0) -> dict:
    """Pick an ETF from a sub-category pool by index (wraps around)."""
    return pool[index % len(pool)]


def _select_low(profile: Optional[dict]) -> list[dict]:
    if profile is None:
        return [
            _pick(LOW_RISK_POOL["core_bonds"]),
            _pick(LOW_RISK_POOL["dividend"]),
            _pick(LOW_RISK_POOL["short_duration"]),
        ]

    horizon = profile.get("investment_horizon_years", 10)
    income = profile.get("annual_income_usd", 50000)
    exp = profile.get("investment_experience", "Beginner")

    picks = []

    # Core bond allocation — always included
    picks.append(_pick(LOW_RISK_POOL["core_bonds"], 0 if horizon <= 10 else 1))

    # Short horizon → heavier short-duration; long horizon → dividend focus
    if horizon <= 7:
        picks.append(_pick(LOW_RISK_POOL["short_duration"], 0))
        picks.append(_pick(LOW_RISK_POOL["short_duration"], 2))
    else:
        picks.append(_pick(LOW_RISK_POOL["dividend"], 0))
        picks.append(_pick(LOW_RISK_POOL["short_duration"], 0))

    # Higher income or experience → add defensive sector exposure
    if income >= 80000 or exp in ("Intermediate", "Advanced"):
        picks.append(_pick(LOW_RISK_POOL["defensive"], 0 if income >= 100000 else 2))
    else:
        picks.append(_pick(LOW_RISK_POOL["dividend"], 1))

    # Advanced investors get an extra diversifier
    if exp == "Advanced":
        picks.append(_pick(LOW_RISK_POOL["defensive"], 1))

    return picks


def _select_medium(profile: Optional[dict]) -> list[dict]:
    if profile is None:
        return [
            _pick(MEDIUM_RISK_POOL["us_broad"]),
            _pick(MEDIUM_RISK_POOL["international"]),
            _pick(MEDIUM_RISK_POOL["bond_ballast"]),
        ]

    horizon = profile.get("investment_horizon_years", 15)
    income = profile.get("annual_income_usd", 60000)
    exp = profile.get("investment_experience", "Beginner")

    picks = []

    # US core — always included
    picks.append(_pick(MEDIUM_RISK_POOL["us_broad"], 0 if exp == "Beginner" else 1))

    # International exposure
    picks.append(_pick(MEDIUM_RISK_POOL["international"], 0 if horizon >= 15 else 2))

    # Bond ballast — more bonds for shorter horizons
    if horizon < 10:
        picks.append(_pick(MEDIUM_RISK_POOL["bond_ballast"], 0))
    elif horizon < 20:
        picks.append(_pick(MEDIUM_RISK_POOL["balanced_growth"], 0))
    else:
        picks.append(_pick(MEDIUM_RISK_POOL["balanced_growth"], 1))

    # Higher income → sector tilt; lower income → dividend growth for stability
    if income >= 90000:
        picks.append(_pick(MEDIUM_RISK_POOL["sector_tilt"], 0))
    elif income >= 60000:
        picks.append(_pick(MEDIUM_RISK_POOL["balanced_growth"], 2))
    else:
        picks.append(_pick(MEDIUM_RISK_POOL["balanced_growth"], 0))

    # Experienced investors get international bonds or a sector pick
    if exp == "Advanced":
        picks.append(_pick(MEDIUM_RISK_POOL["sector_tilt"], 1))

    return picks


def _select_high(profile: Optional[dict]) -> list[dict]:
    if profile is None:
        return [
            _pick(HIGH_RISK_POOL["large_cap_growth"]),
            _pick(HIGH_RISK_POOL["small_mid_cap"]),
            _pick(HIGH_RISK_POOL["sector_momentum"]),
        ]

    horizon = profile.get("investment_horizon_years", 20)
    income = profile.get("annual_income_usd", 70000)
    exp = profile.get("investment_experience", "Beginner")

    picks = []

    # Growth core — always included
    picks.append(_pick(HIGH_RISK_POOL["large_cap_growth"], 0 if exp != "Advanced" else 2))

    # Small/mid-cap exposure
    picks.append(_pick(HIGH_RISK_POOL["small_mid_cap"], 0 if horizon >= 15 else 1))

    # Sector momentum for longer horizons
    if horizon >= 15:
        picks.append(_pick(HIGH_RISK_POOL["sector_momentum"], 1))
    else:
        picks.append(_pick(HIGH_RISK_POOL["large_cap_growth"], 1))

    # Higher income → emerging markets diversification
    if income >= 80000:
        picks.append(_pick(HIGH_RISK_POOL["emerging_markets"], 0))
    else:
        picks.append(_pick(HIGH_RISK_POOL["small_mid_cap"], 2))

    # Experienced investors get thematic exposure
    if exp == "Advanced":
        picks.append(_pick(HIGH_RISK_POOL["thematic"], 0 if income >= 100000 else 2))
    elif exp == "Intermediate" and horizon >= 20:
        picks.append(_pick(HIGH_RISK_POOL["thematic"], 2))

    return picks

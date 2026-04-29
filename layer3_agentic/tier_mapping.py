"""
Layer 3 · Tier → ETF mapping rules.

OWNER: [TBD at kickoff]
BRANCH: layer3-agentic

These are our hand-picked ETF universes per risk tier. The logic is simple
and deliberate — we're not trying to be a robo-advisor, we're showing that
an agent can make category-appropriate recommendations.

Justify each choice in a one-line comment. When you change these, tell the
team at a meeting — Layer 2 (Claude) references these names in its prompt
context, and Layer 4 (model card) documents them.
"""

# Low risk → bond-heavy, dividend-focused, defensive
LOW_RISK_ETFS = [
    {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "category": "Bonds"},
    {"ticker": "SCHD", "name": "Schwab U.S. Dividend Equity ETF", "category": "Dividend Equity"},
    {"ticker": "VTIP", "name": "Vanguard Short-Term Inflation-Protected Securities", "category": "Inflation-Protected"},
]

# Medium risk → broad market equity with some international + bond ballast
MEDIUM_RISK_ETFS = [
    {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "category": "US Broad Market"},
    {"ticker": "VEA", "name": "Vanguard FTSE Developed Markets ETF", "category": "International Equity"},
    {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "category": "Bonds"},
]

# High risk → growth-tilted equity, small-cap exposure, tech-heavy
HIGH_RISK_ETFS = [
    {"ticker": "QQQ", "name": "Invesco QQQ Trust (Nasdaq-100)", "category": "Large-Cap Growth"},
    {"ticker": "IWM", "name": "iShares Russell 2000 ETF", "category": "Small-Cap"},
    {"ticker": "VUG", "name": "Vanguard Growth ETF", "category": "US Growth"},
]


TIER_MAP = {
    "Low": LOW_RISK_ETFS,
    "Medium": MEDIUM_RISK_ETFS,
    "High": HIGH_RISK_ETFS,
}


def get_etfs_for_tier(tier: str) -> list[dict]:
    """Return the base ETF list for a given risk tier (pre-price-fetch)."""
    if tier not in TIER_MAP:
        raise ValueError(f"Unknown tier: {tier}. Expected Low/Medium/High.")
    return TIER_MAP[tier]

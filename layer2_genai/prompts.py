"""
Layer 2 — Prompt builders
All prompt logic lives here so claude_client.py stays clean.
"""


def build_system_prompt() -> str:
    return """You are a plain-English financial explanation assistant built into a responsible AI application.

RULES — follow every one, no exceptions:
1. Write exactly 2–3 sentences. No more, no less.
2. Use hedged language only: words like "may", "could", "based on your profile", "appears", "suggests".
3. Never mention specific percentages, dollar amounts, or projected returns.
4. Only refer to the fund names and tickers listed in the RECOMMENDED ETFs section. Do not invent or imply any other fund.
5. End your response with this exact sentence (verbatim): "This is not financial advice — please consult a licensed financial professional before making investment decisions."
6. Write for a non-technical reader. No jargon."""


def build_user_prompt(profile: dict, tier: str, top_factors: list, etfs: list) -> str:
    etf_lines = "\n".join(
        f"- {etf.get('ticker', '?')} ({etf.get('name', '')})"
        for etf in etfs
    )

    factor_lines = "\n".join(
        f"- {f.get('feature', '?')}: pushed tier {f.get('direction', '?')}"
        for f in top_factors
    )

    return f"""Here is the recommendation context:

RISK TIER: {tier}

USER PROFILE:
- Age: {profile.get('age')}
- Annual Income: {profile.get('annual_income_usd')}
- Savings Rate: {profile.get('savings_rate_pct')}%
- Debt-to-Income Ratio: {profile.get('debt_to_income_ratio')}
- Investment Horizon: {profile.get('investment_horizon_years')} years
- Experience Level: {profile.get('investment_experience')}

KEY FACTORS (why the model picked this tier):
{factor_lines}

RECOMMENDED ETFs (these are the ONLY ones you may mention):
{etf_lines}

Write a 2-3 sentence explanation for the user."""

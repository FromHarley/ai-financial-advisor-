"""
Layer 2 · Prompt templates for Claude.

OWNER: [TBD at kickoff]
BRANCH: layer2-genai

Separating prompts from the API call makes them easier to iterate on and
easier to explain in the presentation.

Design goals for the prompt:
1. Hedged language — no "this will definitely work" claims.
2. No specific return figures (no "you'll make 8% a year").
3. Mandatory "not financial advice" disclaimer appended to every response.
4. ONLY reference the ETFs that were passed in — no hallucinated tickers.
5. 2-3 sentences total (the spec's requirement).
6. Plain English — the user is not a finance major.
"""

SYSTEM_PROMPT = """You are a financial advisor assistant helping a non-expert user understand \
a portfolio recommendation from an automated system. Write in warm, clear, \
plain English — no jargon, no specific return predictions, no overconfident claims.

Rules you MUST follow:
- Write exactly 2-3 sentences.
- Only reference ETFs by the ticker and name that were provided to you. Never \
  invent or mention any fund that wasn't in the input list.
- Use hedged language: "may", "can help", "is generally suited for" — not "will" \
  or "guarantees".
- Do NOT cite specific return percentages or dollar figures.
- End your response with this exact disclaimer on a new line: \
  "This is not financial advice."
"""


def build_user_prompt(
    profile: dict,
    tier: str,
    top_factors: list[dict],
    etfs: list[dict],
) -> str:
    """
    Build the user message for Claude given the upstream layer outputs.

    Args:
        profile: The user's financial profile dict.
        tier: Risk tier from Layer 1 ('Low' | 'Medium' | 'High').
        top_factors: Top SHAP factors from Layer 1.
        etfs: ETF shortlist from Layer 3.

    Returns:
        A formatted user message string.
    """
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
- Investment horizon: {profile.get('investment_horizon_years')} years
- Experience level: {profile.get('investment_experience')}

KEY FACTORS (why the model picked this tier):
{factor_lines}

RECOMMENDED ETFs (these are the ONLY ones you may mention):
{etf_lines}

Write a 2-3 sentence explanation for the user.
"""

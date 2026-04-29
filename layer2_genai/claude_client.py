"""
Layer 2 · Claude API client.

OWNER: [TBD at kickoff]
BRANCH: layer2-genai

This is the one spot in the app where we call the Anthropic API.
Keep it isolated — don't sprinkle API calls across other files.

What you need to do:

1. Read ANTHROPIC_API_KEY from the environment.
2. Construct the Anthropic client.
3. Call client.messages.create() with the system + user prompts from prompts.py.
4. Post-check the response for hallucinated tickers (a ticker appeared that
   wasn't in the etfs list — this is a safety issue, flag it).
5. Return the text.

Stub behavior: returns a generic message so the app runs end-to-end before
the real API is wired up.
"""

import os

# TODO: from anthropic import Anthropic
from layer2_genai.prompts import SYSTEM_PROMPT, build_user_prompt


def generate_explanation(
    profile: dict,
    tier: str,
    top_factors: list[dict],
    etfs: list[dict],
) -> str:
    """
    Generate a 2-3 sentence plain-English explanation of the recommendation.

    Args:
        profile: The user's financial profile.
        tier: Risk tier from Layer 1.
        top_factors: Top SHAP factors from Layer 1.
        etfs: ETF shortlist from Layer 3.

    Returns:
        A 2-3 sentence explanation string, ending with the disclaimer.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")

    if not api_key:
        return (
            "⚠️ ANTHROPIC_API_KEY not set — showing stub response. "
            "Based on your profile, a diversified ETF portfolio aligned with "
            f"a {tier.lower()}-risk profile may be a reasonable starting point. "
            "This is not financial advice."
        )

    # TODO: client = Anthropic(api_key=api_key)
    # TODO: user_prompt = build_user_prompt(profile, tier, top_factors, etfs)
    # TODO: response = client.messages.create(
    #           model=model,
    #           max_tokens=200,
    #           system=SYSTEM_PROMPT,
    #           messages=[{"role": "user", "content": user_prompt}],
    #       )
    # TODO: text = response.content[0].text
    # TODO: safety check — scan for tickers not in etfs list, log warning if found
    # TODO: return text

    # --- STUB RESPONSE ---
    return (
        f"[STUB] Your profile was classified as {tier} risk, which may be "
        f"suitable for the recommended ETFs. Consider reviewing each fund "
        f"carefully before making a decision.\n\n"
        f"This is not financial advice."
    )

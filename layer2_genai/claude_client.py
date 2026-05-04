"""
Layer 2 · Claude API client.

BRANCH: layer2-genai

This is the one spot in the app where we call the Anthropic API.
Keep it isolated — don't sprinkle API calls across other files.

Falls back to a stub response when ANTHROPIC_API_KEY is not set, so the
app still runs end-to-end during development.
"""

import logging
import os
import re

from anthropic import Anthropic
from layer2_genai.prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


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

    client = Anthropic(api_key=api_key)
    user_prompt = build_user_prompt(profile, tier, top_factors, etfs)

    response = client.messages.create(
        model=model,
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = response.content[0].text

    # Safety check: flag any ticker symbols that weren't in the ETF list
    allowed_tickers = {etf.get("ticker", "").upper() for etf in etfs}
    mentioned_tickers = set(re.findall(r"\b[A-Z]{2,5}\b", text))
    # Filter to likely tickers by removing common English words
    common_words = {"THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
                    "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "MAY", "ETF",
                    "WITH", "HIS", "HOW", "ITS", "LET", "SAY", "SHE", "TOO",
                    "USE", "WAY", "WHO", "DID", "GET", "HAS", "HIM", "HAD",
                    "ANY", "NEW", "NOW", "OLD", "SEE", "TWO", "BOY", "OWN",
                    "ALSO", "BACK", "BEEN", "CALL", "COME", "EACH", "FIND",
                    "FROM", "GIVE", "HAVE", "HELP", "HERE", "HIGH", "JUST",
                    "KNOW", "LAST", "LIKE", "LINE", "LONG", "LOOK", "MADE",
                    "MAKE", "MANY", "MORE", "MOST", "MUCH", "MUST", "NAME",
                    "ONLY", "OVER", "PART", "SOME", "SUCH", "TAKE", "THAN",
                    "THAT", "THEM", "THEN", "THIS", "TIME", "VERY", "WHAT",
                    "WHEN", "WILL", "WITH", "WORD", "WORK", "YOUR", "RISK",
                    "LOW", "FUND", "FUNDS", "PORTFOLIO", "THESE"}
    mentioned_tickers -= common_words
    hallucinated = mentioned_tickers - allowed_tickers
    if hallucinated:
        logger.warning(
            "Claude mentioned tickers not in the ETF list: %s", hallucinated
        )

    return text

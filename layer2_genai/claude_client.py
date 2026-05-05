"""
Layer 2 — Claude API client
Autonomous Financial Advisor | MIS 02.303 | Spring 2026
"""

import os
import re
import anthropic
from .prompts import build_system_prompt, build_user_prompt


def generate_explanation(
    profile: dict,
    tier: str,
    top_factors: list,
    etfs: list[dict],
) -> str:
    """
    Calls Claude and returns a 2-3 sentence plain-English explanation.

    Args:
        profile:      investor profile dict from voice/keyboard input
        tier:         "Low" | "Medium" | "High"  (from Layer 1)
        top_factors:  SHAP factor list            (from Layer 1)
        etfs:         ETF list                    (from Layer 3)

    Returns:
        Explanation string with disclaimer, or safe fallback if API fails.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")

    if not api_key:
        return _safe_fallback(tier, etfs)

    client = anthropic.Anthropic(api_key=api_key)

    # Track allowed tickers for hallucination check
    allowed_tickers = {e.get("ticker", "").upper() for e in etfs}

    try:
        message = client.messages.create(
            model=model,
            max_tokens=300,
            system=build_system_prompt(),
            messages=[
                {"role": "user", "content": build_user_prompt(profile, tier, top_factors, etfs)}
            ],
        )
        explanation = message.content[0].text.strip()

        # Block hallucinated tickers before returning
        return _check_for_hallucinated_tickers(explanation, allowed_tickers)

    except Exception as e:
        print(f"[Layer2] API error: {e}")
        return _safe_fallback(tier, etfs)


def _check_for_hallucinated_tickers(text: str, allowed_tickers: set) -> str:
    """
    Scans for ticker-like tokens (2-5 uppercase letters).
    Blocks the response if any unrecognized ticker is found.
    """
    noise = {"ETF", "ETFS", "US", "AI", "OK", "A", "I",
             "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
             "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "MAY",
             "WITH", "HIS", "HOW", "ITS", "LET", "SAY", "SHE", "TOO",
             "USE", "WAY", "WHO", "DID", "GET", "HAS", "HIM", "HAD",
             "ANY", "NEW", "NOW", "OLD", "SEE", "TWO", "BOY", "OWN",
             "ALSO", "BACK", "BEEN", "CALL", "COME", "EACH", "FIND",
             "FROM", "GIVE", "HAVE", "HELP", "HERE", "HIGH", "JUST",
             "KNOW", "LAST", "LIKE", "LINE", "LONG", "LOOK", "MADE",
             "MAKE", "MANY", "MORE", "MOST", "MUCH", "MUST", "NAME",
             "ONLY", "OVER", "PART", "SOME", "SUCH", "TAKE", "THAN",
             "THAT", "THEM", "THEN", "THIS", "TIME", "VERY", "WHAT",
             "WHEN", "WILL", "WORD", "WORK", "YOUR", "RISK",
             "LOW", "FUND", "FUNDS", "PORTFOLIO", "THESE"}
    found = set(re.findall(r"\b[A-Z]{2,5}\b", text)) - noise
    hallucinated = found - allowed_tickers

    if hallucinated:
        print(f"[Layer2] ⚠️ Hallucinated tickers blocked: {hallucinated}")
        return (
            "[Explanation unavailable — an unverified fund name was detected. "
            "Please review the recommended funds listed above directly. "
            "This is not financial advice — please consult a licensed financial "
            "professional before making investment decisions.]"
        )
    return text


def _safe_fallback(tier: str, etfs: list[dict]) -> str:
    """Pre-written guardrail-safe fallback used when the API is unreachable."""
    names = [e.get("name", e.get("ticker", "the recommended funds")) for e in etfs[:2]]
    names_str = " and ".join(names) if names else "the recommended funds"

    phrases = {
        "Low":    "a conservative approach focused on stability",
        "Medium": "a balanced approach between growth and stability",
        "High":   "a growth-oriented approach that accepts higher short-term variability",
    }
    approach = phrases.get(tier, "an approach suited to your profile")

    return (
        f"Based on your profile, your risk tier is {tier}, suggesting {approach}. "
        f"The recommended funds — including {names_str} — reflect this assessment "
        f"and were selected to align with your financial situation and goals. "
        f"This is not financial advice — please consult a licensed financial professional "
        f"before making investment decisions."
    )

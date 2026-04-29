"""
Voice · Parse structured profile fields from a free-form transcript.

OWNER: [TBD at kickoff]
BRANCH: voice-ux

When the user speaks "I'm 28, make about 70k, save around 10%, have some
student loans, investing for retirement in maybe 30 years, I'm a beginner",
we need to turn that into:

{
    "age": 28,
    "annual_income_usd": 70000,
    "savings_rate_pct": 10.0,
    "debt_to_income_ratio": 0.3,  # inferred from "some student loans"
    "investment_horizon_years": 30,
    "investment_experience": "Beginner",
}

Two approaches — pick whichever your group prefers:

APPROACH A (simple, regex-based): works for predictable phrasings, cheap,
no extra API call. Fragile on unusual phrasings.

APPROACH B (LLM-based): send the transcript to Claude with instructions
to return JSON. More robust, costs ~1 extra API call per user input.

Recommendation: start with Approach A for demo reliability. Layer on
Approach B as fallback if the regex misses required fields.
"""

import re


REQUIRED_FIELDS = [
    "age",
    "annual_income_usd",
    "savings_rate_pct",
    "debt_to_income_ratio",
    "investment_horizon_years",
    "investment_experience",
]


def parse_profile_from_transcript(transcript: str) -> tuple[dict, list[str]]:
    """
    Extract structured profile fields from a free-form voice transcript.

    Args:
        transcript: What the user said, e.g. "I'm 28 and make 70k a year..."

    Returns:
        (profile_dict, missing_fields) — profile contains whatever could
        be extracted; missing_fields lists any REQUIRED_FIELDS we didn't
        find, so the caller can re-prompt.
    """
    text = transcript.lower()
    profile = {}

    # Age — "I'm 28" or "age 28" or "28 years old"
    age_match = re.search(r"(?:i['']?m|i am|age|i['']?m age)\s+(\d{2})\b", text)
    if not age_match:
        age_match = re.search(r"\b(\d{2})\s+years?\s+old\b", text)
    if age_match:
        age = int(age_match.group(1))
        if 18 <= age <= 100:
            profile["age"] = age

    # Income — "70k", "$70,000", "seventy thousand", "make 70000"
    income = _extract_income(text)
    if income is not None:
        profile["annual_income_usd"] = income

    # Savings rate — "save 10%", "saving around 10 percent"
    savings_match = re.search(r"sav\w*\s+(?:about|around|roughly)?\s*(\d+(?:\.\d+)?)\s*(?:%|percent)", text)
    if savings_match:
        profile["savings_rate_pct"] = float(savings_match.group(1))

    # Investment horizon — "30 years", "retirement in 30 years", "for 10 years"
    horizon_match = re.search(r"(?:in|for|over)?\s*(\d{1,2})\s*years?\s+(?:of|until|to|for)?", text)
    if not horizon_match:
        horizon_match = re.search(r"retirement.{0,30}?(\d{1,2})\s*years?", text)
    if horizon_match:
        horizon = int(horizon_match.group(1))
        if 1 <= horizon <= 50:
            profile["investment_horizon_years"] = horizon

    # Investment experience
    if re.search(r"\b(beginner|new to|just starting|novice)\b", text):
        profile["investment_experience"] = "Beginner"
    elif re.search(r"\b(intermediate|some experience|a few years)\b", text):
        profile["investment_experience"] = "Intermediate"
    elif re.search(r"\b(advanced|experienced|expert|many years)\b", text):
        profile["investment_experience"] = "Advanced"

    # Debt-to-income — qualitative heuristic
    # TODO: ask user directly if this isn't in the transcript;
    #       for now, infer from keywords
    if re.search(r"\b(no debt|debt[- ]free)\b", text):
        profile["debt_to_income_ratio"] = 0.0
    elif re.search(r"\b(heavy debt|lots of debt|a lot of debt|drowning in debt)\b", text):
        profile["debt_to_income_ratio"] = 0.6
    elif re.search(r"\b(some debt|student loans?|car loans?|mortgages?|credit card)\b", text):
        profile["debt_to_income_ratio"] = 0.3
    elif re.search(r"\b(little debt|small amount of debt)\b", text):
        profile["debt_to_income_ratio"] = 0.15

    missing = [f for f in REQUIRED_FIELDS if f not in profile]
    return profile, missing


def _extract_income(text: str) -> int | None:
    """Try a few common ways of stating income."""
    # "70k", "$70k", "70K"
    match = re.search(r"\$?\s*(\d{2,3})\s*k\b", text)
    if match:
        return int(match.group(1)) * 1000

    # "$70,000", "70000", "seventy thousand"
    match = re.search(r"\$?\s*(\d{2,3}[,.]?\d{3})\b", text)
    if match:
        num_str = match.group(1).replace(",", "").replace(".", "")
        val = int(num_str)
        if 10_000 <= val <= 10_000_000:
            return val

    return None

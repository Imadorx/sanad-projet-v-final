# -*- coding: utf-8 -*-
"""Output safety enforcement.

Even with a strict system prompt (services/ai_provider.py), an LLM can
still occasionally drift into diagnostic or prescriptive language. This
module is the second, independent layer of enforcement: every AI
response is scanned before being returned to the user, and if it trips
a diagnostic/prescriptive pattern, the response is BLOCKED entirely
(never partially shown) and status='blocked' is what gets logged to
sanad.ai.log - not the unsafe text itself.

This is intentionally pattern-based and conservative (may over-block
occasionally) rather than trying to be a clever classifier - for a
hard safety constraint like "never diagnose", false positives (an
overly cautious block) are the acceptable failure mode, not false
negatives.
"""
import re

# Patterns suggesting the model is diagnosing, prescribing, or directing
# a course of medical action - checked case-insensitively.
BLOCKED_PATTERNS = [
    r'\byou (?:have|are suffering from|likely have|probably have)\b.{0,40}\b(disease|condition|syndrome|infection|cancer|diabetes|disorder)\b',
    r'\bi diagnose\b',
    r'\byour diagnosis is\b',
    r'\byou should take\b',
    r'\bi (?:recommend|suggest|prescribe)\b.{0,40}\b(mg|dose|dosage|tablet|pill|medication|drug)\b',
    r'\btake \d+\s?(mg|ml|mcg)\b',
    r'\bstop taking\b',
    r'\bincrease your dose\b',
    r'\bdecrease your dose\b',
    r'\byou do not need to see a doctor\b',
    r'\byou don\'t need a doctor\b',
]
_COMPILED = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]

DISCLAIMER = (
    "\n\n---\nThis information is educational only and is not a "
    "diagnosis or medical advice. Please consult your doctor or another "
    "qualified healthcare professional for any medical decisions."
)


def check_response_safety(text):
    """Returns (is_safe: bool, matched_pattern: str|None)."""
    if not text:
        return True, None
    for pattern in _COMPILED:
        if pattern.search(text):
            return False, pattern.pattern
    return True, None


def finalize_response(text):
    """Appends the mandatory educational disclaimer (PRD 15.3: 'ALWAYS
    mention that information is educational / encourage consultation
    with professionals') to a response that has already passed the
    safety check."""
    if DISCLAIMER.strip() in text:
        return text
    return text + DISCLAIMER

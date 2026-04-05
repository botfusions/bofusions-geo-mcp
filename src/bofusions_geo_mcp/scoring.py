"""Citability scoring engine — scores content blocks for AI citation readiness.

Based on research showing optimal AI-cited passages are:
- 134-167 words long
- Self-contained (extractable without context)
- Fact-rich with specific statistics
- Structured with clear answer patterns
"""

from __future__ import annotations

import re
from typing import Any


def score_passage(text: str, heading: str | None = None) -> dict[str, Any]:
    """Score a single passage for AI citability (0-100)."""
    words = text.split()
    word_count = len(words)

    scores = {
        "answer_block_quality": 0,
        "self_containment": 0,
        "structural_readability": 0,
        "statistical_density": 0,
        "uniqueness_signals": 0,
    }

    # === 1. Answer Block Quality (30%) ===
    abq = 0
    definition_patterns = [
        r"\b\w+\s+is\s+(?:a|an|the)\s",
        r"\b\w+\s+refers?\s+to\s",
        r"\b\w+\s+means?\s",
        r"\b\w+\s+(?:can be |are )?defined\s+as\s",
        r"\bin\s+(?:simple|other)\s+(?:terms|words)\s*,",
    ]
    for pat in definition_patterns:
        if re.search(pat, text, re.IGNORECASE):
            abq += 15
            break

    first_60 = " ".join(words[:60])
    if any(re.search(p, first_60, re.IGNORECASE) for p in [
        r"\b(?:is|are|was|were|means?|refers?)\b",
        r"\d+%", r"\$[\d,]+", r"\d+\s+(?:million|billion|thousand)",
    ]):
        abq += 15

    if heading and heading.endswith("?"):
        abq += 10

    sentences = re.split(r"[.!?]+", text)
    short_clear = sum(1 for s in sentences if 5 <= len(s.split()) <= 25)
    if sentences:
        abq += int((short_clear / len(sentences)) * 10)

    if re.search(
        r"(?:according to|research shows|studies? (?:show|indicate|suggest|found)|data (?:shows|indicates|suggests))",
        text, re.IGNORECASE,
    ):
        abq += 10

    scores["answer_block_quality"] = min(abq, 30)

    # === 2. Self-Containment (25%) ===
    sc = 0
    if 134 <= word_count <= 167:
        sc += 10
    elif 100 <= word_count <= 200:
        sc += 7
    elif 80 <= word_count <= 250:
        sc += 4
    elif 30 <= word_count < 80 or 250 < word_count <= 400:
        sc += 2

    if word_count > 0:
        pronouns = re.findall(
            r"\b(?:it|they|them|their|this|that|these|those|he|she|his|her)\b",
            text, re.IGNORECASE,
        )
        ratio = len(pronouns) / word_count
        if ratio < 0.02:
            sc += 8
        elif ratio < 0.04:
            sc += 5
        elif ratio < 0.06:
            sc += 3

    proper_nouns = len(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text))
    sc += 7 if proper_nouns >= 3 else (4 if proper_nouns >= 1 else 0)

    scores["self_containment"] = min(sc, 25)

    # === 3. Structural Readability (20%) ===
    sr = 0
    if sentences:
        avg_len = word_count / len(sentences)
        if 10 <= avg_len <= 20:
            sr += 8
        elif 8 <= avg_len <= 25:
            sr += 5
        else:
            sr += 2

    if re.search(r"(?:first|second|third|finally|additionally|moreover|furthermore)", text, re.IGNORECASE):
        sr += 4
    if re.search(r"(?:\d+[\.\)]\s|\b(?:step|tip|point)\s+\d+)", text, re.IGNORECASE):
        sr += 4
    if "\n" in text:
        sr += 4

    scores["structural_readability"] = min(sr, 20)

    # === 4. Statistical Density (15%) ===
    sd = 0
    sd += min(len(re.findall(r"\d+(?:\.\d+)?%", text)) * 3, 6)
    sd += min(len(re.findall(r"\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|M|B|K))?", text)) * 3, 5)
    sd += min(len(re.findall(
        r"\b\d+(?:,\d{3})*(?:\.\d+)?\s+(?:users|customers|pages|sites|companies|businesses|people|percent|times|x\b)",
        text, re.IGNORECASE,
    )) * 2, 4)

    if re.search(r"\b20(?:2[3-6]|1\d)\b", text):
        sd += 2

    for pat in [
        r"(?:according to|per|from|by)\s+[A-Z]",
        r"(?:Gartner|Forrester|McKinsey|Harvard|Stanford|MIT|Google|Microsoft|OpenAI|Anthropic)",
        r"\([A-Z][a-z]+(?:\s+\d{4})?\)",
    ]:
        if re.search(pat, text):
            sd += 2

    scores["statistical_density"] = min(sd, 15)

    # === 5. Uniqueness Signals (10%) ===
    us = 0
    if re.search(
        r"(?:our (?:research|study|data|analysis|survey|findings)|we (?:found|discovered|analyzed|surveyed|measured))",
        text, re.IGNORECASE,
    ):
        us += 5
    if re.search(r"(?:case study|for example|for instance|in practice|real-world|hands-on)", text, re.IGNORECASE):
        us += 3
    if re.search(r"(?:using|with|via|through)\s+[A-Z][a-z]+", text):
        us += 2

    scores["uniqueness_signals"] = min(us, 10)

    # === Total & Grade ===
    total = sum(scores.values())

    if total >= 80:
        grade, label = "A", "Highly Citable"
    elif total >= 65:
        grade, label = "B", "Good Citability"
    elif total >= 50:
        grade, label = "C", "Moderate Citability"
    elif total >= 35:
        grade, label = "D", "Low Citability"
    else:
        grade, label = "F", "Poor Citability"

    return {
        "heading": heading,
        "word_count": word_count,
        "total_score": total,
        "grade": grade,
        "label": label,
        "breakdown": scores,
        "preview": " ".join(words[:30]) + ("..." if word_count > 30 else ""),
    }


def calculate_geo_score(
    citability_avg: float,
    brand_score: float,
    content_score: float,
    technical_score: float,
    schema_score: float,
    platform_score: float,
) -> dict[str, Any]:
    """Calculate overall GEO score (0-100) with weighted components."""
    weights = {
        "ai_citability": (0.25, citability_avg),
        "brand_authority": (0.20, brand_score),
        "content_quality": (0.20, content_score),
        "technical": (0.15, technical_score),
        "schema": (0.10, schema_score),
        "platform": (0.10, platform_score),
    }

    total = sum(weight * score for weight, score in weights.values())

    if total >= 80:
        grade = "A"
    elif total >= 65:
        grade = "B"
    elif total >= 50:
        grade = "C"
    elif total >= 35:
        grade = "D"
    else:
        grade = "F"

    return {
        "total_score": round(total, 1),
        "grade": grade,
        "components": {name: {"weight": w, "score": round(s, 1), "weighted": round(w * s, 1)} for name, (w, s) in weights.items()},
    }

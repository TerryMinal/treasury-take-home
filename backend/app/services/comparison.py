"""Text comparison and reviewer-reason helpers for checklist evaluation."""

from __future__ import annotations

import re
import unicodedata

from app.core.constants import GOVERNMENT_WARNING_TEXT


def normalize_text(value: str | None) -> str | None:
    """Normalize ordinary text for tolerant comparisons."""

    if value is None:
        return None

    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.casefold()
    normalized = re.sub(r"[’'`]", "", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized or None


def normalize_abv(value: str | None) -> str | None:
    """Normalize ABV expressions so proof and percent can be compared loosely."""

    if value is None:
        return None

    match = re.search(r"(\d+(?:\.\d+)?)\s*%", value)
    if match:
        return match.group(1).rstrip("0").rstrip(".")

    proof_match = re.search(r"(\d+(?:\.\d+)?)\s*proof", value, re.IGNORECASE)
    if proof_match:
        proof = float(proof_match.group(1))
        return f"{proof / 2:g}"

    return normalize_text(value)


def normalize_net_contents(value: str | None) -> str | None:
    """Normalize common net-content expressions."""

    if value is None:
        return None

    compact = value.casefold().replace("milliliters", "ml").replace("milliliter", "ml")
    compact = compact.replace("liters", "l").replace("liter", "l")
    compact = re.sub(r"\s+", "", compact)
    return compact or None


def warning_matches_exactly(value: str | None) -> bool:
    """Return whether a label warning matches the mandated text exactly."""

    return (value or "").strip() == GOVERNMENT_WARNING_TEXT


def dedupe_review_reasons(reasons: list[str]) -> list[str]:
    """Preserve order while removing duplicate human-review reasons."""

    seen: set[str] = set()
    result: list[str] = []
    for reason in reasons:
        if not reason or reason in seen:
            continue
        seen.add(reason)
        result.append(reason)
    return result

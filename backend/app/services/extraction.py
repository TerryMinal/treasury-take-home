"""OCR text extraction helpers.

The prototype keeps field extraction intentionally lightweight and
explainable. Regex-based heuristics are easy to reason about and can be
replaced later without changing the API contract.
"""

from __future__ import annotations

import re

from app.core.constants import GOVERNMENT_WARNING_TEXT
from app.models.schemas import ApplicationData


def extract_application_fields(ocr_text: str) -> ApplicationData:
    """Extract candidate application fields from OCR text."""
    normalized_text = " ".join(ocr_text.split())

    return ApplicationData(
        brand_name=_find_brand_name(ocr_text),
        class_type=_find_class_type(normalized_text),
        abv=_find_abv(normalized_text),
        net_contents=_find_net_contents(normalized_text),
        producer=_find_producer(normalized_text),
        country_of_origin=_find_country_of_origin(normalized_text),
        government_warning=_find_warning(ocr_text),
    )


def _find_brand_name(ocr_text: str) -> str | None:
    lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
    if not lines:
        return None

    for line in lines:
        cleaned = re.sub(r"[^A-Za-z0-9 '&.-]", "", line).strip()
        if len(cleaned) >= 4 and cleaned.upper() == cleaned and len(cleaned.split()) <= 6:
            return cleaned
    return lines[0]


def _find_class_type(text: str) -> str | None:
    pattern = re.compile(
        r"\b("
        r"kentucky straight bourbon whiskey|straight bourbon whiskey|bourbon whiskey|"
        r"rye whiskey|whiskey|vodka|rum|gin|tequila|mezcal|wine|beer|lager|ale"
        r")\b",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    return match.group(1) if match else None


def _find_abv(text: str) -> str | None:
    percent_match = re.search(r"\b\d+(?:\.\d+)?\s*%\s*(?:alc\.?/?vol\.?)?", text, re.IGNORECASE)
    if percent_match:
        proof_match = re.search(r"\(\s*\d+(?:\.\d+)?\s*proof\s*\)", text, re.IGNORECASE)
        if proof_match:
            return f"{percent_match.group(0).strip()} {proof_match.group(0).strip()}"
        return percent_match.group(0).strip()

    proof_match = re.search(r"\b\d+(?:\.\d+)?\s*proof\b", text, re.IGNORECASE)
    return proof_match.group(0).strip() if proof_match else None


def _find_net_contents(text: str) -> str | None:
    match = re.search(r"\b\d+(?:\.\d+)?\s*(?:ml|mL|l|L|fl\.?\s*oz\.?)\b", text, re.IGNORECASE)
    return match.group(0).strip() if match else None


def _find_producer(text: str) -> str | None:
    match = re.search(
        r"\b(?:bottled by|produced by|distilled by|imported by)\s+([^.;]+)",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None
    return match.group(0).strip()


def _find_country_of_origin(text: str) -> str | None:
    match = re.search(r"\b(?:product of|imported from|country of origin)\s+([^.;]+)", text, re.IGNORECASE)
    if not match:
        return None
    return match.group(0).strip()


def _find_warning(text: str) -> str | None:
    exact_index = text.find("GOVERNMENT WARNING:")
    if exact_index >= 0:
        return text[exact_index : exact_index + len(GOVERNMENT_WARNING_TEXT)]

    case_insensitive = re.search(r"government warning:.*", text, re.IGNORECASE | re.DOTALL)
    if case_insensitive:
        return " ".join(case_insensitive.group(0).split())[: len(GOVERNMENT_WARNING_TEXT) + 40].strip()
    return None

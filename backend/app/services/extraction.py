"""OCR text extraction and beverage-type detection helpers."""

from __future__ import annotations

import re

from app.core.constants import GOVERNMENT_WARNING_TEXT
from app.models.schemas import BeverageType, ExtractedLabelData

_WINE_KEYWORDS = (
    "wine",
    "chardonnay",
    "cabernet",
    "merlot",
    "pinot",
    "sauvignon",
    "riesling",
    "zinfandel",
    "rose",
    "sparkling",
)
_DISTILLED_KEYWORDS = (
    "vodka",
    "whiskey",
    "whisky",
    "bourbon",
    "rum",
    "gin",
    "tequila",
    "mezcal",
    "brandy",
    "liqueur",
    "distilled",
)
_MALT_KEYWORDS = (
    "beer",
    "ale",
    "lager",
    "stout",
    "porter",
    "ipa",
    "india pale ale",
    "malt beverage",
    "pilsner",
)
_WINE_VARIETALS = (
    "chardonnay",
    "cabernet sauvignon",
    "pinot noir",
    "pinot grigio",
    "merlot",
    "riesling",
    "sauvignon blanc",
    "zinfandel",
    "syrah",
)


def detect_beverage_type(ocr_text: str) -> tuple[BeverageType | None, str | None]:
    """Infer the beverage type from OCR text using conservative keyword scoring."""

    normalized = " ".join(ocr_text.casefold().split())
    scores = {
        BeverageType.WINE: _keyword_score(normalized, _WINE_KEYWORDS),
        BeverageType.DISTILLED_SPIRITS: _keyword_score(normalized, _DISTILLED_KEYWORDS),
        BeverageType.MALT_BEVERAGE: _keyword_score(normalized, _MALT_KEYWORDS),
    }

    top_type = max(scores, key=scores.get)
    top_score = scores[top_type]
    sorted_scores = sorted(scores.values(), reverse=True)
    second_score = sorted_scores[1]

    if top_score == 0:
        return None, "Beverage type could not be determined confidently from the label text."
    if top_score == second_score:
        return None, "Beverage type could not be determined confidently because the label matched multiple beverage families."

    return top_type, f"Beverage type was inferred from label terms associated with {top_type.value.replace('_', ' ')}."


def extract_label_data(ocr_text: str, beverage_type: BeverageType | None) -> ExtractedLabelData:
    """Extract structured label evidence from OCR text."""

    normalized_text = " ".join(ocr_text.split())
    excerpt = normalized_text[:500] if normalized_text else None

    return ExtractedLabelData(
        brand_name=_find_brand_name(ocr_text),
        designation=_find_designation(normalized_text, beverage_type),
        alcohol_content=_find_alcohol_content(normalized_text),
        net_contents=_find_net_contents(normalized_text),
        name_and_address=_find_name_and_address(normalized_text),
        government_warning=_find_warning(ocr_text),
        country_of_origin=_find_country_of_origin(normalized_text),
        appellation_of_origin=_find_appellation_of_origin(normalized_text),
        sulfite_declaration=_find_phrase(normalized_text, r"contains sulfites"),
        yellow_5_declaration=_find_phrase(normalized_text, r"contains fd&c yellow #5"),
        cochineal_or_carmine_declaration=_find_phrase(normalized_text, r"contains (?:cochineal extract|carmine)"),
        aspartame_declaration=_find_phrase(normalized_text, r"phenylketonurics:\s*contains phenylalanine"),
        coloring_statement=_find_phrase(normalized_text, r"(?:artificially colored|certified color added|colored with [^.;]+)"),
        treatment_with_wood_statement=_find_phrase(normalized_text, r"colored and flavored with wood[^.;]*"),
        commodity_statement=_find_phrase(
            normalized_text,
            r"(?:\d+%\s*neutral spirits distilled from [^.;]+|distilled from [^.;]+)",
        ),
        state_of_distillation=_find_phrase(normalized_text, r"distilled in [^.;]+"),
        age_statement=_find_phrase(
            normalized_text,
            r"(?:\b\d+\s+years?\s+old\b|aged\s+(?:at least\s+)?\d+\s+(?:years?|months?))",
        ),
        is_imported=_infer_import_status(normalized_text),
        raw_text_excerpt=excerpt,
    )


def _keyword_score(text: str, keywords: tuple[str, ...]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def _find_brand_name(ocr_text: str) -> str | None:
    lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
    for line in lines:
        if "government warning" in line.casefold():
            continue
        cleaned = re.sub(r"[^A-Za-z0-9 '&./()-]", "", line).strip()
        if len(cleaned) >= 4 and cleaned.upper() == cleaned and len(cleaned.split()) <= 8:
            return cleaned
    return lines[0] if lines else None


def _find_designation(text: str, beverage_type: BeverageType | None) -> str | None:
    patterns: dict[BeverageType, str] = {
        BeverageType.WINE: r"\b(?:red wine|white wine|sparkling wine|peach wine|honey wine|chardonnay|merlot|cabernet sauvignon|pinot noir|pinot grigio|riesling|sauvignon blanc)\b",
        BeverageType.DISTILLED_SPIRITS: r"\b(?:kentucky straight bourbon whiskey|straight bourbon whiskey|bourbon whiskey|rye whiskey|vodka|whiskey|whisky|rum|gin|tequila|mezcal|brandy|liqueur|ouzo)\b",
        BeverageType.MALT_BEVERAGE: r"\b(?:malt beverage|beer|ale|india pale ale|ipa|lager|stout|porter|pilsner)\b",
    }
    if beverage_type and beverage_type in patterns:
        match = re.search(patterns[beverage_type], text, re.IGNORECASE)
        if match:
            return match.group(0)

    fallback = re.search(r"\b(?:wine|vodka|whiskey|whisky|bourbon|rum|gin|tequila|beer|ale|lager|stout|ipa)\b", text, re.IGNORECASE)
    return fallback.group(0) if fallback else None


def _find_alcohol_content(text: str) -> str | None:
    percent_match = re.search(r"\b\d+(?:\.\d+)?\s*%\s*(?:alc\.?/?vol\.?)?", text, re.IGNORECASE)
    if percent_match:
        proof_match = re.search(r"\(\s*\d+(?:\.\d+)?\s*proof\s*\)", text, re.IGNORECASE)
        if proof_match:
            return f"{percent_match.group(0).strip()} {proof_match.group(0).strip()}"
        return percent_match.group(0).strip()

    proof_match = re.search(r"\b\d+(?:\.\d+)?\s*proof\b", text, re.IGNORECASE)
    return proof_match.group(0).strip() if proof_match else None


def _find_net_contents(text: str) -> str | None:
    match = re.search(r"\b\d+(?:\.\d+)?\s*(?:ml|mL|l|L|fl\.?\s*oz\.?|pints?|quarts?|gallons?)\b", text, re.IGNORECASE)
    return match.group(0).strip() if match else None


def _find_name_and_address(text: str) -> str | None:
    match = re.search(
        r"\b(?:bottled by|produced by|distilled by|imported by|distributed by)\s+([^.;]+)",
        text,
        re.IGNORECASE,
    )
    return match.group(0).strip() if match else None


def _find_warning(text: str) -> str | None:
    exact_index = text.find("GOVERNMENT WARNING:")
    if exact_index >= 0:
        return " ".join(text[exact_index : exact_index + len(GOVERNMENT_WARNING_TEXT)].split())

    case_insensitive = re.search(r"government warning:.*", text, re.IGNORECASE | re.DOTALL)
    if case_insensitive:
        return " ".join(case_insensitive.group(0).split())[: len(GOVERNMENT_WARNING_TEXT) + 60].strip()
    return None


def _find_country_of_origin(text: str) -> str | None:
    match = re.search(r"\b(?:product of|imported from|country of origin)\s+([^.;]+)", text, re.IGNORECASE)
    return match.group(0).strip() if match else None


def _find_appellation_of_origin(text: str) -> str | None:
    match = re.search(
        r"\b(?:napa valley|sonoma county|california|oregon|washington state|columbia valley|willamette valley|product of [^.;]+)\b",
        text,
        re.IGNORECASE,
    )
    return match.group(0).strip() if match else None


def _find_phrase(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0).strip() if match else None


def _infer_import_status(text: str) -> bool | None:
    if re.search(r"\b(imported by|imported from|product of)\b", text, re.IGNORECASE):
        return True
    if re.search(r"\b(bottled by|produced by|distilled by)\b", text, re.IGNORECASE):
        return False
    return None


def wine_appellation_required(text: str) -> bool:
    """Determine whether the wine checklist should require an appellation review."""

    lowered = text.casefold()
    if "estate bottled" in lowered:
        return True
    if re.search(r"\b(?:19|20)\d{2}\b", lowered):
        return True
    return any(varietal in lowered for varietal in _WINE_VARIETALS)

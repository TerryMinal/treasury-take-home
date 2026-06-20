"""Field comparison helpers.

Ordinary fields use tolerant normalization so reviewers are not flooded
with noisy mismatches for harmless punctuation or case differences.
The government warning remains strict and exact.
"""

from __future__ import annotations

import re
import unicodedata

from app.core.constants import FIELD_DISPLAY_NAMES, GOVERNMENT_WARNING_TEXT
from app.models.schemas import FieldReview, ReviewField, ReviewStatus


def normalize_text(value: str | None) -> str | None:
    """Normalize ordinary text for tolerant field comparison."""
    if value is None:
        return None

    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.casefold()
    normalized = re.sub(r"[’'`]", "", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized or None


def normalize_abv(value: str | None) -> str | None:
    """Normalize ABV expressions to a comparable percentage value when possible."""
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


def compare_field(field: ReviewField, application_value: str | None, extracted_value: str | None) -> FieldReview:
    """Compare a single field according to its business rules."""
    if field == ReviewField.GOVERNMENT_WARNING:
        return compare_warning(application_value, extracted_value)

    if not application_value and not extracted_value:
        status = ReviewStatus.UNCERTAIN
        explanation = "Neither the application nor the label provided a usable value."
        normalized_application = None
        normalized_extracted = None
    elif not application_value:
        status = ReviewStatus.MISSING_APPLICATION
        explanation = "The application did not provide a value for this field."
        normalized_application = None
        normalized_extracted = _normalize_for_field(field, extracted_value)
    elif not extracted_value:
        status = ReviewStatus.MISSING_LABEL
        explanation = "The label text did not produce a usable value for this field."
        normalized_application = _normalize_for_field(field, application_value)
        normalized_extracted = None
    else:
        normalized_application = _normalize_for_field(field, application_value)
        normalized_extracted = _normalize_for_field(field, extracted_value)
        if normalized_application == normalized_extracted:
            status = ReviewStatus.MATCH
            explanation = "The application and extracted label values align after normalization."
        else:
            status = ReviewStatus.MISMATCH
            explanation = "The application and extracted label values differ after normalization."

    return FieldReview(
        field=field,
        display_name=FIELD_DISPLAY_NAMES[field.value],
        application_value=application_value,
        extracted_value=extracted_value,
        normalized_application_value=normalized_application,
        normalized_extracted_value=normalized_extracted,
        status=status,
        explanation=explanation,
    )


def compare_warning(application_value: str | None, extracted_value: str | None) -> FieldReview:
    """Validate the government warning strictly and exactly."""
    expected_warning = application_value or GOVERNMENT_WARNING_TEXT

    if not extracted_value:
        status = ReviewStatus.MISSING_LABEL
        explanation = "The label did not yield a readable government warning statement."
    elif extracted_value.strip() == expected_warning.strip():
        status = ReviewStatus.MATCH
        explanation = "The label contains the exact expected government warning statement."
    else:
        status = ReviewStatus.MISMATCH
        explanation = "The government warning must match the expected wording and capitalization exactly."

    return FieldReview(
        field=ReviewField.GOVERNMENT_WARNING,
        display_name=FIELD_DISPLAY_NAMES[ReviewField.GOVERNMENT_WARNING.value],
        application_value=expected_warning,
        extracted_value=extracted_value,
        normalized_application_value=expected_warning,
        normalized_extracted_value=extracted_value,
        status=status,
        explanation=explanation,
    )


def overall_status(fields: list[FieldReview]) -> ReviewStatus:
    """Summarize field-level reviews into a single status."""
    statuses = {field.status for field in fields}
    if ReviewStatus.MISMATCH in statuses:
        return ReviewStatus.MISMATCH
    if ReviewStatus.UNCERTAIN in statuses or ReviewStatus.MISSING_LABEL in statuses:
        return ReviewStatus.UNCERTAIN
    if ReviewStatus.MISSING_APPLICATION in statuses:
        return ReviewStatus.UNCERTAIN
    return ReviewStatus.MATCH


def _normalize_for_field(field: ReviewField, value: str | None) -> str | None:
    if field == ReviewField.ABV:
        return normalize_abv(value)
    if field == ReviewField.NET_CONTENTS:
        return normalize_net_contents(value)
    return normalize_text(value)

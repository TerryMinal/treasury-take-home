"""Checklist review orchestration for single-item and batch processing."""

from __future__ import annotations

from uuid import uuid4

from app.core.constants import BEVERAGE_TYPE_LABELS
from app.models.schemas import (
    BatchJobResponse,
    BatchReviewItem,
    BeverageType,
    ChecklistItemResult,
    ExtractedLabelData,
    RequirementLevel,
    ReviewResponse,
    ReviewStatus,
    ReviewSummaryCounts,
)
from app.services.checklists import CHECKLISTS, ChecklistRule
from app.services.comparison import (
    dedupe_review_reasons,
    normalize_abv,
    normalize_net_contents,
    normalize_text,
    warning_matches_exactly,
)
from app.services.extraction import detect_beverage_type, extract_label_data, wine_appellation_required
from app.services.ocr import OCRInput, build_ocr_provider


class BatchJobStore:
    """In-memory batch store suitable for prototype scope."""

    def __init__(self) -> None:
        self._jobs: dict[str, BatchJobResponse] = {}

    def create_job(self, results: list[BatchReviewItem]) -> BatchJobResponse:
        job_id = str(uuid4())
        processed_count = sum(1 for item in results if item.status != "queued")
        status = "completed" if processed_count == len(results) else "processing"
        job = BatchJobResponse(
            job_id=job_id,
            status=status,
            item_count=len(results),
            processed_count=processed_count,
            results=results,
        )
        self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> BatchJobResponse | None:
        return self._jobs.get(job_id)


batch_job_store = BatchJobStore()


def review_label(filename: str, content_type: str, data: bytes) -> ReviewResponse:
    """Run OCR, extract evidence, choose a checklist, and evaluate one label."""

    ocr_input = OCRInput(filename=filename, content_type=content_type, data=data)
    ocr_provider = build_ocr_provider(ocr_input)
    ocr_result = ocr_provider.extract_text(ocr_input)

    beverage_type, beverage_type_reason = detect_beverage_type(ocr_result.text)
    extracted = extract_label_data(ocr_result.text, beverage_type)

    checklist_items = _evaluate_checklist(beverage_type, extracted, ocr_result.warnings)

    review_reasons = []
    if beverage_type_reason and beverage_type is None:
        review_reasons.append(beverage_type_reason)
    for warning in ocr_result.warnings:
        review_reasons.append(warning)
    for item in checklist_items:
        review_reasons.extend(item.review_reasons)
    review_reasons = dedupe_review_reasons(review_reasons)

    overall_status = ReviewStatus.REVIEW if review_reasons else ReviewStatus.PASS
    summary_counts = ReviewSummaryCounts(
        total=len(checklist_items),
        passed=sum(1 for item in checklist_items if item.status == ReviewStatus.PASS),
        review=sum(1 for item in checklist_items if item.status == ReviewStatus.REVIEW),
    )

    beverage_type_label = (
        BEVERAGE_TYPE_LABELS[beverage_type.value]
        if beverage_type is not None
        else "Needs Human Review"
    )

    summary = _build_summary(overall_status, beverage_type_label, summary_counts, review_reasons)
    return ReviewResponse(
        filename=filename,
        beverage_type=beverage_type,
        beverage_type_label=beverage_type_label,
        overall_status=overall_status,
        summary=summary,
        summary_counts=summary_counts,
        review_reasons=review_reasons,
        checklist_items=checklist_items,
        extracted=extracted,
        ocr=ocr_result,
    )


def build_batch_job(files: list[tuple[str, str, bytes]]) -> BatchJobResponse:
    """Process each batch item independently so one failure does not block the rest."""

    results: list[BatchReviewItem] = []
    for filename, content_type, data in files:
        try:
            result = review_label(filename, content_type, data)
            results.append(BatchReviewItem(filename=filename, status="completed", result=result))
        except Exception as exc:  # pragma: no cover - defensive safeguard
            results.append(
                BatchReviewItem(
                    filename=filename,
                    status="failed",
                    error=f"Processing failed for this label: {exc}",
                )
            )
    return batch_job_store.create_job(results)


def _evaluate_checklist(
    beverage_type: BeverageType | None,
    extracted: ExtractedLabelData,
    ocr_warnings: list[str],
) -> list[ChecklistItemResult]:
    if beverage_type is None:
        return [
            ChecklistItemResult(
                id="beverage_type",
                label="Beverage Type",
                section="Classification",
                requirement_level=RequirementLevel.REQUIRED,
                evaluation_type="beverage_type_detection",
                status=ReviewStatus.REVIEW,
                explanation="The label could not be matched confidently to the wine, distilled spirits, or malt beverage checklist.",
                review_reasons=["Beverage type could not be determined confidently"],
                evidence_text=extracted.raw_text_excerpt,
            )
        ]

    items: list[ChecklistItemResult] = []
    for rule in CHECKLISTS[beverage_type]:
        items.append(_evaluate_rule(rule, beverage_type, extracted, ocr_warnings))
    return items


def _evaluate_rule(
    rule: ChecklistRule,
    beverage_type: BeverageType,
    extracted: ExtractedLabelData,
    ocr_warnings: list[str],
) -> ChecklistItemResult:
    if rule.id == "brand_name":
        return _presence_rule(rule, extracted.brand_name, "Brand name was detected on the label.", "Brand name could not be read from the image")
    if rule.id == "designation":
        return _presence_rule(rule, extracted.designation, "Designation was detected on the label.", "Class or type designation could not be read from the image")
    if rule.id == "alcohol_content":
        if beverage_type == BeverageType.MALT_BEVERAGE and extracted.alcohol_content is None:
            return _conditional_pass(rule, "Alcohol content was not detected. This disclosure is only mandatory for certain malt beverages or where state law requires it.")
        return _presence_rule(rule, extracted.alcohol_content, "Alcohol content was detected on the label.", "Alcohol content could not be read from the image")
    if rule.id == "net_contents":
        return _presence_rule(rule, extracted.net_contents, "Net contents were detected on the label.", "Net contents could not be read from the image")
    if rule.id == "name_and_address":
        return _presence_rule(rule, extracted.name_and_address, "Name and address were detected on the label.", "Name and address could not be read from the image")
    if rule.id == "government_warning":
        return _warning_rule(rule, extracted.government_warning)
    if rule.id == "country_of_origin":
        return _country_of_origin_rule(rule, extracted)
    if rule.id == "importer_name_and_address":
        return _importer_rule(rule, extracted)
    if rule.id == "appellation_of_origin":
        return _appellation_rule(rule, extracted)
    if rule.id == "same_field_of_vision":
        return ChecklistItemResult(
            id=rule.id,
            label=rule.label,
            section=rule.section,
            requirement_level=rule.requirement_level,
            evaluation_type=rule.evaluation_type,
            status=ReviewStatus.REVIEW,
            explanation="The distilled-spirits checklist requires brand name, designation, and alcohol content to appear in the same field of vision, which this MVP cannot verify reliably from OCR alone.",
            review_reasons=["This rule depends on label layout and needs human confirmation"],
            evidence_text=_join_evidence(extracted.brand_name, extracted.designation, extracted.alcohol_content),
        )

    disclosures = {
        "sulfite_declaration": extracted.sulfite_declaration,
        "yellow_5_declaration": extracted.yellow_5_declaration,
        "cochineal_or_carmine_declaration": extracted.cochineal_or_carmine_declaration,
        "aspartame_declaration": extracted.aspartame_declaration,
        "coloring_statement": extracted.coloring_statement,
        "treatment_with_wood_statement": extracted.treatment_with_wood_statement,
        "commodity_statement": extracted.commodity_statement,
        "state_of_distillation": extracted.state_of_distillation,
        "age_statement": extracted.age_statement,
    }
    if rule.id in disclosures:
        return _conditional_disclosure_rule(rule, disclosures[rule.id], ocr_warnings)

    return ChecklistItemResult(
        id=rule.id,
        label=rule.label,
        section=rule.section,
        requirement_level=rule.requirement_level,
        evaluation_type=rule.evaluation_type,
        status=ReviewStatus.REVIEW,
        explanation="This checklist item has not been implemented yet.",
        review_reasons=[f"{rule.label} requires human review because no automated evaluator is available yet"],
    )


def _presence_rule(rule: ChecklistRule, value: str | None, pass_explanation: str, review_reason: str) -> ChecklistItemResult:
    if value:
        return ChecklistItemResult(
            id=rule.id,
            label=rule.label,
            section=rule.section,
            requirement_level=rule.requirement_level,
            evaluation_type=rule.evaluation_type,
            status=ReviewStatus.PASS,
            explanation=pass_explanation,
            evidence_text=value,
        )
    return ChecklistItemResult(
        id=rule.id,
        label=rule.label,
        section=rule.section,
        requirement_level=rule.requirement_level,
        evaluation_type=rule.evaluation_type,
        status=ReviewStatus.REVIEW,
        explanation=f"{rule.label} could not be confirmed from the OCR output.",
        review_reasons=[review_reason],
    )


def _warning_rule(rule: ChecklistRule, warning_text: str | None) -> ChecklistItemResult:
    if warning_text and warning_matches_exactly(warning_text):
        return ChecklistItemResult(
            id=rule.id,
            label=rule.label,
            section=rule.section,
            requirement_level=rule.requirement_level,
            evaluation_type=rule.evaluation_type,
            status=ReviewStatus.PASS,
            explanation="The government warning matched the mandated wording exactly.",
            evidence_text=warning_text,
        )

    reasons: list[str] = []
    if not warning_text:
        reasons.append("Government warning statement could not be read from the image")
        explanation = "The label did not yield a readable government warning statement."
    else:
        reasons.append("Government warning text did not match the required wording exactly")
        explanation = "The label contains warning text, but it did not match the required wording and capitalization exactly."

    return ChecklistItemResult(
        id=rule.id,
        label=rule.label,
        section=rule.section,
        requirement_level=rule.requirement_level,
        evaluation_type=rule.evaluation_type,
        status=ReviewStatus.REVIEW,
        explanation=explanation,
        review_reasons=reasons,
        evidence_text=warning_text,
    )


def _country_of_origin_rule(rule: ChecklistRule, extracted: ExtractedLabelData) -> ChecklistItemResult:
    if extracted.is_imported is False:
        return _conditional_pass(rule, "Country-of-origin review did not apply because the label appears to describe a domestic product.")
    if extracted.country_of_origin:
        return ChecklistItemResult(
            id=rule.id,
            label=rule.label,
            section=rule.section,
            requirement_level=rule.requirement_level,
            evaluation_type=rule.evaluation_type,
            status=ReviewStatus.PASS,
            explanation="A country-of-origin statement was detected on the label.",
            evidence_text=extracted.country_of_origin,
        )
    if extracted.is_imported is True:
        return ChecklistItemResult(
            id=rule.id,
            label=rule.label,
            section=rule.section,
            requirement_level=rule.requirement_level,
            evaluation_type=rule.evaluation_type,
            status=ReviewStatus.REVIEW,
            explanation="The label appears to describe an imported product, but a country-of-origin statement was not confirmed.",
            review_reasons=["Country-of-origin statement could not be confirmed for an imported product"],
        )
    return ChecklistItemResult(
        id=rule.id,
        label=rule.label,
        section=rule.section,
        requirement_level=rule.requirement_level,
        evaluation_type=rule.evaluation_type,
        status=ReviewStatus.REVIEW,
        explanation="The country-of-origin requirement depends on whether the product is imported, which could not be determined confidently.",
        review_reasons=["Importer/country-of-origin requirement may apply, but import status was unclear"],
    )


def _importer_rule(rule: ChecklistRule, extracted: ExtractedLabelData) -> ChecklistItemResult:
    if extracted.is_imported is False:
        return _conditional_pass(rule, "Importer name-and-address review did not apply because the label appears to describe a domestic product.")
    if extracted.is_imported is True and _is_importer_statement(extracted.name_and_address):
        return ChecklistItemResult(
            id=rule.id,
            label=rule.label,
            section=rule.section,
            requirement_level=rule.requirement_level,
            evaluation_type=rule.evaluation_type,
            status=ReviewStatus.PASS,
            explanation="An importer-style name-and-address statement was detected on the label.",
            evidence_text=extracted.name_and_address,
        )
    return ChecklistItemResult(
        id=rule.id,
        label=rule.label,
        section=rule.section,
        requirement_level=rule.requirement_level,
        evaluation_type=rule.evaluation_type,
        status=ReviewStatus.REVIEW,
        explanation="The importer name-and-address requirement could not be confirmed from the label.",
        review_reasons=["Importer/country-of-origin requirement may apply, but import status was unclear"],
        evidence_text=extracted.name_and_address,
    )


def _is_importer_statement(value: str | None) -> bool:
    if not value:
        return False
    normalized = value.casefold()
    return normalized.startswith("imported by") or normalized.startswith("imported for")


def _appellation_rule(rule: ChecklistRule, extracted: ExtractedLabelData) -> ChecklistItemResult:
    text = extracted.raw_text_excerpt or ""
    if not wine_appellation_required(text):
        return _conditional_pass(rule, "Appellation-of-origin review did not appear to be triggered by varietal, vintage, or estate-bottled text.")
    if extracted.appellation_of_origin:
        return ChecklistItemResult(
            id=rule.id,
            label=rule.label,
            section=rule.section,
            requirement_level=rule.requirement_level,
            evaluation_type=rule.evaluation_type,
            status=ReviewStatus.PASS,
            explanation="An appellation-of-origin statement was detected on the label.",
            evidence_text=extracted.appellation_of_origin,
        )
    return ChecklistItemResult(
        id=rule.id,
        label=rule.label,
        section=rule.section,
        requirement_level=rule.requirement_level,
        evaluation_type=rule.evaluation_type,
        status=ReviewStatus.REVIEW,
        explanation="The wine checklist appears to require an appellation-of-origin statement, but one was not confirmed.",
        review_reasons=["Appellation of origin could not be confirmed from the image"],
    )


def _conditional_disclosure_rule(
    rule: ChecklistRule,
    evidence: str | None,
    ocr_warnings: list[str],
) -> ChecklistItemResult:
    if evidence:
        return ChecklistItemResult(
            id=rule.id,
            label=rule.label,
            section=rule.section,
            requirement_level=rule.requirement_level,
            evaluation_type=rule.evaluation_type,
            status=ReviewStatus.PASS,
            explanation=f"{rule.label} was detected on the label.",
            evidence_text=evidence,
        )
    if ocr_warnings:
        return ChecklistItemResult(
            id=rule.id,
            label=rule.label,
            section=rule.section,
            requirement_level=rule.requirement_level,
            evaluation_type=rule.evaluation_type,
            status=ReviewStatus.REVIEW,
            explanation=f"{rule.label} is conditional, but the OCR output was not reliable enough to rule it in or out confidently.",
            review_reasons=[f"{rule.label} may apply, but the image quality or OCR output was too weak to confirm it"],
        )
    return _conditional_pass(rule, f"{rule.label} did not appear to apply based on the visible label text.")


def _conditional_pass(rule: ChecklistRule, explanation: str) -> ChecklistItemResult:
    return ChecklistItemResult(
        id=rule.id,
        label=rule.label,
        section=rule.section,
        requirement_level=rule.requirement_level,
        evaluation_type=rule.evaluation_type,
        status=ReviewStatus.PASS,
        explanation=explanation,
    )


def _join_evidence(*values: str | None) -> str | None:
    parts = [value for value in values if value]
    return " | ".join(parts) if parts else None


def _build_summary(
    status: ReviewStatus,
    beverage_type_label: str,
    counts: ReviewSummaryCounts,
    review_reasons: list[str],
) -> str:
    if status == ReviewStatus.PASS:
        return f"{beverage_type_label} checklist review passed all {counts.total} automated checks."
    if review_reasons:
        return f"{beverage_type_label} checklist review needs human follow-up on {counts.review} item(s)."
    return f"{beverage_type_label} checklist review requires human review."

"""Review orchestration service for single-item and batch processing."""

from __future__ import annotations

from uuid import uuid4

from app.models.schemas import (
    ApplicationData,
    BatchJobResponse,
    BatchReviewItem,
    ReviewField,
    ReviewResponse,
)
from app.services.comparison import compare_field, overall_status
from app.services.extraction import extract_application_fields
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


def review_label(filename: str, content_type: str, data: bytes, application_data: ApplicationData) -> ReviewResponse:
    """Run OCR, extraction, and comparison for a single label."""
    ocr_input = OCRInput(filename=filename, content_type=content_type, data=data)
    ocr_provider = build_ocr_provider(ocr_input)
    ocr_result = ocr_provider.extract_text(ocr_input)
    extracted = extract_application_fields(ocr_result.text)

    fields = [
        compare_field(ReviewField.BRAND_NAME, application_data.brand_name, extracted.brand_name),
        compare_field(ReviewField.CLASS_TYPE, application_data.class_type, extracted.class_type),
        compare_field(ReviewField.ABV, application_data.abv, extracted.abv),
        compare_field(ReviewField.NET_CONTENTS, application_data.net_contents, extracted.net_contents),
        compare_field(ReviewField.PRODUCER, application_data.producer, extracted.producer),
        compare_field(
            ReviewField.COUNTRY_OF_ORIGIN,
            application_data.country_of_origin,
            extracted.country_of_origin,
        ),
        compare_field(
            ReviewField.GOVERNMENT_WARNING,
            application_data.government_warning,
            extracted.government_warning,
        ),
    ]

    status = overall_status(fields)
    summary = _build_summary(status.value, fields)
    return ReviewResponse(
        filename=filename,
        overall_status=status,
        fields=fields,
        extracted=extracted,
        ocr=ocr_result,
        summary=summary,
    )


def build_batch_job(
    files: list[tuple[str, str, bytes]],
    application_data_list: list[ApplicationData],
) -> BatchJobResponse:
    """Process each batch item independently so one failure does not block the rest."""
    results: list[BatchReviewItem] = []
    for index, (filename, content_type, data) in enumerate(files):
        application_data = (
            application_data_list[index] if index < len(application_data_list) else ApplicationData()
        )
        try:
            result = review_label(filename, content_type, data, application_data)
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


def _build_summary(status: str, fields: list) -> str:
    mismatches = [field.display_name for field in fields if field.status.value == "mismatch"]
    uncertain = [field.display_name for field in fields if field.status.value in {"uncertain", "missing_label"}]
    if status == "match":
        return "All reviewed fields matched the submitted application data."
    if mismatches:
        return f"Review flagged mismatches in: {', '.join(mismatches)}."
    if uncertain:
        return f"Review needs human confirmation for: {', '.join(uncertain)}."
    return "Review completed with issues that need human confirmation."

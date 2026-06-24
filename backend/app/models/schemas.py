"""Typed request and response models for checklist-driven compliance review."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ReviewStatus(str, Enum):
    """Reviewer-facing status values used throughout the MVP."""

    PASS = "pass"
    REVIEW = "review"


class BeverageType(str, Enum):
    """Supported beverage families for checklist selection."""

    WINE = "wine"
    DISTILLED_SPIRITS = "distilled_spirits"
    MALT_BEVERAGE = "malt_beverage"


class RequirementLevel(str, Enum):
    """Whether a checklist rule is always required or conditional."""

    REQUIRED = "required"
    CONDITIONAL = "conditional"


class ExtractedLabelData(BaseModel):
    """Evidence extracted from OCR text for compliance evaluation."""

    brand_name: str | None = None
    designation: str | None = None
    alcohol_content: str | None = None
    net_contents: str | None = None
    name_and_address: str | None = None
    government_warning: str | None = None
    country_of_origin: str | None = None
    appellation_of_origin: str | None = None
    sulfite_declaration: str | None = None
    yellow_5_declaration: str | None = None
    cochineal_or_carmine_declaration: str | None = None
    aspartame_declaration: str | None = None
    coloring_statement: str | None = None
    treatment_with_wood_statement: str | None = None
    commodity_statement: str | None = None
    state_of_distillation: str | None = None
    age_statement: str | None = None
    is_imported: bool | None = None
    raw_text_excerpt: str | None = None


class OCRResult(BaseModel):
    """Raw OCR output plus any caveats from preprocessing or OCR execution."""

    text: str
    provider: str
    warnings: list[str] = Field(default_factory=list)
    preprocessing_steps: list[str] = Field(default_factory=list)


class ChecklistItemResult(BaseModel):
    """Result for a single transcribed checklist rule."""

    id: str
    label: str
    section: str
    requirement_level: RequirementLevel
    evaluation_type: str
    status: ReviewStatus
    explanation: str
    review_reasons: list[str] = Field(default_factory=list)
    evidence_text: str | None = None


class ReviewSummaryCounts(BaseModel):
    """Counts used for compact UI summaries."""

    total: int
    passed: int
    review: int


class ReviewResponse(BaseModel):
    """Checklist review response returned for one uploaded image."""

    filename: str
    beverage_type: BeverageType | None = None
    beverage_type_label: str
    overall_status: ReviewStatus
    summary: str
    summary_counts: ReviewSummaryCounts
    review_reasons: list[str] = Field(default_factory=list)
    checklist_items: list[ChecklistItemResult]
    extracted: ExtractedLabelData
    ocr: OCRResult


class BatchReviewItem(BaseModel):
    """Per-file batch job output."""

    filename: str
    status: str
    result: ReviewResponse | None = None
    error: str | None = None


class BatchJobResponse(BaseModel):
    """Response for batch submission and batch polling endpoints."""

    job_id: str
    status: str
    item_count: int
    processed_count: int
    results: list[BatchReviewItem] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Simple health response for smoke tests."""

    status: str
    version: str

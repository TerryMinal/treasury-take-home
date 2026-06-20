"""Typed request and response models for the API contract."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ReviewStatus(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    MISSING_LABEL = "missing_label"
    MISSING_APPLICATION = "missing_application"
    UNCERTAIN = "uncertain"


class ReviewField(str, Enum):
    BRAND_NAME = "brand_name"
    CLASS_TYPE = "class_type"
    ABV = "abv"
    NET_CONTENTS = "net_contents"
    PRODUCER = "producer"
    COUNTRY_OF_ORIGIN = "country_of_origin"
    GOVERNMENT_WARNING = "government_warning"


class ApplicationData(BaseModel):
    brand_name: str | None = None
    class_type: str | None = None
    abv: str | None = None
    net_contents: str | None = None
    producer: str | None = None
    country_of_origin: str | None = None
    government_warning: str | None = None


class OCRResult(BaseModel):
    text: str
    provider: str
    warnings: list[str] = Field(default_factory=list)


class FieldReview(BaseModel):
    field: ReviewField
    display_name: str
    application_value: str | None = None
    extracted_value: str | None = None
    normalized_application_value: str | None = None
    normalized_extracted_value: str | None = None
    status: ReviewStatus
    explanation: str


class ReviewResponse(BaseModel):
    filename: str
    overall_status: ReviewStatus
    fields: list[FieldReview]
    extracted: ApplicationData
    ocr: OCRResult
    summary: str


class BatchReviewItem(BaseModel):
    filename: str
    status: str
    result: ReviewResponse | None = None
    error: str | None = None


class BatchJobResponse(BaseModel):
    job_id: str
    status: str
    item_count: int
    processed_count: int
    results: list[BatchReviewItem] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    version: str

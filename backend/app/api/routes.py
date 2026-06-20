"""API route handlers."""

from __future__ import annotations

import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.models.schemas import ApplicationData, BatchJobResponse, HealthResponse, ReviewResponse
from app.services.review import batch_job_store, build_batch_job, review_label

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return a lightweight health response for monitoring and smoke tests."""
    return HealthResponse(status="ok", version=settings.app_version)


@router.post("/review", response_model=ReviewResponse)
async def review_endpoint(
    label_file: UploadFile = File(...),
    application_data: str = Form("{}"),
) -> ReviewResponse:
    """Run a single label review from multipart form data."""
    parsed_application_data = _parse_application_data(application_data)
    file_bytes = await label_file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded label file was empty.")

    return review_label(
        filename=label_file.filename or "uploaded-label",
        content_type=label_file.content_type or "application/octet-stream",
        data=file_bytes,
        application_data=parsed_application_data,
    )


@router.post("/batch", response_model=BatchJobResponse)
async def batch_endpoint(
    label_files: list[UploadFile] = File(...),
    application_data: str = Form("[]"),
) -> BatchJobResponse:
    """Run batch review over multiple labels."""
    application_data_list = _parse_batch_application_data(application_data)
    files: list[tuple[str, str, bytes]] = []
    for upload in label_files:
        file_bytes = await upload.read()
        files.append(
            (
                upload.filename or "uploaded-label",
                upload.content_type or "application/octet-stream",
                file_bytes,
            )
        )
    return build_batch_job(files, application_data_list)


@router.get("/batch/{job_id}", response_model=BatchJobResponse)
def batch_status(job_id: str) -> BatchJobResponse:
    """Fetch the current batch-job status."""
    job = batch_job_store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Batch job not found.")
    return job


def _parse_application_data(raw_value: str) -> ApplicationData:
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail=f"application_data must be valid JSON: {exc.msg}") from exc
    return ApplicationData.model_validate(payload)


def _parse_batch_application_data(raw_value: str) -> list[ApplicationData]:
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail=f"application_data must be valid JSON: {exc.msg}") from exc
    if not isinstance(payload, list):
        raise HTTPException(status_code=422, detail="application_data must be a JSON array for batch review.")
    return [ApplicationData.model_validate(item) for item in payload]

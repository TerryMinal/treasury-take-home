"""API route handlers for checklist-driven image review."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.models.schemas import BatchJobResponse, HealthResponse, ReviewResponse
from app.services.review import batch_job_store, build_batch_job, review_label

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return a lightweight health response for monitoring and smoke tests."""
    return HealthResponse(status="ok", version=settings.app_version)


@router.post("/review", response_model=ReviewResponse)
async def review_endpoint(
    label_file: UploadFile = File(...),
) -> ReviewResponse:
    """Run a single checklist review from an uploaded label image."""
    file_bytes = await label_file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded label file was empty.")

    return review_label(
        filename=label_file.filename or "uploaded-label",
        content_type=label_file.content_type or "application/octet-stream",
        data=file_bytes,
    )


@router.post("/batch", response_model=BatchJobResponse)
async def batch_endpoint(
    label_files: list[UploadFile] = File(...),
) -> BatchJobResponse:
    """Run batch review over multiple uploaded label images."""
    files: list[tuple[str, str, bytes]] = []
    for upload in label_files:
        file_bytes = await upload.read()
        if not file_bytes:
            continue
        files.append(
            (
                upload.filename or "uploaded-label",
                upload.content_type or "application/octet-stream",
                file_bytes,
            )
        )
    if not files:
        raise HTTPException(status_code=400, detail="At least one non-empty label file is required.")
    return build_batch_job(files)


@router.get("/batch/{job_id}", response_model=BatchJobResponse)
def batch_status(job_id: str) -> BatchJobResponse:
    """Fetch the current batch-job status."""
    job = batch_job_store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Batch job not found.")
    return job

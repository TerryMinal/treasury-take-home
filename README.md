# Alcohol Label Verification Prototype

This repository contains a standalone prototype that helps reviewers compare alcohol label artwork against submitted application data.

## Stack

- Frontend: SvelteKit + TypeScript
- Backend: FastAPI + Python
- OCR approach: local-first provider abstraction with optional Tesseract support

## What the prototype does

- single-label review via `POST /review`
- batch review via `POST /batch` and `GET /batch/{job_id}`
- tolerant matching for ordinary fields
- strict, exact matching for the government warning
- simple reviewer-facing UI for single and batch workflows

## Repository layout

- `backend/app/`: FastAPI application code
- `backend/tests/`: backend tests
- `frontend/src/`: SvelteKit application code

## Backend setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --app-dir backend --reload
```

Optional local OCR dependencies:

```bash
pip install -e .[ocr]
```

## Frontend setup

```bash
cd frontend
pnpm install
pnpm dev
```

Set `PUBLIC_API_BASE_URL` if the backend is not running on `http://localhost:8000`.

## Verification

Backend:

```bash
pytest
```

Frontend:

```bash
cd frontend
pnpm test
pnpm check
```

## Prototype assumptions

- Batch jobs are stored in memory for prototype scope.
- Text fixture uploads are supported so the comparison pipeline can be exercised even when OCR tooling is unavailable locally.
- Real image OCR improves when optional Tesseract dependencies are installed.

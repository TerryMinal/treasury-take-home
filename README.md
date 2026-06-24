# Alcohol Label Verification Prototype

This repository contains a standalone prototype that helps reviewers run TTB-style compliance checks against uploaded alcohol label images.

## Stack

- Frontend: SvelteKit + TypeScript
- Backend: FastAPI + Python
- OCR approach: local-first provider abstraction with preprocessing and optional Tesseract support

## What the prototype does

- single-label review via `POST /review`
- batch review via `POST /batch` and `GET /batch/{job_id}`
- detects `wine`, `distilled_spirits`, or `malt_beverage` from OCR text
- evaluates OCR evidence against transcribed checklist rules from the attached TTB PDF checklists
- enforces exact matching for the government warning
- shows only green passed states and yellow human-review states
- lists explicit human-review reasons for any yellow image or checklist item
- provides an elderly-friendly batch upload flow without JSON or manual application forms

## Repository layout

- `backend/app/`: FastAPI application code
- `backend/tests/`: backend tests
- `frontend/src/`: SvelteKit application code

## Backend setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --app-dir backend --reload
```

Optional local OCR dependencies:

```bash
pip install -e '.[ocr]'
```

Install the `tesseract` executable locally as well if you want OCR to run on image uploads. Without it, the app still returns a structured review, but image files will be marked for human review with an OCR availability reason.

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
- The PDF checklist documents are transcribed into structured runtime rules rather than parsed on every request.
- Real image OCR requires optional Tesseract dependencies and a local `tesseract` binary.
- Layout-specific checklist items, such as distilled-spirits same-field-of-vision review, fall back to human review when OCR alone cannot verify them reliably.

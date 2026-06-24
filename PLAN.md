# Test Plan for Alcohol Label Verification Prototype

## Summary

This file captures the implementation-verification strategy for the alcohol label verification prototype. It describes how we will prove that OCR works on real sample labels, that the Svelte frontend stays aligned with the FastAPI backend contract, that each route behaves correctly, and that the full single-review and batch workflows function end to end.

The test strategy is layered so failures are easy to localize:

- backend unit tests for preprocessing, OCR, extraction, comparison, and warning validation
- backend API tests for request validation and route behavior
- frontend component and route tests for rendering, submission, loading, and error handling
- Playwright end-to-end tests for real user workflows

## Purpose

Document the test approach for the MVP so implementation can be verified consistently during development and before submission.

## Execution Status

This repository currently contains planning documentation only. The application code and runtime configuration needed for the backend, frontend, and Playwright tests described below are not present yet.

To keep execution aligned with `AGENTS.md`, the current implementation step is limited to:

- reserving the expected test directory structure
- documenting the exact files and coverage to add once application code exists
- recording which planned items are blocked on missing implementation

See [docs/TEST_EXECUTION_STATUS.md](/Users/tguan/Documents/Projects/treasury-take-home/docs/TEST_EXECUTION_STATUS.md) for the current execution checklist and blockers.

## Test Layers

### 1. Backend unit tests

Cover the core review pipeline below the API layer.

Include tests for:

- image preprocessing
- OCR provider behavior on known fixtures
- field extraction from OCR text
- strict government warning validation
- tolerant comparison logic for normal fields
- end-to-end review pipeline behavior with fixture images

Recommended backend test files:

- `backend/tests/test_preprocessing.py`
- `backend/tests/test_ocr_provider.py`
- `backend/tests/test_field_extraction.py`
- `backend/tests/test_warning_validator.py`
- `backend/tests/test_comparison.py`
- `backend/tests/test_review_pipeline.py`

### 2. Backend API tests

Verify FastAPI routes and request/response contracts.

Cover:

- `GET /health`
- `POST /review`
- `POST /batch`
- `GET /batch/{job_id}`

Test:

- valid multipart uploads
- missing file or malformed input
- clean success responses
- OCR or processing failure returning structured review output instead of server crashes
- batch status transitions and partial item failures

Recommended backend API test files:

- `backend/tests/test_review_api.py`
- `backend/tests/test_batch_api.py`

### 3. Frontend component and route tests

Verify that the Svelte frontend renders correctly and stays in sync with the backend schema.

Use mocked backend responses to test:

- application form rendering and validation
- file upload behavior
- results table rendering
- batch results table rendering
- `/review` route submission, loading, success, and error states
- `/batch` route submission flow
- `/batch/[jobId]` route polling and result display

Recommended frontend test files:

- `frontend/src/lib/components/__tests__/ApplicationForm.test.ts`
- `frontend/src/lib/components/__tests__/FileUpload.test.ts`
- `frontend/src/lib/components/__tests__/ResultsTable.test.ts`
- `frontend/src/lib/components/__tests__/BatchResultsTable.test.ts`
- `frontend/src/routes/review/review.test.ts`
- `frontend/src/routes/batch/batch.test.ts`
- `frontend/src/routes/batch/[jobId]/batch-job.test.ts`

### 4. End-to-end tests

Use Playwright to verify the full application works as a user would experience it.

Cover:

- route smoke checks
- single-label review flow
- batch review flow
- user-facing error handling

Recommended E2E files:

- `frontend/e2e/route-smoke.spec.ts`
- `frontend/e2e/review-flow.spec.ts`
- `frontend/e2e/batch-flow.spec.ts`
- `frontend/e2e/error-handling.spec.ts`

## Test Fixtures

Use sample label fixtures with adjacent expected-output files.

Recommended structure:

- `backend/tests/fixtures/labels/*.jpg|png`
- `backend/tests/fixtures/labels/*.expected.json`

Each expected file should define:

- expected anchor text in OCR output
- expected extracted field values
- expected warning validity
- expected overall review behavior where needed

Use at least these fixture categories:

- clean readable label
- warning capitalization mismatch
- punctuation-only ordinary-field variation
- low-quality or partially unreadable label
- invalid or corrupt input file

## Contract Verification

Use the backend response schema as the contract source of truth.

Verify that frontend tests can render backend-shaped payloads without ad hoc transformation. Add one frontend API/client test to confirm valid review responses are parsed safely and malformed responses fail clearly.

## Manual QA Pass

After automated tests pass, run a short manual verification pass:

- single review with a real sample label
- batch review with 3–5 labels
- confirm statuses are understandable
- confirm errors suggest a next step
- confirm performance feels acceptable for the MVP workflow

## Commands

Document and use these commands:

- Backend tests: `pytest`
- Frontend unit/component tests: `pnpm test` or `npm test`
- End-to-end tests: `npx playwright test`

Playwright should be run against the real local frontend and backend for full integration validation.

## Automation Priority

Implement tests in this order:

1. `test_warning_validator.py`
2. `test_comparison.py`
3. `test_review_api.py`
4. `ResultsTable.test.ts`
5. `review.test.ts`
6. `review-flow.spec.ts`
7. `test_field_extraction.py`
8. `test_review_pipeline.py`
9. `test_batch_api.py`
10. batch frontend tests
11. batch E2E tests

This sequence validates the highest-risk logic first while getting the main single-review workflow covered early.

## Acceptance Criteria

The test plan is complete when it verifies that:

- OCR works against known fixture labels well enough to extract required fields
- warning validation is strict and exact
- tolerant comparison behaves correctly for ordinary fields
- `/review` and batch endpoints return stable structured responses
- frontend routes render and submit correctly
- frontend and backend stay aligned on response shape
- the single-label review flow passes end to end
- at least one batch flow passes end to end
- failures produce usable messages rather than crashes

## Assumptions

- The MVP uses a local-first OCR stack with preprocessing plus Tesseract via `pytesseract`
- Sample-label fixtures are available or will be created for automated testing
- Batch state remains ephemeral for prototype scope
- This file is intended as a concise execution guide, not a full QA handbook

# Test Execution Status

## Purpose

This document turns [TEST_PLAN.md](/Users/tguan/Documents/Projects/treasury-take-home/TEST_PLAN.md) into a concrete execution checklist for this repository.

The current repository contains planning and requirements documentation, but it does not yet contain the SvelteKit or FastAPI application code described in the project docs. Because of that, the test plan can only be executed up to the point of scaffolding the expected test layout, naming the required coverage, and identifying what is blocked on application implementation.

## Current Status

| Priority | Planned item | Status | Notes |
| --- | --- | --- | --- |
| 1 | `backend/tests/test_warning_validator.py` | Complete | Strict warning-validation coverage added. |
| 2 | `backend/tests/test_comparison.py` | Complete | Tolerant normalization and mismatch coverage added. |
| 3 | `backend/tests/test_review_api.py` | Complete | `/health` and `/review` contract coverage added. |
| 4 | `frontend/src/lib/components/__tests__/ResultsTable.test.ts` | Complete | Basic rendering coverage added. |
| 5 | `frontend/src/routes/review/review.test.ts` | Pending | Route-level tests still need installed frontend toolchain. |
| 6 | `frontend/e2e/review-flow.spec.ts` | Pending | Requires runnable installed frontend and backend apps. |
| 7 | `backend/tests/test_field_extraction.py` | Complete | Extraction heuristics covered with fixture-style text input. |
| 8 | `backend/tests/test_review_pipeline.py` | Pending | Useful next layer, but core API path already exercises orchestration. |
| 9 | `backend/tests/test_batch_api.py` | Pending | Batch implementation exists but lacks direct API test coverage. |
| 10 | Batch frontend tests | Blocked | Requires batch screens, components, and polling behavior. |
| 11 | Batch E2E tests | Blocked | Requires full batch workflow implementation. |

## Work Completed In This Repository

- Implemented the FastAPI backend with typed schemas, OCR abstraction, single review, and batch review.
- Implemented the SvelteKit frontend with single-review, batch-submission, and batch-status flows.
- Added backend tests for warning validation, comparison, extraction, and review API behavior.
- Added frontend tests for response-shape validation and results rendering.

## Unblock Order

Complete these implementation steps before writing the real tests:

1. Add the FastAPI application package and define typed request and response schemas.
2. Implement the single-review pipeline entry points for OCR, extraction, comparison, and warning validation.
3. Add the SvelteKit frontend routes and shared API response types.
4. Add batch-processing models and route handlers.
5. Add sample label fixtures and expected-output files.

## Definition Of Done

The test plan can be considered fully executed only after the repository contains:

- runnable backend and frontend applications
- real automated tests at the planned paths
- documented commands for format, lint, type check, unit tests, and E2E tests
- passing verification for the implemented stack

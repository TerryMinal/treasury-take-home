# Backend Test Scaffold

This folder reserves the backend test layout defined in [TEST_PLAN.md](/Users/tguan/Documents/Projects/treasury-take-home/TEST_PLAN.md).

Create these test modules once the FastAPI backend exists:

- `test_preprocessing.py`
- `test_ocr_provider.py`
- `test_field_extraction.py`
- `test_warning_validator.py`
- `test_comparison.py`
- `test_review_pipeline.py`
- `test_review_api.py`
- `test_batch_api.py`

## Intended Coverage

### Unit coverage

- image normalization for skew, grayscale, thresholding, and bounded resizing
- OCR provider behavior against known fixtures
- extraction of brand name, class/type, ABV, net contents, producer details, origin, and warning text
- strict validation of the government warning statement
- tolerant comparison for ordinary fields
- review-pipeline behavior when OCR returns low-confidence or partial text

### API coverage

- `GET /health`
- `POST /review`
- `POST /batch`
- `GET /batch/{job_id}`

API tests should verify structured error handling rather than server crashes whenever OCR or processing fails.

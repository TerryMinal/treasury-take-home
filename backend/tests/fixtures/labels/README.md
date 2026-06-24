# Label Fixture Scaffold

Store image fixtures here alongside adjacent expected-output files.

Recommended naming pattern:

- `clean-readable-label.png`
- `clean-readable-label.expected.json`
- `warning-capitalization-mismatch.png`
- `warning-capitalization-mismatch.expected.json`
- `ordinary-field-punctuation-variation.png`
- `ordinary-field-punctuation-variation.expected.json`
- `low-quality-label.png`
- `low-quality-label.expected.json`
- `corrupt-input-file.expected.json`

Each expected file should capture:

- OCR anchor text worth asserting
- extracted field values
- warning validity
- expected review statuses where that improves clarity

Current seeded fixture:

- `clean-readable-label.png`: baseline OCR-friendly label image for upload, OCR, extraction, and end-to-end review tests
- `clean-readable-label.expected.json`: expected anchor text, extracted fields, submitted application data, and overall review status for the baseline fixture
- `warning-capitalization-mismatch.png`: strict warning-validation case where title case should fail exact warning comparison
- `warning-capitalization-mismatch.expected.json`: expected warning mismatch with ordinary fields still matching
- `ordinary-field-punctuation-variation.png`: normalization case with punctuation, spacing, and casing differences in ordinary fields
- `ordinary-field-punctuation-variation.expected.json`: expected normalized matches across ordinary fields
- `low-quality-label.png`: degraded OCR case with blur, light skew, and noise
- `low-quality-label.expected.json`: resilience-oriented expectations that favor partial OCR and uncertain review outcomes

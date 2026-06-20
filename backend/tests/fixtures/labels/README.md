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

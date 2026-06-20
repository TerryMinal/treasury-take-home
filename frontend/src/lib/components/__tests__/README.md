# Frontend Component Test Scaffold

This directory is reserved for component tests that validate rendering against backend-shaped data.

Planned files:

- `ApplicationForm.test.ts`
- `FileUpload.test.ts`
- `ResultsTable.test.ts`
- `BatchResultsTable.test.ts`

These tests should prefer mocked API payloads that match the backend response schema exactly, so the frontend contract stays aligned without ad hoc response reshaping.

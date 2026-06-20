# AGENTS.md

## Stack

-   Frontend: SvelteKit + TypeScript
-   Backend: FastAPI + Python

## Principles

-   Make the smallest correct change.
-   Preserve existing behavior unless asked.
-   Prefer readability over cleverness.
-   Keep functions focused.
-   Avoid unnecessary dependencies.
-   Update documentation when behavior changes.

## Types

-   Avoid `any` in TypeScript.
-   Type all public Python functions.
-   Use Pydantic models for request/response validation.

## Documentation

Document public functions, non-obvious business logic, and API changes.
Explain **why**, not **what**.

## Testing

Run formatting, linting, type checking, and tests before considering
work complete. Add regression tests for bug fixes whenever practical.

## Workflow

1.  Read existing code.
2.  Follow existing patterns.
3.  Make the smallest correct change.
4.  Verify types and tests.
5.  Update documentation if needed.

## References

-   docs/ARCHITECTURE.md
-   docs/CONTRIBUTING.md

## Development Workflow
For each objective:
1. Break the work into small, testable features
2. For each feature:
   * Git branch for this feature
   * Write or update tests first, including edge cases
   * Implement the feature. Incrementally git commit changes
   * Run [tests](#testing), type checks, linting, and formatting. Refer to [style guide](#style-guide) for formatting
   * Review for security, correctness, and regressions
   * Fix critical issues immediately; note non-blocking risks for follow-up
   * Git commit only the files relevant to that feature
   * Push and merge branch, but do not delete
   * Checkout to original branch after finishing feature if next feature does not build upon this one
3. Update documentation with any changes
4. Summarize changes made 
## Style Guide
* **Python**
  * Use type hints for public functions and non-obvious values
  * Add docstrings for public modules, classes, and functions
  * Use inline comments only for non-obvious logic, constraints, or tradeoffs
  * Format with `black` or `ruff format`; lint with `ruff`
  * Follow clear, descriptive naming conventions
* **TypeScript**
  * Use `strict` mode and avoid `any`.
  * Prefer explicit types, interfaces, unions, and generics
  * Add JSDoc for exported functions, classes, types, and modules
  * Use inline comments only for non-obvious logic, constraints, or tradeoffs
  * Use clear, descriptive names for variables, functions, and modules
* **Svelte**
  * Use TypeScript where practical.
  * Keep component, prop, event, store, and action names clear and descriptive
  * Document component props, exported functions, stores, and actions
  * Use inline comments only for non-obvious reactive logic or UI behavior
  * Keep styling scoped, consistent, and close to the component unless shared globally
## Development Principles
* Keep changes small, focused, and easy to review
* Separate I/O, business logic, and side effects where practical
* Validate untrusted data at API, file, and user-input boundaries
* Handle errors explicitly and avoid broad catches
* Design for testability with clear seams and minimal hidden state
* Prefer derived state over duplicated state
* Use semantic, accessible UI markup
* Never hard-code secrets, credentials, or environment-specific values
## Testing
* **Python**
  * Use `pytest`
  * Test behavior, edge cases, and error paths
  * Use fixtures for shared setup
  * Mock external services, I/O, time, and randomness
  * Keep tests deterministic and isolated
* **TypeScript**
  * Use `vitest` or `jest`
  * Test behavior, edge cases, and error paths
  * Mock external APIs, browser APIs, timers, and storage
  * Keep tests deterministic and isolated
* **Svelte**
  * Test user-visible behavior, rendered output, events, and state changes
  * Prefer user-centric queries over implementation details
  * Mock stores, server calls, navigation, and browser-only APIs
  * Use end-to-end tests for critical flows
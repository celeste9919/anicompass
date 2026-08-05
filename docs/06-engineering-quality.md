# Engineering Quality Standards

## General Rules

- Keep one responsibility per module.
- Prefer explicit data models over dictionaries crossing module boundaries.
- Keep QML free of network, SQL, prompt, and credential logic.
- Keep provider-specific code behind adapters.
- Avoid base classes unless two real implementations need the shared contract.
- Use no global mutable application state.
- Do not silently swallow exceptions.

## Python Style

- Format and lint with Ruff.
- Use type hints on public functions and service boundaries.
- Use docstrings for public modules, classes, and non-obvious contracts.
- Use Chinese comments for learning-oriented explanations only where logic is
  not self-explanatory.
- Use English identifiers.

## QML Style

- Reusable visual controls live under `ui/components/`.
- Page components own layout and interaction binding, not business logic.
- Keep stable dimensions for navigation, buttons, covers, and repeated cards.
- All visible strings use translation identifiers.

## Dependency Rule

Before adding a dependency, record its responsibility, why the standard
library is insufficient, license, supported platforms, packaging impact, test
strategy, and removal cost.

## Interface Change Rule

Changes to public service methods or domain models require affected-module
review, tests, documentation, migration planning for persisted data, and a
daily-log decision entry.

## Error Rule

- Raise typed domain or infrastructure errors.
- Convert errors to user text only in ErrorPresenter.
- Preserve a safe diagnostic code.
- Never include secrets in exception messages.
- Unknown errors use a generic user message.

## Data Migration Rule

- Every SQLite schema change has an ordered migration.
- Released migrations are forward-only.
- Migration tests start from the previous released schema.
- A failed migration must not leave partially modified data.

## Definition Of Done

A change is done only when acceptance criteria, relevant tests, formatting,
linting, secret checks, documentation, and the daily log are complete.


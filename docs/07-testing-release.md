# Testing And Release Standards

## Test Layers

### Unit Tests

Cover validation, prompt construction, AI response parsing, catalog
normalization, policy filtering, watch-list calculations, history retention,
backup validation, and secret redaction.

### Integration Tests

Cover SQLite repositories and migrations, service transactions, provider
adapters against protocol fixtures, isolated keyring behavior, and backup
round trips.

Network responses may be simulated in tests. Runtime product behavior must not
use fake recommendation mode.

### UI Tests

Cover navigation, language switching, theme switching, form validation,
loading/error/partial-result states, list editing, and text wrapping at the
minimum supported window size.

### Manual Smoke Tests

Required for real provider connection, real catalog search, OS keyring, file
dialogs, packaged application launch, and clean-machine release candidates.

## Standard Checks

After project setup:

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest
python -m compileall src
```

Packaging checks are added in Phase 0 and must use committed build
configuration rather than undocumented local commands.

## Security Checks

- Search repository and build output for test-secret markers.
- Verify backups contain no credential fields.
- Verify logs redact authorization headers and API-key-like values.
- Reject non-HTTPS custom endpoints unless an approved local exception exists.
- Verify imported paths cannot escape the selected file.

## Release Evidence

Each release candidate records source revision, Python and lock versions,
operating system and architecture, build command, automated checks, manual
smoke tests, artifact checksum, known limitations, and signing state.

## Platform Rule

- Build Windows artifacts on Windows.
- Build macOS artifacts on macOS.
- Test each artifact in a clean user environment.
- Do not claim macOS support from Windows-only source tests.

## Failure Rule

If a required check fails, mark the phase not ready, record the failure, fix it
within the current phase, and rerun the failed and related checks.


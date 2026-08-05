# Phase 7 Local Backup And Restore

Date: 2026-08-04  
Status: Versioned local backup/restore backend, QML bridge, and Settings UI implemented

## Scope

This phase provides local data portability for user-owned data only. It exports
watch-list items and recommendation history sessions. It does not export API
keys, provider secrets, keyring contents, logs, settings files, cache files, or
network responses.

## Implemented

- Versioned `AniCompassBackup` JSON payload with `format_version = 1`.
- Safe backup models for watch-list items and recommendation history sessions.
- `BackupService` for export, inspect/validate, and restore.
- Transactional restore that rolls back on SQLite constraint failures.
- `BackupBridge` as the QML-facing boundary for export/import status.
- Settings page export/restore buttons and native file dialogs.
- Restore completion signal that refreshes My List and History page data.

## Files

- `src/anicompass/backup/__init__.py`
- `src/anicompass/backup/models.py`
- `src/anicompass/backup/service.py`
- `src/anicompass/backup/bridge.py`
- `src/anicompass/main.py`
- `src/anicompass/ui/Main.qml`
- `tests/test_backup_service.py`
- `tests/test_backup_bridge.py`

## Security Rules

- API keys remain in `CredentialService`/keyring only and are not read by the
  backup path.
- Backup JSON must not contain `api_key`, `apikey`, `authorization`, or
  `secret` fields.
- Invalid or incompatible backup files must fail before replacing current data.
- SQLite errors during import must roll back and keep the existing local data.

## Acceptance Checks

```powershell
.\.venv\Scripts\python -m ruff check . --no-cache
.\.venv\Scripts\python -m pytest -q -p no:cacheprovider -p no:anyio
.\.venv\Scripts\pyside6-qmllint src\anicompass\ui\Main.qml
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'; .\.venv\Scripts\python -m anicompass.main --smoke-test
```

Result: passed. Pytest currently covers 72 focused checks. QML lint syntax
passed with existing non-blocking unqualified-access warnings.

## Current Test Coverage

- Backup export writes a versioned JSON file.
- Backup bytes exclude sensitive key-like fields.
- Backup restore works into a fresh SQLite database.
- Malformed/incompatible backup files do not change existing data.
- Import rollback is proven with duplicate records that violate SQLite
  constraints.
- QML-facing bridge handles local file URLs, reports invalid backups, and emits
  restore completion.
- Settings page declares export/restore buttons, dialogs, status text, and
  `backupBridge` calls.

## Next Step

Begin Phase 8 release readiness in small steps: README/user run instructions,
license notices, app metadata/icon decisions, and Windows packaging smoke retry
when escalation/service availability permits.

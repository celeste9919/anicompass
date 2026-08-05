# Phase 8 Release Readiness

Date: 2026-08-04  
Status: README, license, app icon, and Windows packaged smoke implemented

## Scope

Phase 8 prepares the Windows release candidate. It should proceed in small
steps: public README, license notices, app metadata/icon, packaging smoke, and
release artifact verification.

## Implemented In This Step

- Root `README.md` with feature list, security boundaries, source run commands,
  quality checks, and packaging status.
- MIT `LICENSE`, matching the requirement that everyone can use the software.
- `docs/THIRD_PARTY_NOTICES.md` for direct dependencies, development tools, and
  catalog attribution reminders.
- `.gitignore` for Python caches, local virtualenv, build outputs, SQLite data,
  logs, and local env files.
- `assets/anicompass.ico` and `assets/anicompass.png` as the first app icon.
- `AniCompass.spec` for no-console Windows packaging.
- Packaged smoke test for `dist/AniCompass/AniCompass.exe --smoke-test`.

## Remaining Phase 8 Work

- Add richer Windows version metadata if needed.
- Decide whether to publish binary artifacts through GitHub Releases.
- Confirm GitHub repository metadata and publish source.

## Acceptance Checks For This Step

```powershell
.\.venv\Scripts\python -m ruff check . --no-cache
.\.venv\Scripts\python -m pytest -q -p no:cacheprovider -p no:anyio
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'; .\.venv\Scripts\python -m anicompass.main --smoke-test
.\.venv\Scripts\pyinstaller AniCompass.spec --noconfirm
$env:QT_QPA_PLATFORM='offscreen'; .\dist\AniCompass\AniCompass.exe --smoke-test
Get-FileHash -Algorithm SHA256 .\dist\AniCompass\AniCompass.exe
```

Result: passed. Windows executable SHA256:

```text
879FEE8B2DA24C0A4BE90FEAD9009502B838285E9CA706952ED3354E8B2FADD6
```

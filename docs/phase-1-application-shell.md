# Phase 1 Application Shell And Design System

Date: 2026-08-04  
Status: Application shell implemented, settings wrapper added, packaged smoke test rebuilt

## Scope

This step creates only the application shell and design-system state. It does
not implement catalog search, AI recommendation calls, SQLite persistence, or
watch-list editing.

## Implemented

- Stable desktop sidebar with five destinations: Recommend, Search, My List,
  History, and Settings.
- Chinese and English UI copy skeleton inside the QML shell.
- Global language state persisted through a Python `SettingsService` exposed to
  QML.
- User-adjustable RGB accent color persisted through the same non-secret local
  settings service.
- Shared empty/loading/error/missing-config state badges for future screens.
- Empty screen placeholders that avoid fake anime, fake AI results, or fake
  catalog entries.
- Public QML shell contract for automated QA: page selection, language switch,
  accent color update, and explicit settings sync.

## Files

- `src/anicompass/ui/Main.qml`
- `src/anicompass/main.py`
- `src/anicompass/settings.py`
- `tests/test_qml_smoke.py`
- `tests/test_phase1_shell_contract.py`
- `qa/phase-1-shell.png`
- `dist/AniCompassSmoke/AniCompassSmoke.exe`

## Settings Rules

- `SettingsService` stores only non-sensitive UI preferences.
- API keys and provider credentials must not use this service; they belong in a
  future keyring-backed credential service.
- Tests use `ANICOMPASS_CONFIG_DIR` to keep settings isolated in temporary
  directories.
- Normal runtime uses the Qt application config location when writable and only
  falls back during restricted local smoke runs.

## Source Acceptance Checks

```powershell
.\.venv\Scripts\python -m ruff check . --no-cache
.\.venv\Scripts\python -m pytest -q -p no:cacheprovider -p no:anyio
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'; .\.venv\Scripts\python -m anicompass.main --smoke-test
```

Result: passed. Pytest currently covers 5 focused shell and settings-contract
checks.

## Packaged Smoke Check

```powershell
$env:QT_QPA_PLATFORM='offscreen'; .\dist\AniCompassSmoke\AniCompassSmoke.exe --smoke-test
```

Result: passed. The packaged bundle contains
`dist/AniCompassSmoke/_internal/src/anicompass/ui/Main.qml` with Phase 1 shell
and `settingsService` markers.

## Visual QA Artifact

A Phase 1 offscreen screenshot was generated for nonblank layout verification:

- `qa/phase-1-shell.png`

The screenshot dimensions are 1080 x 700. Pixel sampling found distinct text,
surface, border, accent, and background colors, so the shell is not rendering as
a blank surface.

## Known Notes

- PyInstaller reported a missing optional Qt labs assetdownloader plugin during
  analysis. The current app does not import that plugin, and the packaged smoke
  test passed.
- Normal release packaging still needs a no-console build, icon, metadata, and
  clean-machine smoke test in a later phase.

## Next Step

After user approval, continue Phase 1 with one real interactive/manual visual
pass of the shell. If the shell feels acceptable, Phase 2 can start with the
catalog provider interface and Jikan search adapter skeleton.
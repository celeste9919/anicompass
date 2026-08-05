# Phase 0 Packaging Feasibility

Date: 2026-08-04  
Status: Windows PyInstaller smoke test passed; pyside6-deploy blocked in current environment

## Current Local Environment

- Project path: `I:\Temp\Git\AniCompass`
- Python: 3.12.6
- Virtual environment: `.venv`
- Installed project dependencies:
  - PySide6 6.11.1
  - keyring 25.7.0
  - httpx 0.28.1
  - pydantic 2.13.4
  - pytest 9.1.1
  - ruff 0.16.1

## Completed Smoke Test

Created a minimal PySide6/QML app:

- `src/anicompass/main.py`
- `src/anicompass/ui/Main.qml`
- `tests/test_qml_smoke.py`

Verified:

```powershell
.\.venv\Scripts\python -m compileall src tests
.\.venv\Scripts\python -m ruff check . --no-cache
.\.venv\Scripts\python -m pytest -q -p no:cacheprovider -p no:anyio
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'; .\.venv\Scripts\python -m anicompass.main --smoke-test
```

Results:

- Python compilation passed.
- Ruff passed.
- Pytest passed with 2 tests.
- QML loaded in offscreen smoke-test mode.

## Packaging Direction

Primary packaging candidate: `pyside6-deploy`.

Reasons:

- It is the Qt for Python deployment tool.
- Qt documentation recommends it for optimized PySide6 executable deployment.
- It can work with `pyproject.toml` project metadata and QML files.

Fallback packaging candidate: PyInstaller.

Reasons:

- PyInstaller is already available on the Windows machine.
- PyInstaller can bundle Python apps so users do not need Python installed.
- PyInstaller is not a cross-compiler, so Windows and macOS artifacts must be
  built separately on their target operating systems.

## Known Packaging Constraints

- Windows `.exe` must be built on Windows.
- macOS `.app` must be built on macOS.
- macOS signing and notarization require a separate release decision.
- QML files and future image/icon resources must be included explicitly in the
  packaging configuration.
- Normal app launch should not open a console window.
- Release artifacts need clean-machine smoke tests.

## pyside6-deploy Result

Attempted `pyside6-deploy --init` and `--dry-run`. Both failed because the tool could not resolve `pyside6-qmlimportscanner` from its internal subprocess call, even though the scanner executable exists in `.venv\Scripts` and works when called directly. Treat this as an environment/tooling blocker, not an application-code failure.

## PyInstaller Fallback Result

Installed PyInstaller 6.21.0 into `.venv` and built a Windows onedir smoke artifact:

- `dist\AniCompassSmoke\AniCompassSmoke.exe`
- `AniCompassSmoke.spec`

Verified:

```powershell
$env:QT_QPA_PLATFORM='offscreen'; .\dist\AniCompassSmoke\AniCompassSmoke.exe --smoke-test
```

Result: passed. The packaged executable loaded the bundled QML file and exited successfully.

## Next Packaging Step

Use PyInstaller as the current Windows fallback packaging path for Phase 1 and Phase 2 smoke builds. Revisit `pyside6-deploy` later only if the QML import scanner subprocess issue is resolved. Do not treat the smoke artifact as a release build.



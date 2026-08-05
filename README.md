# AniCompass

AniCompass is a desktop anime recommendation and watch-list app built with
Python and PySide6/QML.

It helps users search real anime catalog data, save a local watch list, configure
an OpenAI-compatible AI provider, generate catalog-verified recommendations, keep
recent recommendation history, and export/restore local data backups.

## Current Features

- Real anime catalog search through Jikan / MyAnimeList metadata.
- Local watch list with plan-to-watch, watching, completed, progress, score, and
  notes.
- AI provider configuration for OpenAI-compatible chat completion endpoints.
- Secure API-key storage through the operating-system keyring.
- AI recommendations that are verified against catalog results before display.
- Latest 10 recommendation history sessions stored locally.
- Versioned JSON backup and restore for local watch-list/history data.
- Chinese/English UI switch and user-adjustable RGB accent color.

## Privacy And Security

- API keys are stored only through `keyring` and are not written to SQLite,
  settings files, logs, tests, screenshots, or backups.
- Backups include local watch-list and recommendation-history data only.
- AI output is not trusted as catalog fact; recommendation candidates are
  verified through the catalog layer before being shown as results.

## Requirements

- Python 3.12+
- Windows for the current tested desktop workflow
- Network access for real catalog search and AI provider calls
- A compatible AI provider API key for recommendation generation

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Run From Source

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python -m anicompass.main
```

Smoke-test QML loading without entering the GUI loop:

```powershell
$env:QT_QPA_PLATFORM='offscreen'
$env:PYTHONPATH='src'
.\.venv\Scripts\python -m anicompass.main --smoke-test
```

## Quality Checks

```powershell
.\.venv\Scripts\python -m ruff check . --no-cache
.\.venv\Scripts\python -m pytest -q -p no:cacheprovider -p no:anyio
.\.venv\Scripts\pyside6-qmllint src\anicompass\ui\Main.qml
```

Current verified state: 72 pytest checks pass. QML lint syntax passes with
existing non-blocking unqualified-access warnings.

## Packaging Status

Windows `.exe` packaging is available at `dist/AniCompass/AniCompass.exe` after
running PyInstaller locally. The current packaged smoke test passes.

Current Windows executable SHA256:

```text
879FEE8B2DA24C0A4BE90FEAD9009502B838285E9CA706952ED3354E8B2FADD6
```

The source repository ignores `build/` and `dist/` by default; publish binary
artifacts through GitHub Releases after a final release review.

macOS `.app` packaging is planned after the Windows release candidate.

## Project Docs

Development requirements, architecture, design standards, security rules,
roadmap, execution workflow, and phase notes live in `docs/`.

Daily development notes live in `dev-logs/`.

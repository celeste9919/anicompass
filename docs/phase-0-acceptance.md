# Phase 0 Acceptance Checklist

Status: Phase 0 decisions complete; ready for Phase 1 after user approval

## Toolchain

- [x] Python 3.12 runtime is available.
- [x] Local `.venv` created.
- [x] Phase 0 dependencies installed and pinned.
- [x] Minimal PySide6/QML window source created.
- [x] QML loads in offscreen smoke-test mode.
- [x] Windows packaging smoke-test artifact launches with PyInstaller fallback.

## Catalog Provider

- [x] Provider-neutral catalog interface decision retained.
- [x] Candidate review documented for Jikan, AniList, and TMDB.
- [x] User confirms v1 catalog scope: Japanese/Asian anime first.
- [x] First adapter strategy selected: Jikan-only for v1.
- [x] Catalog rate-limit behavior specified for the future Jikan adapter.
- [x] Terms and attribution requirements recorded for future UI/about page planning.

## AI Provider

- [x] Real-provider-only rule documented.
- [x] Multiple AI provider categories confirmed.
- [x] Initial service preset list confirmed: OpenAI, DeepSeek, Alibaba Cloud Model Studio/Qwen, and custom compatible endpoint.
- [x] Custom endpoint validation rules documented for later implementation.

## Phase 0 Exit Gate

Phase 0 completion criteria:

1. Catalog scope/provider strategy is confirmed.
2. A Windows packaging smoke test is completed or the blocker is documented.
3. The final Phase 0 decision is logged.






# AniCompass Project Guide

This repository is developed in small, verifiable stages. Read the linked
standards before changing code. Do not start a later phase while the current
phase has failing checks or unresolved acceptance criteria.

## Source Of Truth

1. Product requirements: `docs/01-product-requirements.md`
2. Technical architecture: `docs/02-technical-architecture.md`
3. UI and interaction rules: `docs/03-ui-design-spec.md`
4. Data, security, and AI rules: `docs/04-data-security-ai.md`
5. Development roadmap: `docs/05-development-roadmap.md`
6. Engineering quality rules: `docs/06-engineering-quality.md`
7. Testing and release rules: `docs/07-testing-release.md`
8. Execution workflow: `docs/08-execution-workflow.md`
9. Future change impact: `docs/09-change-impact.md`
10. Full design package: `docs/AI 编程项目 LLM 开发设计包.md`
11. Documentation index: `docs/README.md`

When documents conflict, use this priority:

1. Confirmed product requirements
2. Security and privacy rules
3. Current phase acceptance criteria
4. Technical architecture
5. UI and engineering conventions

Do not silently change a confirmed requirement. Record proposed changes in the
daily log and update the affected standard only after user confirmation.

## Required Work Cycle

At the beginning of every active development day:

```powershell
python scripts/dev_log.py ensure
```

Before editing:

1. Read the current phase in `docs/05-development-roadmap.md`.
2. Read the standards relevant to the files being changed.
3. Check the latest entry under `dev-logs/`.
4. Define one small goal with explicit acceptance checks.

During work:

1. Keep UI, orchestration, prompts, provider calls, parsing, and storage in
   separate modules.
2. Do not implement unconfirmed features.
3. Do not add mock runtime AI recommendations or fake catalog data.
4. Never put API keys in source code, logs, screenshots, fixtures, exports, or
   backup files.
5. Stop and fix failures before moving to another phase.

At the end of every work session:

```powershell
python scripts/dev_log.py add --done "Completed item" --todo "Next item"
```

Add `--decision`, `--blocker`, `--check`, and repeated arguments when needed.
The log must describe real work, checks, failures, fixes, and remaining work.

## Scope Discipline

- Work on only one roadmap phase at a time.
- Prefer a modular monolith over services, plugins, or framework wrappers.
- Add dependencies only when they have a clear owner and test strategy.
- New public interfaces require documentation and tests.
- Do not add login, cloud sync, payments, social features, playback, download,
  or an admin dashboard in v1.
- A catalog provider must not be selected until the Phase 0 review is recorded.

## Completion Rule

A stage is complete only when:

1. Its acceptance criteria are met.
2. Required automated checks pass.
3. A manual smoke test is recorded when UI behavior changed.
4. Documentation reflects any intentional contract change.
5. The daily log contains completed work, checks, and next steps.


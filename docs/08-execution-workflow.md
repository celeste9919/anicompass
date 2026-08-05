# Execution Workflow

This workflow applies to Codex, Claude Code, and human contributors.

## Start Of Day

1. Run `python scripts/dev_log.py ensure`.
2. Read the newest file under `dev-logs/`.
3. Read the active phase in `05-development-roadmap.md`.
4. Choose one small goal that can be verified in the same session.
5. Record assumptions before acting.

## Before A Change

Write down the current phase, exact goal, expected files, excluded features,
acceptance checks, and rollback approach for persisted-data changes.

## During A Change

- Inspect existing code before editing.
- Keep changes within the active module boundary.
- Add tests proportional to risk.
- Run the smallest relevant check early.
- Do not stack multiple unverified subsystems into one change.
- Stop when a product decision is missing.

## End Of Session

1. Run relevant automated checks.
2. Perform required manual checks when UI, credentials, network, or packaging
   changed.
3. Update affected documentation.
4. Append a log entry:

```powershell
python scripts/dev_log.py add `
  --done "Implemented one verified item" `
  --decision "Recorded any design decision" `
  --check "Command and result" `
  --todo "Named next concrete task"
```

5. State whether the current phase is ready or still in progress.

## Small-Step Limits

A normal session should target one module contract, one screen state group, one
repository migration, one provider adapter, one end-to-end path, or one
packaging concern. Avoid combining UI, database, provider, packaging, and a new
feature in one step.

## Approval Gates

User confirmation is required before changing confirmed v1 scope, selecting a
catalog provider with restrictive terms, adding login/cloud sync/analytics/
payments, storing additional personal data, adding plaintext credential
fallback, changing backup compatibility, or introducing a new framework.


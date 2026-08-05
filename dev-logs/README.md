# Development Logs

One file is used per active development day:

```text
dev-logs/YYYY-MM-DD.md
```

Create or locate today's file:

```powershell
python scripts/dev_log.py ensure
```

Append a work-session entry:

```powershell
python scripts/dev_log.py add `
  --done "Completed item" `
  --check "Command or manual check and result" `
  --todo "Next concrete item"
```

Arguments `--done`, `--check`, `--decision`, `--blocker`, and `--todo` may be
repeated. Never record API keys, tokens, authorization headers, or private user
text.


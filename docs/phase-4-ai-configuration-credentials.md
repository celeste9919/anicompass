# Phase 4 AI Configuration And Credentials

Date: 2026-08-04  
Status: Provider config models, keyring credential boundary, AIConfigBridge, and Settings-page AI controls implemented

## Scope

This step adds the local configuration and secure credential boundary for future
AI recommendation calls. It does not call any AI provider yet and does not store
API keys in settings, SQLite, logs, backups, or tests.

## Implemented

- `AIProviderType` for OpenAI, DeepSeek, Qwen, and custom compatible endpoints.
- `AIProviderConfig` for non-secret provider settings: provider id, display
  name, base URL, model name, and timeout.
- Editable OpenAI-compatible provider presets without API keys.
- `CredentialService` backed by Python `keyring` by default.
- Injected credential backend protocol so tests never write real OS secrets.
- Stable credential error codes for empty secret, invalid provider id, and
  unavailable keyring backend.
- `AIConfigBridge` exposing provider presets, selected provider, saved-key state,
  save/delete API-key actions, background provider connection testing, and
  localized status text to QML.
- Settings-page AI provider selector, password input, save key button, delete key
  button, test connection button, and saved/error/connection status text.
- `OpenAICompatibleChatClient` for real `/chat/completions` requests with
  Authorization header, timeout handling, response parsing, and stable provider
  error mapping.
- Connection-test client method using the same real provider path, with tests
  based on `httpx.MockTransport`.

## Files

- `src/anicompass/ai/__init__.py`
- `src/anicompass/ai/models.py`
- `src/anicompass/ai/providers.py`
- `src/anicompass/ai/credentials.py`
- `src/anicompass/ai/client.py`
- `src/anicompass/ai/bridge.py`
- `src/anicompass/main.py`
- `src/anicompass/ui/Main.qml`
- `tests/test_ai_credentials.py`
- `tests/test_ai_config_bridge.py`
- `tests/test_ai_client.py`

## Acceptance Checks

```powershell
.\.venv\Scripts\python -m ruff check . --no-cache
.\.venv\Scripts\python -m pytest -q -p no:cacheprovider -p no:anyio
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'; .\.venv\Scripts\python -m anicompass.main --smoke-test
```

Result: passed. Pytest currently covers 53 focused checks.

## Security Rules

- API keys are secret values and must only move through `CredentialService`.
- Provider presets and ordinary app settings must never include API key values.
- Tests must use injected fake credential backends.
- User-facing errors must expose stable error codes/messages, not backend stack
  traces or secret values.

## Next Step

Begin the recommendation prompt/parser/orchestration pipeline.

# Data, Security, And AI Integration

## Data Classification

Ordinary local data includes watch-list records, recommendation history, notes,
ratings, locale, theme, and non-secret provider metadata.

Secrets include API keys and future access tokens. Secrets must never share the
ordinary settings or backup storage path.

## Storage Rules

- Use SQLite transactions for watch-list and history mutations.
- Enable foreign-key checks.
- Store timestamps in UTC and localize only for display.
- Use schema migrations; never mutate tables ad hoc at startup.
- Keep only the latest 10 recommendation sessions.
- Treat imported backups as untrusted input.

## Credential Rules

- Store API keys through the operating-system keyring.
- Never log secret values or full authorization headers.
- Redact likely secret patterns in exception reporting.
- A missing keyring backend is a blocking configuration error; do not fall back
  to plaintext without explicit future approval.
- Backup and diagnostic exports exclude secrets.

## Real AI Rule

Allowed runtime states:

- no API key configured
- loading
- timeout
- provider error
- parse error
- no verified results
- partial verified results

Forbidden runtime behavior:

- hard-coded recommendation results
- random or sample results presented as real
- fake provider responses
- silently replacing failed AI calls with static content

## Provider Contract

All AI adapters implement one provider-neutral contract:

```text
validate_config(config) -> ValidationResult
complete(config, prompt_payload) -> RawAIResponse
```

The user chooses provider, endpoint, and model. Preset model lists are
convenience only and must permit manual model entry because provider catalogs
change.

## Prompt Safety

- Prompts are versioned files, not strings embedded in QML.
- User input is clearly delimited from instructions.
- Ask for structured candidate output.
- AI-provided titles are candidates, not verified facts.
- Reject unsupported fields rather than guessing.
- Limit user text length and response size.

## Catalog Data Rule

- Catalog metadata is authoritative only within the selected provider's scope.
- Record catalog provider and source ID on each item.
- Do not scrape sites that prohibit it.
- Do not bulk mirror a provider database.
- Implement request throttling, retry-after handling, and a small local cache.
- Apply adult-content checks after catalog enrichment, not only before.

## Network Rules

- HTTPS only.
- Explicit connect and read timeouts.
- Bounded retries only for transient failures.
- Respect `Retry-After`.
- Cancellation must stop pending work.
- Never retry authentication or validation failures automatically.

## Backup Rules

Backup contains a schema version, creation timestamp, application version,
watch-list items, recommendation history, and non-secret settings.

Backup excludes API keys, access tokens, raw authorization headers, temporary
network cache, and application logs.

Import flow:

1. Parse into a temporary structure.
2. Validate schema and content limits.
3. Show a summary.
4. Import in one transaction.
5. Roll back completely on failure.

## Logging Rules

- Default logs contain event type, safe error code, and timestamp.
- Do not log complete prompts or raw model responses by default.
- Do not log user notes unless the user explicitly exports diagnostics.
- Diagnostic exports require preview and confirmation.


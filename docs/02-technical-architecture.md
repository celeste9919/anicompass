# Technical Architecture

Status: Planning baseline  
Architecture style: Modular monolith

## Technical Baseline

- Python 3.12 baseline
- PySide6 with Qt Quick/QML for the desktop UI
- SQLite for local structured data
- Python `keyring` for operating-system credential storage
- `httpx` for network calls
- Pydantic models for validated boundaries
- `pytest` and `pytest-qt` for tests
- Ruff for linting and formatting
- `pyside6-deploy` as the preferred packaging path
- PyInstaller retained only as a documented fallback

Dependency versions are pinned when the project is initialized. Upgrades happen
in isolated maintenance work, not during feature phases.

## Runtime Data Flow

```text
QML UI
  -> ViewModel
  -> Input validation
  -> Recommendation orchestrator
  -> AI provider adapter
  -> Candidate parser
  -> Catalog provider adapter
  -> Result merger and policy filter
  -> ViewModel
  -> QML result display
```

Local list updates use:

```text
QML UI -> WatchList ViewModel -> WatchList Service -> SQLite Repository
```

Secrets use:

```text
Settings UI -> Credential Service -> OS keyring
```

## Module Contracts

### Module: AppShell

**Responsibility**
- Own navigation, global language, theme, and top-level application states.

**Non-responsibility**
- Must not call AI, catalog, or database clients.

**Input**
- View models and global settings.

**Output**
- User navigation and global commands.

**Public interface**
- `show_page(name)`
- `show_error(error_view)`
- `apply_locale(locale)`
- `apply_theme(theme)`

**Hidden internals**
- QML component composition and window behavior.

**Dependencies**
- SettingsViewModel, navigation registry.

**Extension points**
- Future account or export pages.

**Run/test focus**
- Navigation, resize behavior, language switching, and non-overlapping states.

### Module: RecommendationViewModel

**Responsibility**
- Translate UI actions into recommendation use-case requests and expose state.

**Non-responsibility**
- Must not build prompts or make network calls.

**Input**
- Preference form values and user commands.

**Output**
- Idle, validating, loading, success, empty, and error states.

**Public interface**
- `request_recommendations(form)`
- `cancel_request()`
- `add_to_watch_list(item_id)`

**Hidden internals**
- UI state transitions and async task ownership.

**Dependencies**
- RecommendationOrchestrator, ErrorPresenter.

**Extension points**
- Retry, result export, and session comparison.

**Run/test focus**
- State transitions, cancellation, duplicate actions, and error recovery.

### Module: ValidationService

**Responsibility**
- Validate recommendation, settings, list, and backup inputs.

**Non-responsibility**
- Must not display UI or alter storage.

**Input**
- Typed request candidates.

**Output**
- Validated models or structured validation errors.

**Public interface**
- `validate_recommendation_input(data)`
- `validate_provider_config(data)`
- `validate_watch_item(data)`
- `validate_backup_manifest(data)`

**Hidden internals**
- Length limits, incompatible combinations, and normalization rules.

**Dependencies**
- Domain models only.

**Extension points**
- Additional safety filters and provider-specific validation.

**Run/test focus**
- Boundary values, empty values, malformed URLs, and unsafe file paths.

### Module: RecommendationOrchestrator

**Responsibility**
- Coordinate validation, AI candidates, catalog enrichment, policy filtering,
  result assembly, and history persistence.

**Non-responsibility**
- Must not render UI or contain provider SDK details.

**Input**
- `RecommendationRequest`.

**Output**
- `RecommendationSession` or typed domain error.

**Public interface**
- `recommend(request)`

**Hidden internals**
- Retry policy, partial-result rules, timeout coordination, and deduplication.

**Dependencies**
- PromptBuilder, AIProviderRegistry, ResultParser, CatalogService,
  RecommendationPolicy, HistoryService.

**Extension points**
- Batch comparison and shareable exports.

**Run/test focus**
- Partial failures, duplicates, cancellation, timeout, and no-fake-result rule.

### Module: PromptBuilder

**Responsibility**
- Build versioned prompts requesting candidate identities and explanations.

**Non-responsibility**
- Must not call providers or include catalog facts it cannot verify.

**Input**
- `RecommendationRequest` and locale.

**Output**
- Provider-neutral `PromptPayload`.

**Public interface**
- `build_recommendation_prompt(request, locale)`

**Hidden internals**
- Prompt wording, schema instructions, and prompt version.

**Dependencies**
- Domain models.

**Extension points**
- Review analysis and alternative recommendation strategies.

**Run/test focus**
- Required fields, injection-resistant delimiters, locale, and schema contract.

### Module: AIProviderRegistry

**Responsibility**
- Resolve a configured provider adapter and expose one stable call contract.

**Non-responsibility**
- Must not store API keys or parse domain recommendation results.

**Input**
- `AIProviderConfig` and `PromptPayload`.

**Output**
- `RawAIResponse`.

**Public interface**
- `list_provider_types()`
- `validate_config(config)`
- `complete(config, payload)`

**Hidden internals**
- SDK or HTTP request formats and provider error mapping.

**Dependencies**
- CredentialService, HTTP client.

**Extension points**
- New provider adapters without changing UI or orchestration.

**Run/test focus**
- Missing credentials, timeout, authentication, rate limit, and redaction.

### Module: ResultParser

**Responsibility**
- Parse and validate raw AI output into candidate recommendations.

**Non-responsibility**
- Must not treat AI text as verified catalog facts.

**Input**
- `RawAIResponse`.

**Output**
- List of `RecommendationCandidate` or parse error.

**Public interface**
- `parse_candidates(response)`

**Hidden internals**
- JSON extraction, schema repair limits, and rejection reasons.

**Dependencies**
- Pydantic domain schemas.

**Extension points**
- Future response schema versions.

**Run/test focus**
- Malformed JSON, missing fields, duplicates, and adversarial text.

### Module: CatalogService

**Responsibility**
- Search catalog providers, resolve candidate identity, and normalize metadata.

**Non-responsibility**
- Must not generate AI recommendations or own watch-list state.

**Input**
- Search query or `RecommendationCandidate`.

**Output**
- `CatalogAnime` or structured no-match/ambiguous result.

**Public interface**
- `search(query, filters)`
- `resolve_candidate(candidate)`
- `get_by_id(catalog_id)`

**Hidden internals**
- Provider query syntax, caching, rate-limit handling, and title matching.

**Dependencies**
- CatalogProvider adapter, cache repository, HTTP client.

**Extension points**
- Additional data sources and fallback resolution.

**Run/test focus**
- Ambiguous titles, missing translations, rate limits, and adult filtering.

### Module: RecommendationPolicy

**Responsibility**
- Enforce age level, avoidance tags, data-confidence, and duplicate rules.

**Non-responsibility**
- Must not call AI or alter source metadata.

**Input**
- Enriched candidates and user safety preferences.

**Output**
- Accepted results plus explicit rejection reasons.

**Public interface**
- `filter_results(items, preferences)`

**Hidden internals**
- Safety mappings and confidence thresholds.

**Dependencies**
- Domain models.

**Extension points**
- Regional policy profiles.

**Run/test focus**
- Adult-content exclusion, avoidance tags, unknown ratings, and false certainty.

### Module: WatchListService

**Responsibility**
- Create, update, list, and remove local watch-list entries.

**Non-responsibility**
- Must not fetch AI recommendations.

**Input**
- Catalog identity and user-owned status/progress/rating/note changes.

**Output**
- Validated `WatchListItem` records.

**Public interface**
- `add_item(catalog_anime)`
- `update_item(item_id, patch)`
- `list_items(filter)`
- `remove_item(item_id)`

**Hidden internals**
- Transaction handling and duplicate prevention.

**Dependencies**
- WatchListRepository, ValidationService.

**Extension points**
- Cloud repository implementation after login is approved.

**Run/test focus**
- Transactions, progress boundaries, duplicate titles, and sorting.

### Module: HistoryService

**Responsibility**
- Persist, list, and delete the most recent 10 recommendation sessions.

**Non-responsibility**
- Must not rerun recommendations.

**Input**
- Completed recommendation sessions.

**Output**
- Ordered history records.

**Public interface**
- `save_session(session)`
- `list_sessions()`
- `delete_session(session_id)`

**Hidden internals**
- Ten-item retention and cleanup transaction.

**Dependencies**
- HistoryRepository.

**Extension points**
- Search and cloud history.

**Run/test focus**
- Retention order, deletion, and corrupted record handling.

### Module: SettingsService

**Responsibility**
- Persist non-secret locale, theme, provider metadata, and user preferences.

**Non-responsibility**
- Must not store API key values.

**Input**
- `AppSettings`.

**Output**
- Validated current settings.

**Public interface**
- `load_settings()`
- `save_settings(settings)`
- `reset_settings()`

**Hidden internals**
- Settings schema migration.

**Dependencies**
- SettingsRepository.

**Extension points**
- Additional appearance and accessibility preferences.

**Run/test focus**
- Defaults, migration, invalid values, and theme persistence.

### Module: CredentialService

**Responsibility**
- Store, retrieve, replace, and delete provider secrets through the OS keyring.

**Non-responsibility**
- Must not return secrets to logs or backup services.

**Input**
- Provider identifier and secret value.

**Output**
- Success state or typed credential error.

**Public interface**
- `set_api_key(provider_id, value)`
- `has_api_key(provider_id)`
- `get_api_key(provider_id)`
- `delete_api_key(provider_id)`

**Hidden internals**
- Keyring service names and backend behavior.

**Dependencies**
- Python keyring backend.

**Extension points**
- Hardware-backed or enterprise secret stores.

**Run/test focus**
- Redaction, missing keyring backend, replacement, and deletion.

### Module: BackupService

**Responsibility**
- Export and import versioned local data without secrets.

**Non-responsibility**
- Must not read or export API keys.

**Input**
- User-selected file path and local repositories.

**Output**
- `BackupResult` or safe import validation error.

**Public interface**
- `export_backup(path)`
- `inspect_backup(path)`
- `import_backup(path, mode)`

**Hidden internals**
- Archive format, checksums, and transaction rollback.

**Dependencies**
- Repositories, ValidationService.

**Extension points**
- Selective backup and encrypted user archives.

**Run/test focus**
- Path safety, malformed files, schema versions, rollback, and secret absence.

### Module: ErrorPresenter

**Responsibility**
- Convert typed errors into localized, actionable user messages.

**Non-responsibility**
- Must not expose raw secrets, stack traces, or provider response bodies.

**Input**
- Domain and infrastructure errors.

**Output**
- `ErrorViewModel`.

**Public interface**
- `present(error, locale)`

**Hidden internals**
- Error-code mapping and safe diagnostic identifiers.

**Dependencies**
- I18nService.

**Extension points**
- Optional user-approved diagnostic export.

**Run/test focus**
- Redaction, localization, retry guidance, and unknown errors.

## Catalog Provider Decision Gate

Do not bind business logic directly to a catalog API. Phase 0 must compare
candidate providers for geographic coverage, translated titles, cover usage
rights, content ratings, public/commercial terms, request limits, reliability,
identity stability, and desktop compatibility.

The result is recorded as an architecture decision before Phase 2 begins.

## Packaging Rule

Windows and macOS packages are built on their own operating systems. The
application code remains shared; build outputs and signing steps are
platform-specific.


# Phase 2 Catalog Search

Date: 2026-08-04  
Status: Catalog backend, Search view-model, Qt bridge, QML Search screen, and result detail selection connected

## Scope

Phase 2 now connects the Search screen to the real catalog path through clear
layers. It does not cache results, does not write to a database, does not edit
the watch list, and does not return sample or fake anime data.

## Official Provider Basis

- Jikan REST API v4 docs: `https://docs.api.jikan.moe/`
- Search endpoint used by the adapter: `GET /v4/anime`
- Detail endpoint used by the adapter: `GET /v4/anime/{id}`
- Documented public limits retained in code: 3 requests per second and 60
  requests per minute.

## Implemented

- Provider-neutral catalog models and typed catalog errors.
- `JikanCatalogProvider` using injectable `httpx.AsyncClient`.
- Minimal in-process request pacing with `JikanRateLimiter`.
- Jikan response normalization for titles, synopsis, image URL, type, episodes,
  score, rating, season/year, genres, studios, source URL, and attribution.
- Error mapping for timeout, offline/network failure, invalid request, not
  found, rate limit, provider unavailable, and unexpected provider payloads.
- `CatalogService` wrapper that trims/validates user search input, routes by
  provider source, preserves provider error payloads, and hides adapter details
  from UI/view-model code.
- `SearchViewModel` with stable `idle`, `loading`, `success`, `empty`, and
  `error` states, plus provider-id-based result selection.
- `SearchBridge` as the Qt-facing QML boundary. It runs search work on a single
  background thread so the QML window can enter loading state without blocking.
- QML Search screen with real query input, search action, status text, busy
  indicator, result rows bound to `searchBridge.items`, selected-row highlighting,
  and a detail panel bound to `searchBridge.selectedItem`.
- App startup now injects both `settingsService` and `searchBridge` into QML.

## No-Fake-Results Rule

All tests use `httpx.MockTransport` or local provider/service doubles. Runtime
adapter methods perform real HTTP calls when a real client is used. There are no
hardcoded anime search results or sample fallback records in runtime code.

## Files

- `src/anicompass/catalog/__init__.py`
- `src/anicompass/catalog/models.py`
- `src/anicompass/catalog/provider.py`
- `src/anicompass/catalog/service.py`
- `src/anicompass/search/__init__.py`
- `src/anicompass/search/viewmodel.py`
- `src/anicompass/search/bridge.py`
- `src/anicompass/main.py`
- `src/anicompass/ui/Main.qml`
- `tests/test_catalog_contract.py`
- `tests/test_catalog_service.py`
- `tests/test_search_viewmodel.py`
- `tests/test_search_bridge.py`
- `scripts/catalog_smoke.py`

## Acceptance Checks

```powershell
.\.venv\Scripts\python -m ruff check . --no-cache
.\.venv\Scripts\python -m pytest -q -p no:cacheprovider -p no:anyio
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'; .\.venv\Scripts\python -m anicompass.main --smoke-test
$env:QT_QPA_PLATFORM='offscreen'; .\dist\AniCompassSmoke\AniCompassSmoke.exe --smoke-test
```

Result: passed. Pytest currently covers 29 focused checks.

## Current Test Coverage

- Provider-neutral anime model validation.
- Search filter validation.
- Jikan search URL/query parameters.
- Search response normalization.
- Detail response normalization.
- 429 retry-after mapping.
- Timeout mapping.
- 5xx provider-unavailable mapping, including HTTP 504.
- AI candidate resolution prefers matching year.
- CatalogService trims and validates search input.
- CatalogService routes search/detail/candidate resolution by provider source.
- CatalogService reports missing providers as typed not-implemented errors.
- CatalogService preserves provider error payloads.
- SearchViewModel initial/reset, success, empty, error, duplicate-submit, and
  result selection/clear-selection states.
- SearchBridge loading-to-success state, QML-friendly result conversion, selected
  item exposure, and clear/reselect behavior.
- QML Search page loads with injected bridge and exposes search controls, result
  list, and detail panel controls.
- Existing Phase 1 app shell and settings persistence checks.


## Real Network Smoke

A controlled real-network smoke script is available:

```powershell
.\.venv\Scripts\python scripts\catalog_smoke.py --query "cowboy bebop" --limit 3
```

Current environment result on 2026-08-04:

- sandboxed run: `offline`, Jikan unreachable
- escalated network run attempt 1: HTTP 504 from Jikan
- escalated network run attempt 2: `offline`, Jikan unreachable

The adapter test suite still covers successful Jikan responses and error
mapping through `httpx.MockTransport`. Treat the real-network smoke as pending
external/network availability, not as a completed provider availability proof.

## Packaging Notes

The Windows PyInstaller smoke bundle was rebuilt after QML Search selection/detail
connection. The packaged QML contains `searchPanel`, `searchBridge`, result-list,
and detail-panel markers.
PyInstaller still reports optional dependency warnings from PySide6/Pydantic/httpx
analysis; the packaged smoke test passes.

## Next Step

Continue Phase 2 by adding a controlled real-network search smoke command or a
small Search visual QA artifact. After that, add a lightweight search result
selection/detail boundary before moving toward watch-list persistence.
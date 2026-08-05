# Phase 3 Local Watch List

Date: 2026-08-04  
Status: SQLite backend, WatchListBridge, add-from-search, and minimal My List UI connected

## Scope

Phase 3 now connects local persistence to the QML shell through a Qt bridge.
The My List screen can display, filter, and delete local records, and the Search
detail panel can add the selected real catalog item to the local list. This step
does not call AI providers and does not store recommendation history.

## Implemented

- `WatchStatus` with `plan_to_watch`, `watching`, and `completed` states.
- `WatchListItem`, `WatchListUpdate`, and `WatchListFilter` Pydantic models.
- SQLite schema version `1` with `watch_list_items` table.
- Unique constraint on `(catalog_source, provider_id)` to prevent duplicate
  local entries for the same catalog item.
- `SQLiteWatchListRepository` for migration, add, get, find-by-catalog-id,
  list/filter, update, and remove operations.
- `WatchListService` for user-facing add/update/list/remove flow.
- Validation for progress range, 10-point score, notes length, and typed status.
- `WatchListBridge` with QML-facing list items, status filtering, add-from-catalog, delete, and localized status text.
- Search detail panel `Add to List` action bound to `watchListBridge.addFromCatalogItem(searchBridge.selectedItem)`.
- My List screen with status filters, local record list, count/error status, and delete action.
- Startup injection for `watchListBridge`, with database path fallback when the default OS config directory is not writable.

## Files

- `src/anicompass/watchlist/__init__.py`
- `src/anicompass/watchlist/models.py`
- `src/anicompass/watchlist/repository.py`
- `src/anicompass/watchlist/service.py`
- `src/anicompass/watchlist/bridge.py`
- `src/anicompass/main.py`
- `src/anicompass/ui/Main.qml`
- `tests/test_watchlist_service.py`
- `tests/test_watchlist_bridge.py`

## Acceptance Checks

```powershell
.\.venv\Scripts\python -m ruff check . --no-cache
.\.venv\Scripts\python -m pytest -q -p no:cacheprovider -p no:anyio
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'; .\.venv\Scripts\python -m anicompass.main --smoke-test
$env:QT_QPA_PLATFORM='offscreen'; .\dist\AniCompassSmoke\AniCompassSmoke.exe --smoke-test
```

Result: passed. Pytest currently covers 39 focused checks.

## Current Test Coverage

- SQLite schema migration version.
- Add and reload from a real temporary SQLite database.
- Duplicate catalog item prevention.
- Status, progress, score, and notes update flow.
- Status-based filtering.
- Invalid progress and score rejection.
- Delete flow and not-found behavior.
- WatchListBridge add/filter/delete behavior and duplicate user-facing error.
- QML My List controls load through an injected bridge.

## Boundaries

- The repository owns SQLite details and transaction boundaries.
- The service owns the business flow and converts `CatalogAnime` into local
  watch-list records.
- The QML UI binds through `WatchListBridge` and does not call the repository directly.
- No API keys, AI responses, or recommendation history are stored here.

## Next Step

Add edit controls for status/progress/score/notes in the My List screen, then
verify persistence after restart through the QML boundary.

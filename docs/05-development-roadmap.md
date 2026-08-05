# Development Roadmap

Principle: one small phase at a time. A phase does not start until the previous
phase passes its gate.

## Phase 0: Provider And Feasibility Decisions

Goal:

- Validate the desktop toolchain.
- Compare catalog providers.
- Confirm AI provider adapter categories.
- Record packaging and licensing constraints.

Deliverables:

- minimal PySide6/QML window
- provider comparison note
- architecture decision for catalog provider
- dependency lock baseline
- Windows build smoke test

Do not do:

- recommendation UI
- database schema
- real product screens

Acceptance:

- window launches on Windows
- QML loads from packaged resources
- chosen catalog approach has documented coverage, terms, rate limits, and
  fallback behavior
- no unresolved blocker to Windows packaging

## Phase 1: Application Shell And Design System

Goal:

- Build navigation, localization, theme state, color picker, and required UI
  states without fake content.

Deliverables:

- AppShell
- Recommend/Search/List/History/Settings empty screens
- Chinese and English resources
- persisted non-secret settings
- accessible theme derivation

Do not do:

- AI calls
- catalog calls
- watch-list persistence

Acceptance:

- navigation and resize checks pass
- language switches globally
- selected accent persists after restart
- empty/loading/error components render without overlap

## Phase 2: Catalog Search

Goal:

- Implement real catalog search and normalized result display.

Deliverables:

- CatalogProvider interface
- selected provider adapter
- catalog cache
- search screen
- detail summary

Do not do:

- AI recommendations
- watch-list edits

Acceptance:

- real search results render
- ambiguous and empty results are handled
- content policy filtering is applied
- timeout, offline, and rate-limit states are verified

## Phase 3: Local Watch List

Goal:

- Add reliable local list management.

Deliverables:

- SQLite schema and migrations
- repository and WatchListService
- status tabs
- progress, 10-point score, notes, and delete flow

Do not do:

- recommendation history
- backup import/export

Acceptance:

- create, update, restart, reload, and delete flows pass
- duplicate items are prevented
- invalid progress and score values are rejected
- migration test passes

## Phase 4: AI Configuration And Secure Credentials

Goal:

- Support provider settings and secure local API-key storage.

Deliverables:

- provider registry
- initial adapters
- custom compatible endpoint
- keyring-based CredentialService
- provider connection test

Do not do:

- recommendation generation UI
- plaintext credential fallback

Acceptance:

- API keys never enter SQLite or logs
- missing keyring backend fails safely
- connection tests return clear provider errors
- secrets are deleted when the user requests removal

## Phase 5: AI Recommendation Pipeline

Goal:

- Complete the real recommendation flow with verified catalog enrichment.

Deliverables:

- input validation
- versioned prompt
- AI call
- structured parser
- catalog candidate resolution
- content policy filter
- recommendation result UI

Do not do:

- fake fallback results
- save history until the result contract is stable

Acceptance:

- 3, 5, and 10 result requests work
- missing or ambiguous candidates are explicit
- no catalog fact is accepted only because the AI said it
- cancellation, timeout, parse error, and partial success work

## Phase 6: Recommendation History

Goal:

- Save and manage the latest 10 verified recommendation sessions.

Deliverables:

- history schema and service
- history page
- delete and retention behavior

Acceptance:

- latest 10 retention is deterministic
- old records are removed transactionally
- deleted history does not affect watch-list entries

## Phase 7: Backup And Restore

Goal:

- Provide safe local data portability.

Deliverables:

- versioned backup format
- export, inspect, confirm, import, and rollback
- user-facing validation errors

Acceptance:

- round-trip backup test passes
- malformed backup cannot alter current data
- API keys are absent from exported bytes
- import rollback is proven

## Phase 8: Windows Packaging And Release Candidate

Goal:

- Produce a Windows release candidate.

Deliverables:

- packaged `.exe`
- icon and metadata
- clean-machine smoke-test checklist
- license notices
- known limitations

Acceptance:

- launches without Python installed
- no console window in normal use
- settings, database, keyring, network, and backup flows pass
- installer or package is scanned and checksummed

## Phase 9: macOS Packaging

Goal:

- Produce and verify the macOS `.app`.

Deliverables:

- macOS build configuration
- `.app` bundle
- signing/notarization decision
- macOS smoke-test report

Acceptance:

- built on macOS
- app launches on supported target versions
- keychain and local file access work
- packaging differences are documented

## Phase 10: Post-v1 Enhancements

Order:

1. shareable recommendation export
2. richer detail and viewing-order guidance
3. AI review analysis
4. account and cloud sync

Each item requires a separate requirement confirmation and roadmap update.


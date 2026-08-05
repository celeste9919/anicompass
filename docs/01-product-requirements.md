# AniCompass Product Requirements

Status: Confirmed baseline for planning  
Last updated: 2026-08-04

## Product Definition

AniCompass is a public-facing desktop application for AI-assisted Japanese and Asian animation recommendations and personal watch-list management. It targets ordinary users
and must remain understandable without technical knowledge.

## Supported Platforms

- Windows desktop package: `.exe`
- macOS desktop package: `.app`
- Windows is developed and verified first.
- macOS is built and verified on macOS, not cross-built from Windows.
- A web edition is outside the v1 scope.

## Core User Flows

### Recommendation Flow

1. The user selects genres, region, era, length, mood, age level, and avoidance
   tags.
2. The user may describe the desired experience in natural language.
3. The user may list liked and disliked titles.
4. The user selects 3, 5, or 10 recommendations; the default is 5.
5. The app validates input and AI configuration.
6. A real AI provider interprets preferences and proposes candidates.
7. A catalog provider verifies and enriches candidate information.
8. The app shows accepted results and clearly reports rejected or unavailable
   data.
9. The user may add a result to a local watch list.

### Search And List Flow

1. The user searches the animation catalog.
2. The user opens a result and adds it to a list.
3. The user sets status, episode progress, a 10-point rating, and notes.
4. The user can edit or remove the item later.

### Backup Flow

1. The user exports local application data to a backup file.
2. API keys and other secrets are excluded.
3. The user can import a valid backup after confirmation.
4. Invalid or newer unsupported backup formats must not overwrite current data.

## Recommendation Result

Each result should contain, when the catalog provides it:

- localized display title
- original title
- cover image
- region or country of origin
- genres and tags
- release year
- episode count and format
- synopsis
- AI recommendation reason
- suitable audience
- content warnings
- viewing order when relevant and verifiable

Missing catalog fields are displayed as unavailable, never invented as facts.

## V1 Catalog Scope

- V1 focuses on Japanese and Asian anime.
- Data providers should be selected for anime-focused coverage first.
- Global animation coverage is a later expansion and must not block v1.
- The catalog layer must still remain provider-neutral so global providers can
  be added later without rewriting recommendation, watch-list, or UI logic.

## Local Watch List

Statuses:

- Plan to watch
- Watching
- Completed

Per-item data:

- catalog identity
- status
- watched episode count
- optional score from 1 to 10
- optional note
- created and updated timestamps

## Recommendation History

- Keep the most recent 10 recommendation sessions.
- Permit viewing and deleting individual sessions.
- Remove the oldest session when the limit is exceeded.
- Store history only on the local device.

## Language And Appearance

- Global Chinese and English UI switch.
- Chinese UI prefers a Chinese title when available.
- English UI prefers an English title when available.
- Always retain an original title when the source provides one.
- Use a light, clean, approachable desktop layout.
- Include a color picker for the accent theme.
- Persist language and theme preferences locally.

## AI Configuration

- Support preset domestic and international providers.
- Support a custom compatible endpoint.
- Let users enter provider, endpoint, model name, and API key.
- Do not hard-code claims about a provider's latest model.
- Missing credentials produce a configuration state, not a fake result.

## Privacy And Safety

- No account is required.
- Do not collect email, age, identity, or behavioral analytics in v1.
- API credentials are secrets even though ordinary profile data is not stored.
- Provide age-level filtering and avoidance tags.
- Do not include API keys in logs, backups, exports, screenshots, or exceptions.

## V1 Exclusions

- login and cloud sync
- social features
- payments or usage quotas
- admin dashboard
- animation playback or downloading
- automated episode notifications
- AI review analysis
- user-created catalog entries
- online recommendation sharing

## Later Candidates

1. Shareable image or Markdown recommendation exports
2. Richer detail and viewing-order guidance
3. AI review analysis
4. Account-based multi-device sync
5. Global animation coverage through additional catalog providers

## Open Product Constraints

- Exact provider presets and default model names require a current provider
  review before implementation.
- Public distribution signing and notarization require platform-specific
  accounts and are release concerns, not v1 feature logic.







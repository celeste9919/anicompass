# Phase 0 Catalog Strategy Decision

Date: 2026-08-04  
Decision: Use Jikan-only as the first v1 catalog adapter.

## Decision Summary

AniCompass v1 will focus on Japanese and Asian anime. The first catalog adapter
will use Jikan only. AniList remains a later enrichment or fallback candidate,
and TMDB remains a future global-animation expansion candidate.

## Why Jikan First

- It is anime-focused and fits the narrowed v1 scope.
- It is read-only, which matches AniCompass because the app owns its local watch
  list instead of writing to an external list service.
- It does not require a user API key, so Phase 2 can validate real catalog
  search without adding credential configuration.
- It documents clear limits: 3 requests per second and 60 requests per minute.
- It returns useful fields for v1: MyAnimeList ID, title, English title,
  Japanese title, synonyms, type, episodes, rating, score, synopsis, aired
  dates, season/year, images, genres, studios, and related entries.

Official references:

- `https://docs.api.jikan.moe/`
- `https://docs.jikan.moe/objects/model/anime/anime/`

## Why Not AniList In The First Adapter

AniList is technically useful, but it is not chosen as the first adapter because
its terms and reliability profile add extra review work for a beginner-friendly
v1.

Reasons:

- AniList terms prohibit using the API as backup/data storage.
- AniList terms restrict competing list/tracker services unless authorized.
- AniCompass contains local list/tracker features, so usage must be carefully
  reviewed before integration.
- Current API documentation notes a degraded limit of 30 requests per minute,
  with 90 requests per minute as the normal documented limit.

Official references:

- `https://anilist.gitbook.io/anilist-apiv2-docs/docs/guide/terms-of-use`
- `https://docs.anilist.co/guide/rate-limiting`

## Implementation Rule For Phase 2

When Phase 2 begins, implement a provider-neutral `CatalogProvider` interface
and a concrete `JikanCatalogProvider` adapter. Do not let UI or watch-list code
import Jikan-specific response shapes directly.

The adapter must provide:

1. `search(query, filters)`
2. `get_by_id(provider_id)`
3. `resolve_candidate(candidate)`
4. normalized `CatalogAnime` objects
5. rate-limit protection for 3 requests per second and 60 requests per minute
6. handling for 304, 400, 404, 405, 429, 500, and 503 responses
7. source attribution fields for display in About or item details

## Cache Rule

Use a small local cache only for user-facing responsiveness. Do not bulk mirror
Jikan or MyAnimeList data. Respect Jikan cache headers when present.

## Fallback Rule

If Jikan lacks a field:

- show unavailable rather than inventing facts
- keep AI recommendation reasoning separate from verified catalog data
- do not query AniList automatically until a later integration decision is made

## Remaining Phase 0 Work

- Add a Windows packaging smoke-test artifact or document the blocker.
- Confirm whether `pyside6-deploy` or PyInstaller is the first packaging path.

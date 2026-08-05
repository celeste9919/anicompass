# Phase 0 Provider Review

Date: 2026-08-04  
Status: V1 scope confirmed; first adapter strategy selected

## Purpose

AniCompass v1 needs verified Japanese and Asian anime metadata: identity,
localized titles, original titles, covers, release year, episode count, region,
content rating, and tags. AI output is useful for recommendation reasoning, but
must not be the source of truth for catalog facts.

## Candidate: Jikan

Official docs: `https://docs.api.jikan.moe/` and `https://jikan.moe/`

Strengths:

- Free, open-source, unauthenticated REST API.
- Strong anime and manga focus through public MyAnimeList pages.
- Structured endpoints for anime search, details, genres, seasons, top lists,
  recommendations, reviews, characters, staff, producers, and schedules.
- Published rate limits: 3 requests per second and 60 requests per minute.
- Read-only behavior matches AniCompass v1 because AniCompass keeps its own
  local watch list.

Risks:

- It is an unofficial MyAnimeList API and scrapes public MAL pages.
- It is Japanese-anime-first, so it is a good fit for the narrowed v1 scope but
  not enough for future global animation coverage.
- It can still be rate limited by MyAnimeList upstream.
- Cover and metadata usage must be treated cautiously; do not bulk mirror data.

Fit:

- Good Phase 2 prototype provider for anime-focused search.
- Good default starting candidate for the narrowed Japanese/Asian anime v1.
- Keep provider abstraction because global animation remains a later extension.

## Candidate: AniList

Official docs: `https://docs.anilist.co/`

Strengths:

- GraphQL API with strongly shaped queries.
- Anime-focused media data.
- Rate-limit headers are documented.
- Good fit for targeted anime search and metadata enrichment.

Risks:

- API availability is not guaranteed; the docs describe degraded states and
  temporary disabling under severe instability.
- Current documented degraded rate can be 30 requests per minute, with the
  normal limit documented as 90 requests per minute.
- Terms prohibit using AniList as backup/data storage and prohibit hoarding or
  mass collection.
- Terms restrict competing list/tracker services unless authorized. AniCompass
  has local list features, so this must be reviewed carefully before shipping.

Fit:

- Good candidate for additional anime metadata enrichment.
- Do not approve as the default watch-list-linked provider until list/tracker
  terms are reviewed and accepted.

## Candidate: TMDB

Official docs: `https://developer.themoviedb.org/` and
`https://www.themoviedb.org/api-terms-of-use`

Strengths:

- Broad movie and TV metadata, useful for global animation coverage.
- Provides image APIs and documented image URL construction.
- API-wide SSL is documented.

Risks:

- Requires an API key.
- Non-commercial use requires attribution.
- Commercial use requires a commercial agreement.
- Terms restrict cache duration and use of TMDB content in AI/LLM contexts.
- Desktop apps cannot safely embed a shared developer API key as a secret.

Fit:

- Good future candidate for global animation coverage.
- Not required for v1 after narrowing the catalog scope.
- Not suitable for silent built-in shared-key distribution.

## Decision

User decision: v1 will focus on Japanese and Asian anime first.

Approved architecture direction:

1. Keep `CatalogProvider` as a provider-neutral interface.
2. Use an anime-focused provider strategy for v1.
3. Use Jikan as the first Phase 2 implementation adapter.
4. Keep AniList as a secondary candidate pending terms review.
5. Keep TMDB for later global-animation expansion.
6. Prefer user-provided API keys for providers that require keys.
7. Keep a small cache with provider identity and expiry rules.
8. Never bulk mirror catalog data.

## Selected First Adapter Strategy

Use Jikan-only for the first v1 catalog adapter. Keep AniList as a later enrichment or fallback candidate, but do not add it to the first implementation.

Before implementing the adapter:

1. Record attribution and source display requirements.
2. Define rate-limit behavior in the provider adapter.
3. Define fallback behavior for missing Chinese or English titles.
4. Keep all Jikan response shapes behind the `CatalogProvider` interface.

## Phase 0 Exit Requirement

Phase 0 catalog scope is confirmed. Phase 0 catalog work is not fully complete
until the packaging smoke test is completed or its blocker is documented.


# Future Change Impact

## Shareable Recommendation Export

Will change ExportService, result actions, and export templates. It should not
change AI providers, PromptBuilder, CatalogProvider, or WatchListService.
Reserve `export_recommendation(session, format, options)`.

## Richer Detail And Viewing Order

Will change CatalogService, detail pages, and an optional viewing-order
resolver. It should not change credentials, watch-list user fields, or history
retention. Add `RelatedTitle` and `ViewingOrderGroup` with source and
confidence fields.

## AI Review Analysis

Will add a separate ReviewAnalysisOrchestrator, prompt, parser, input screen,
and result screen. It should reuse AIProviderRegistry without changing
WatchListService or CatalogProvider. Add `ReviewAnalysisRequest` and
`ReviewAnalysisResult`.

## Login And Cloud Sync

Will change authentication, cloud repositories, conflict resolution, privacy
documentation, and account settings. It should not change PromptBuilder,
ResultParser, catalog normalization, or the QML component library. Reserve
repository protocols for watch list, history, and settings.

## Additional AI Providers

Add one provider adapter, preset metadata, and provider-specific tests. Do not
change recommendation UI, PromptBuilder, ResultParser, or watch-list storage.
Use the provider-neutral `complete(config, payload)` contract.

## Additional Catalog Providers

Add one catalog adapter, source resolution/fallback policy, and provider cache
rules. Do not change watch-list user fields, AI adapters, theme, or
localization. Use CatalogProvider search, resolve, and get-by-id methods.


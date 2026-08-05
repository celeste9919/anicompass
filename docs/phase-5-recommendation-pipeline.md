# Phase 5 Recommendation Pipeline

Date: 2026-08-04  
Status: Prompt/parser/orchestrator contract, RecommendBridge, and minimal Recommend UI implemented

## Scope

This step creates the tested recommendation pipeline contract without connecting
the Recommend UI yet. It uses the real AI client interface and requires catalog
verification before a recommendation can become user-visible as verified anime
metadata.

## Implemented

- `RecommendationRequest` with preferences, count, UI language, and all-audience
  safety flag.
- Versioned `RecommendationPromptBuilder` that asks for JSON-only AI candidate
  output and explicitly forbids invented catalog ids, scores, episode counts,
  studios, or URLs.
- Strict `RecommendationParser` for AI JSON output.
- `RecommendationOrchestrator` that calls the AI client, parses candidates, and
  verifies each candidate through `CatalogService.resolve_candidate`.
- Explicit unresolved candidate output when catalog verification cannot match a
  recommendation.
- `RecommendBridge` with idle/loading/success/empty/error states, background
  recommendation execution, verified result exposure, unresolved candidate
  exposure, and localized status copy.
- Recommend screen preference input, count selector, action button, loading
  indicator, verified results list, and unresolved count.

## Files

- `src/anicompass/recommendation/__init__.py`
- `src/anicompass/recommendation/models.py`
- `src/anicompass/recommendation/prompt.py`
- `src/anicompass/recommendation/parser.py`
- `src/anicompass/recommendation/orchestrator.py`
- `src/anicompass/recommendation/bridge.py`
- `src/anicompass/main.py`
- `src/anicompass/ui/Main.qml`
- `tests/test_recommendation_pipeline.py`
- `tests/test_recommend_bridge.py`

## Acceptance Checks

```powershell
.\.venv\Scripts\python -m ruff check . --no-cache
.\.venv\Scripts\python -m pytest -q -p no:cacheprovider -p no:anyio
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'; .\.venv\Scripts\python -m anicompass.main --smoke-test
```

Result: passed. Pytest currently covers 59 focused checks.

## No-Fake-Results Rule

The orchestrator does not accept catalog facts directly from AI output. AI may
only propose candidate identity and a reason. The catalog service must verify the
anime record before it enters `RecommendationResult.items`; otherwise the parsed
candidate remains in `RecommendationResult.unresolved`.

## Next Step

Add save-to-watch-list actions from recommendation results and decide the
recommendation history persistence boundary.

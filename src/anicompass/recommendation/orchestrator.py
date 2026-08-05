"""Recommendation orchestration from prompt to catalog verification."""

from __future__ import annotations

from typing import Protocol

from anicompass.ai.models import AIProviderConfig, AIProviderResponse
from anicompass.catalog.models import CatalogAnime, RecommendationCandidate
from anicompass.recommendation.models import (
    RecommendationRequest,
    RecommendationResult,
    VerifiedRecommendation,
)
from anicompass.recommendation.parser import RecommendationParser
from anicompass.recommendation.prompt import RecommendationPromptBuilder


class AICompletionClient(Protocol):
    async def complete(
        self,
        config: AIProviderConfig,
        user_prompt: str,
        *,
        system_prompt: str = ...,
        max_tokens: int = ...,
    ) -> AIProviderResponse: ...


class CandidateCatalogService(Protocol):
    async def resolve_candidate(
        self,
        candidate: RecommendationCandidate,
    ) -> CatalogAnime | None: ...


class RecommendationOrchestrator:
    """Run AI candidate generation and verify identities through catalog data."""

    def __init__(
        self,
        ai_client: AICompletionClient,
        catalog_service: CandidateCatalogService,
        prompt_builder: RecommendationPromptBuilder | None = None,
        parser: RecommendationParser | None = None,
    ) -> None:
        self._ai_client = ai_client
        self._catalog_service = catalog_service
        self._prompt_builder = prompt_builder or RecommendationPromptBuilder()
        self._parser = parser or RecommendationParser()

    async def recommend(
        self,
        request: RecommendationRequest,
        config: AIProviderConfig,
    ) -> RecommendationResult:
        prompt = self._prompt_builder.build(request)
        response = await self._ai_client.complete(
            config,
            prompt,
            max_tokens=1200,
        )
        parsed = self._parser.parse(response.content)[: request.count]
        verified: list[VerifiedRecommendation] = []
        unresolved = []
        for item in parsed:
            anime = await self._catalog_service.resolve_candidate(item.candidate)
            if anime is None:
                unresolved.append(item)
                continue
            verified.append(VerifiedRecommendation(anime=anime, reason=item.reason))
        return RecommendationResult(items=tuple(verified), unresolved=tuple(unresolved))

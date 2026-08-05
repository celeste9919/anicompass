from __future__ import annotations

import asyncio
import json

import pytest

from anicompass.ai import AIProviderConfig, AIProviderResponse, AIProviderType
from anicompass.catalog import CatalogAnime, CatalogAnimeId, CatalogSource
from anicompass.recommendation import (
    RecommendationOrchestrator,
    RecommendationParseError,
    RecommendationParser,
    RecommendationPromptBuilder,
    RecommendationRequest,
)


class AIClientDouble:
    def __init__(self, content: str) -> None:
        self.content = content
        self.prompts: list[str] = []

    async def complete(
        self,
        config: AIProviderConfig,
        user_prompt: str,
        *,
        system_prompt: str = "",
        max_tokens: int = 0,
    ) -> AIProviderResponse:
        self.prompts.append(user_prompt)
        return AIProviderResponse(
            provider_id=config.provider_id,
            model_name=config.model_name,
            content=self.content,
        )


class CatalogServiceDouble:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def resolve_candidate(self, candidate):
        self.calls.append(candidate.title)
        if candidate.title == "Unknown Show":
            return None
        return CatalogAnime(
            catalog_id=CatalogAnimeId(source=CatalogSource.JIKAN, provider_id="1"),
            title=candidate.title,
            year=candidate.year,
        )


def _config() -> AIProviderConfig:
    return AIProviderConfig(
        provider_type=AIProviderType.CUSTOM,
        provider_id="custom",
        display_name="Custom",
        base_url="https://example.com/v1",
        model_name="anime-model",
    )


def _ai_json() -> str:
    return json.dumps(
        {
            "recommendations": [
                {
                    "title": "Cowboy Bebop",
                    "year": 1998,
                    "original_title": "Cowboy Bebop",
                    "reason": "Stylish space western tone.",
                },
                {
                    "title": "Unknown Show",
                    "year": None,
                    "original_title": None,
                    "reason": "May match the mood.",
                },
            ]
        }
    )


def test_recommendation_prompt_requests_json_and_forbids_unverified_facts() -> None:
    prompt = RecommendationPromptBuilder().build(
        RecommendationRequest(preferences="space jazz noir", count=3)
    )

    assert "Return JSON only" in prompt
    assert "Do not invent catalog ids" in prompt
    assert "space jazz noir" in prompt


def test_recommendation_parser_parses_candidates_and_rejects_bad_json() -> None:
    parsed = RecommendationParser().parse(_ai_json())

    assert parsed[0].candidate.title == "Cowboy Bebop"
    assert parsed[0].reason == "Stylish space western tone."

    with pytest.raises(RecommendationParseError):
        RecommendationParser().parse("not json")


def test_recommendation_orchestrator_verifies_candidates_through_catalog() -> None:
    ai_client = AIClientDouble(_ai_json())
    catalog = CatalogServiceDouble()
    orchestrator = RecommendationOrchestrator(ai_client, catalog)

    result = asyncio.run(
        orchestrator.recommend(
            RecommendationRequest(preferences="space jazz noir", count=2),
            _config(),
        )
    )

    assert catalog.calls == ["Cowboy Bebop", "Unknown Show"]
    assert [item.anime.title for item in result.items] == ["Cowboy Bebop"]
    assert [item.candidate.title for item in result.unresolved] == ["Unknown Show"]
    assert ai_client.prompts

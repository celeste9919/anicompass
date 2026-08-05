"""Versioned prompt builder for anime recommendations."""

from __future__ import annotations

import json

from anicompass.recommendation.models import RecommendationRequest

PROMPT_VERSION = "recommendation-v1"


class RecommendationPromptBuilder:
    """Build JSON-focused prompts without claiming unverified catalog facts."""

    def build(self, request: RecommendationRequest) -> str:
        locale = "Chinese" if request.language == "zh" else "English"
        payload = {
            "prompt_version": PROMPT_VERSION,
            "task": (
                "Recommend anime candidates only. "
                "Catalog facts will be verified later."
            ),
            "output_language": locale,
            "count": request.count,
            "safe_for_all_audiences": request.safe_for_all_audiences,
            "user_preferences": request.preferences,
            "required_json_schema": {
                "recommendations": [
                    {
                        "title": "string",
                        "year": "integer or null",
                        "original_title": "string or null",
                        "reason": "string",
                    }
                ]
            },
            "rules": [
                "Return JSON only.",
                "Do not invent catalog ids, scores, episode counts, studios, or URLs.",
                "Avoid adult-only content when safe_for_all_audiences is true.",
            ],
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

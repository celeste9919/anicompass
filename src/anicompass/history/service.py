"""Business service for recommendation history."""

from __future__ import annotations

from anicompass.history.models import RecommendationHistorySession
from anicompass.history.repository import SQLiteHistoryRepository
from anicompass.recommendation.models import RecommendationRequest, RecommendationResult


class HistoryService:
    """Save and manage recent completed recommendation sessions."""

    def __init__(self, repository: SQLiteHistoryRepository) -> None:
        self._repository = repository

    def save_result(
        self,
        request: RecommendationRequest,
        result: RecommendationResult,
    ) -> RecommendationHistorySession:
        session = RecommendationHistorySession(
            preferences=request.preferences,
            language=request.language,
            verified_count=len(result.items),
            unresolved_count=len(result.unresolved),
        )
        return self._repository.save(session)

    def list_sessions(self) -> tuple[RecommendationHistorySession, ...]:
        return self._repository.list_sessions()

    def delete_session(self, session_id: int) -> None:
        self._repository.delete(session_id)

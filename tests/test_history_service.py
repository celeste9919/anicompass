from __future__ import annotations

import pytest

from anicompass.catalog import CatalogAnime, CatalogAnimeId, CatalogSource
from anicompass.history import (
    HISTORY_LIMIT,
    HistoryService,
    HistorySessionNotFoundError,
    SQLiteHistoryRepository,
)
from anicompass.recommendation.models import (
    RecommendationRequest,
    RecommendationResult,
    VerifiedRecommendation,
)


def _request(index: int = 1) -> RecommendationRequest:
    return RecommendationRequest(preferences=f"space jazz noir {index}")


def _result() -> RecommendationResult:
    return RecommendationResult(
        items=(
            VerifiedRecommendation(
                anime=CatalogAnime(
                    catalog_id=CatalogAnimeId(
                        source=CatalogSource.JIKAN,
                        provider_id="1",
                    ),
                    title="Cowboy Bebop",
                ),
                reason="Fits the mood.",
            ),
        )
    )


def test_history_service_saves_and_reloads_sessions(tmp_path) -> None:
    database_path = tmp_path / "anicompass.db"
    repository = SQLiteHistoryRepository(database_path)
    service = HistoryService(repository)

    saved = service.save_result(_request(), _result())
    repository.close()

    reloaded = SQLiteHistoryRepository(database_path)
    try:
        sessions = HistoryService(reloaded).list_sessions()

        assert saved.session_id is not None
        assert len(sessions) == 1
        assert sessions[0].preferences == "space jazz noir 1"
        assert sessions[0].verified_count == 1
    finally:
        reloaded.close()


def test_history_repository_retains_latest_ten_sessions() -> None:
    repository = SQLiteHistoryRepository()
    service = HistoryService(repository)

    for index in range(12):
        service.save_result(_request(index), _result())

    sessions = service.list_sessions()

    assert len(sessions) == HISTORY_LIMIT
    assert sessions[0].preferences == "space jazz noir 11"
    assert sessions[-1].preferences == "space jazz noir 2"
    repository.close()


def test_history_service_deletes_sessions() -> None:
    repository = SQLiteHistoryRepository()
    service = HistoryService(repository)
    saved = service.save_result(_request(), _result())

    service.delete_session(saved.session_id or 0)

    assert service.list_sessions() == ()
    with pytest.raises(HistorySessionNotFoundError):
        service.delete_session(saved.session_id or 0)
    repository.close()

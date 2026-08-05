"""Qt-facing bridge for the recommendation screen."""

from __future__ import annotations

import asyncio
from concurrent.futures import Future, ThreadPoolExecutor

from pydantic import ValidationError
from PySide6.QtCore import Property, QObject, Signal, Slot

from anicompass.ai.models import AIProviderCallError, AIProviderConfig
from anicompass.catalog.models import CatalogProviderError
from anicompass.history.service import HistoryService
from anicompass.recommendation.models import RecommendationRequest, RecommendationResult
from anicompass.recommendation.orchestrator import RecommendationOrchestrator
from anicompass.recommendation.parser import RecommendationParseError


class RecommendBridge(QObject):
    """Expose recommendation state and commands to QML."""

    stateChanged = Signal()
    _recommendationFinished = Signal(object, object)

    def __init__(
        self,
        orchestrator: RecommendationOrchestrator,
        provider_config: AIProviderConfig,
        parent: QObject | None = None,
        executor: ThreadPoolExecutor | None = None,
        history_service: HistoryService | None = None,
    ) -> None:
        super().__init__(parent)
        self._orchestrator = orchestrator
        self._provider_config = provider_config
        self._history_service = history_service
        self._last_request: RecommendationRequest | None = None
        self._status = "idle"
        self._is_busy = False
        self._items: tuple[dict[str, object], ...] = ()
        self._unresolved: tuple[dict[str, object], ...] = ()
        self._error_code = ""
        self._error_message = ""
        self._executor = executor or ThreadPoolExecutor(max_workers=1)
        self._owns_executor = executor is None
        self._recommendationFinished.connect(self._handle_recommendation_finished)

    @Property(str, notify=stateChanged)
    def status(self) -> str:
        return self._status

    @Property(bool, notify=stateChanged)
    def isBusy(self) -> bool:
        return self._is_busy

    @Property(list, notify=stateChanged)
    def items(self) -> list[dict[str, object]]:
        return list(self._items)

    @Property(list, notify=stateChanged)
    def unresolved(self) -> list[dict[str, object]]:
        return list(self._unresolved)

    @Property(str, notify=stateChanged)
    def errorCode(self) -> str:
        return self._error_code

    @Property(str, notify=stateChanged)
    def errorMessage(self) -> str:
        return self._error_message

    @Slot(str, int, str)
    def recommend(self, preferences: str, count: int, language: str) -> None:
        if self._is_busy:
            return
        try:
            request = RecommendationRequest(
                preferences=preferences.strip(),
                count=count,
                language=language if language == "en" else "zh",
                safe_for_all_audiences=True,
            )
        except ValidationError:
            self._set_error("invalid_request", "Recommendation input is invalid.")
            self.stateChanged.emit()
            return
        self._last_request = request
        self._status = "loading"
        self._is_busy = True
        self._items = ()
        self._unresolved = ()
        self._clear_error()
        self.stateChanged.emit()
        future = self._executor.submit(self._run_recommendation, request)
        future.add_done_callback(self._emit_recommendation_finished)

    @Slot(str, result=str)
    def copyForStatus(self, language: str) -> str:
        if self._status == "loading":
            return "??????..." if language == "zh" else "Generating recommendations..."
        if self._status == "success":
            if language == "zh":
                return f"??? {len(self._items)} ????"
            return f"{len(self._items)} verified recommendations."
        if self._status == "empty":
            return "?????????" if language == "zh" else "No recommendations to show."
        if self._status == "error":
            if language == "zh" and self._error_code == "missing_api_key":
                return "???????? API Key?"
            if language == "zh":
                return "?????"
            return self._error_message or "Recommendation failed."
        return "??????????" if language == "zh" else "Enter preferences to recommend."

    @Slot(object, object)
    def _handle_recommendation_finished(
        self,
        result: RecommendationResult | None,
        error: BaseException | None,
    ) -> None:
        self._is_busy = False
        if result is not None:
            if self._history_service is not None and self._last_request is not None:
                self._history_service.save_result(self._last_request, result)
            self._items = tuple(self._verified_to_qml(item) for item in result.items)
            self._unresolved = tuple(
                self._unresolved_to_qml(item) for item in result.unresolved
            )
            self._status = "success" if self._items else "empty"
            self._clear_error()
        elif isinstance(error, AIProviderCallError):
            self._status = "error"
            self._set_error(error.error.code.value, error.error.message)
        elif isinstance(error, (CatalogProviderError, RecommendationParseError)):
            self._status = "error"
            self._set_error("provider_error", str(error))
        elif error is not None:
            self._status = "error"
            self._set_error("provider_error", "Recommendation failed unexpectedly.")
        self.stateChanged.emit()

    def close(self) -> None:
        if self._owns_executor:
            self._executor.shutdown(wait=False, cancel_futures=True)

    def _run_recommendation(
        self,
        request: RecommendationRequest,
    ) -> RecommendationResult:
        return asyncio.run(
            self._orchestrator.recommend(request, self._provider_config)
        )

    def _emit_recommendation_finished(
        self,
        future: Future[RecommendationResult],
    ) -> None:
        try:
            self._recommendationFinished.emit(future.result(), None)
        except BaseException as exc:
            self._recommendationFinished.emit(None, exc)

    def _verified_to_qml(self, item) -> dict[str, object]:
        anime = item.anime
        return {
            "catalogSource": anime.catalog_id.source.value,
            "providerId": anime.catalog_id.provider_id,
            "title": anime.title,
            "originalTitle": anime.original_title or "",
            "imageUrl": str(anime.image_url) if anime.image_url else "",
            "sourceUrl": str(anime.source_url) if anime.source_url else "",
            "year": anime.year if anime.year is not None else "",
            "score": anime.score if anime.score is not None else "",
            "genres": ", ".join(anime.genres),
            "reason": item.reason,
            "attribution": anime.attribution,
        }

    def _unresolved_to_qml(self, item) -> dict[str, object]:
        return {
            "title": item.candidate.title,
            "year": item.candidate.year if item.candidate.year is not None else "",
            "reason": item.reason,
        }

    def _clear_error(self) -> None:
        self._error_code = ""
        self._error_message = ""

    def _set_error(self, code: str, message: str) -> None:
        self._error_code = code
        self._error_message = message
        self._status = "error"
        self._is_busy = False

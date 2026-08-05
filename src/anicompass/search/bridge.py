"""Qt-facing bridge for the Search QML screen."""

from __future__ import annotations

import asyncio
from concurrent.futures import Future, ThreadPoolExecutor

from PySide6.QtCore import Property, QObject, Signal, Slot

from anicompass.catalog.models import CatalogAnime, CatalogError, CatalogErrorCode
from anicompass.search.viewmodel import SearchStatus, SearchViewModel, SearchViewState


class SearchBridge(QObject):
    """Expose SearchViewModel state through QML-friendly properties."""

    stateChanged = Signal()
    _searchFinished = Signal(object, object)

    def __init__(
        self,
        view_model: SearchViewModel,
        parent: QObject | None = None,
        executor: ThreadPoolExecutor | None = None,
    ) -> None:
        super().__init__(parent)
        self._view_model = view_model
        self._state = view_model.state
        self._executor = executor or ThreadPoolExecutor(max_workers=1)
        self._owns_executor = executor is None
        self._searchFinished.connect(self._handle_search_finished)

    @Property(str, notify=stateChanged)
    def status(self) -> str:
        return self._state.status.value

    @Property(str, notify=stateChanged)
    def query(self) -> str:
        return self._state.query

    @Property(bool, notify=stateChanged)
    def isBusy(self) -> bool:
        return self._state.is_busy

    @Property(str, notify=stateChanged)
    def errorCode(self) -> str:
        error = self._state.error
        return error.code.value if error else ""

    @Property(str, notify=stateChanged)
    def errorMessage(self) -> str:
        error = self._state.error
        return error.message if error else ""

    @Property(int, notify=stateChanged)
    def itemCount(self) -> int:
        return len(self._state.items)

    @Property(list, notify=stateChanged)
    def items(self) -> list[dict[str, object]]:
        return [self._item_to_qml(item) for item in self._state.items]

    @Property(bool, notify=stateChanged)
    def hasSelection(self) -> bool:
        return self._state.selected_item is not None

    @Property(dict, notify=stateChanged)
    def selectedItem(self) -> dict[str, object]:
        if self._state.selected_item is None:
            return {}
        return self._item_to_qml(self._state.selected_item)

    @Slot(str)
    def search(self, query: str) -> None:
        trimmed_query = query.strip()
        if self._state.is_busy:
            return
        self._state = SearchViewState(
            status=SearchStatus.LOADING,
            query=trimmed_query,
            is_busy=True,
        )
        self.stateChanged.emit()
        future = self._executor.submit(self._run_search, trimmed_query)
        future.add_done_callback(self._emit_finished)

    @Slot(str)
    def selectItem(self, provider_id: str) -> None:
        if self._state.is_busy:
            return
        self._state = self._view_model.select_result(provider_id)
        self.stateChanged.emit()

    @Slot()
    def clearSelection(self) -> None:
        if self._state.is_busy:
            return
        self._state = self._view_model.clear_selection()
        self.stateChanged.emit()

    @Slot()
    def reset(self) -> None:
        if self._state.is_busy:
            return
        self._state = self._view_model.reset()
        self.stateChanged.emit()

    @Slot(str, result=str)
    def copyForStatus(self, language: str) -> str:
        status = self._state.status
        error = self._state.error
        if language == "en":
            messages = {
                SearchStatus.IDLE: "Enter a title to search the real anime catalog.",
                SearchStatus.LOADING: "Searching Jikan...",
                SearchStatus.SUCCESS: "Results from Jikan / MyAnimeList.",
                SearchStatus.EMPTY: "No matching anime was found.",
                SearchStatus.ERROR: error.message if error else "Search failed.",
            }
            return messages[status]
        messages = {
            SearchStatus.IDLE: (
                "\u8f93\u5165\u6807\u9898\u641c\u7d22"
                "\u771f\u5b9e\u52a8\u6f2b\u76ee\u5f55\u3002"
            ),
            SearchStatus.LOADING: "\u6b63\u5728\u641c\u7d22 Jikan...",
            SearchStatus.SUCCESS: (
                "\u7ed3\u679c\u6765\u81ea Jikan / MyAnimeList\u3002"
            ),
            SearchStatus.EMPTY: (
                "\u6ca1\u6709\u627e\u5230\u5339\u914d\u7684\u52a8\u6f2b\u3002"
            ),
            SearchStatus.ERROR: (
                error.message if error else "\u641c\u7d22\u5931\u8d25\u3002"
            ),
        }
        return messages[status]

    @Slot(object, object)
    def _handle_search_finished(
        self,
        state: SearchViewState | None,
        error: BaseException | None,
    ) -> None:
        if state is not None:
            self._state = state
        elif error is not None:
            self._state = SearchViewState(
                status=SearchStatus.ERROR,
                query=self._state.query,
                error=CatalogError(
                    code=CatalogErrorCode.PROVIDER_ERROR,
                    message="Catalog search failed unexpectedly.",
                ),
            )
        self.stateChanged.emit()

    def close(self) -> None:
        if self._owns_executor:
            self._executor.shutdown(wait=False, cancel_futures=True)

    def _run_search(self, query: str) -> SearchViewState:
        return asyncio.run(
            self._view_model.search(
                query,
                limit=10,
                safe_for_all_audiences=True,
            )
        )

    def _emit_finished(self, future: Future[SearchViewState]) -> None:
        try:
            self._searchFinished.emit(future.result(), None)
        except BaseException as exc:
            self._searchFinished.emit(None, exc)

    def _item_to_qml(self, item: CatalogAnime) -> dict[str, object]:
        return {
            "catalogSource": item.catalog_id.source.value,
            "providerId": item.catalog_id.provider_id,
            "title": item.title,
            "originalTitle": item.original_title or "",
            "englishTitle": item.english_title or "",
            "mediaType": item.media_type or "",
            "episodes": item.episodes if item.episodes is not None else "",
            "year": item.year if item.year is not None else "",
            "score": item.score if item.score is not None else "",
            "rating": item.rating or "",
            "synopsis": item.synopsis or "",
            "imageUrl": str(item.image_url) if item.image_url else "",
            "sourceUrl": str(item.source_url) if item.source_url else "",
            "genres": ", ".join(item.genres),
            "studios": ", ".join(item.studios),
            "attribution": item.attribution,
        }

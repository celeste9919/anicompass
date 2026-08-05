"""Qt-facing bridge for local watch-list state."""

from __future__ import annotations

from pydantic import ValidationError
from PySide6.QtCore import Property, QObject, Signal, Slot

from anicompass.catalog.models import CatalogAnime, CatalogAnimeId, CatalogSource
from anicompass.watchlist.models import (
    WatchListFilter,
    WatchListItem,
    WatchListUpdate,
    WatchStatus,
)
from anicompass.watchlist.repository import (
    DuplicateWatchListItemError,
    WatchListItemNotFoundError,
)
from anicompass.watchlist.service import WatchListService


class WatchListBridge(QObject):
    """Expose local watch-list service state to QML."""

    stateChanged = Signal()

    def __init__(
        self,
        service: WatchListService,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._status_filter = "all"
        self._error_code = ""
        self._error_message = ""

    @Property(list, notify=stateChanged)
    def items(self) -> list[dict[str, object]]:
        item_filter = self._current_filter()
        return [
            self._item_to_qml(item)
            for item in self._service.list_items(item_filter)
        ]

    @Property(int, notify=stateChanged)
    def itemCount(self) -> int:
        return len(self.items)

    @Property(str, notify=stateChanged)
    def statusFilter(self) -> str:
        return self._status_filter

    @Property(str, notify=stateChanged)
    def errorCode(self) -> str:
        return self._error_code

    @Property(str, notify=stateChanged)
    def errorMessage(self) -> str:
        return self._error_message

    @Slot(str)
    def setStatusFilter(self, status: str) -> None:
        next_status = status if status in self._allowed_filters() else "all"
        if next_status == self._status_filter:
            return
        self._status_filter = next_status
        self._clear_error()
        self.stateChanged.emit()

    @Slot(object)
    def addFromCatalogItem(self, payload: object) -> None:
        try:
            item = self._catalog_item_from_payload(payload)
            self._service.add_anime(item)
            self._clear_error()
        except DuplicateWatchListItemError:
            self._set_error("duplicate_item", "This anime is already in your list.")
        except (KeyError, TypeError, ValueError, ValidationError):
            self._set_error("invalid_item", "The selected catalog item is invalid.")
        self.stateChanged.emit()

    @Slot(int, str, int, int, str)
    def updateItem(
        self,
        item_id: int,
        status: str,
        progress: int,
        score: int,
        notes: str,
    ) -> None:
        try:
            patch = WatchListUpdate(
                status=WatchStatus(status),
                progress=progress,
                score=score if score > 0 else None,
                notes=notes,
            )
            self._service.update_item(item_id, patch)
            self._clear_error()
        except WatchListItemNotFoundError:
            self._set_error("not_found", "This list item was not found.")
        except (ValueError, ValidationError):
            self._set_error("invalid_update", "The watch-list update is invalid.")
        self.stateChanged.emit()

    @Slot(int)
    def removeItem(self, item_id: int) -> None:
        try:
            self._service.remove_item(item_id)
            self._clear_error()
        except WatchListItemNotFoundError:
            self._set_error("not_found", "This list item was not found.")
        self.stateChanged.emit()

    @Slot(str, result=str)
    def copyForStatus(self, language: str) -> str:
        if self._error_message:
            if language == "zh" and self._error_code == "duplicate_item":
                return (
                    "\u8fd9\u90e8\u52a8\u6f2b\u5df2\u7ecf"
                    "\u5728\u4f60\u7684\u7247\u5355\u91cc\u3002"
                )
            if language == "zh" and self._error_code == "not_found":
                return "\u8fd9\u4e2a\u7247\u5355\u6761\u76ee\u4e0d\u5b58\u5728\u3002"
            if language == "zh":
                return "\u7247\u5355\u64cd\u4f5c\u5931\u8d25\u3002"
            return self._error_message
        if self.itemCount == 0:
            return (
                "\u7247\u5355\u8fd8\u662f\u7a7a\u7684\u3002"
                if language == "zh"
                else "Your list is empty."
            )
        return (
            f"\u7247\u5355\u4e2d\u6709 {self.itemCount} \u4e2a\u6761\u76ee\u3002"
            if language == "zh"
            else f"{self.itemCount} items in your list."
        )

    def _current_filter(self) -> WatchListFilter | None:
        if self._status_filter == "all":
            return None
        return WatchListFilter(status=WatchStatus(self._status_filter))

    def _allowed_filters(self) -> set[str]:
        return {"all", *(status.value for status in WatchStatus)}

    def _clear_error(self) -> None:
        self._error_code = ""
        self._error_message = ""

    def _set_error(self, code: str, message: str) -> None:
        self._error_code = code
        self._error_message = message

    def _catalog_item_from_payload(self, payload: object) -> CatalogAnime:
        if not isinstance(payload, dict):
            raise TypeError("Expected selected catalog item dictionary.")
        catalog_source = str(payload.get("catalogSource") or CatalogSource.JIKAN.value)
        provider_id = str(payload["providerId"])
        return CatalogAnime(
            catalog_id=CatalogAnimeId(
                source=CatalogSource(catalog_source),
                provider_id=provider_id,
            ),
            title=str(payload["title"]),
            original_title=str(payload.get("originalTitle") or "") or None,
            image_url=str(payload.get("imageUrl") or "") or None,
            source_url=str(payload.get("sourceUrl") or "") or None,
        )

    def _item_to_qml(self, item: WatchListItem) -> dict[str, object]:
        return {
            "itemId": item.item_id or 0,
            "catalogSource": item.catalog_id.source.value,
            "providerId": item.catalog_id.provider_id,
            "title": item.title,
            "originalTitle": item.original_title or "",
            "imageUrl": item.image_url or "",
            "sourceUrl": item.source_url or "",
            "status": item.status.value,
            "progress": item.progress,
            "score": item.score if item.score is not None else "",
            "notes": item.notes,
            "updatedAt": item.updated_at.isoformat(),
        }

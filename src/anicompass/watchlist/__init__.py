"""Local watch-list persistence for AniCompass."""

from anicompass.watchlist.bridge import WatchListBridge
from anicompass.watchlist.models import (
    WatchListFilter,
    WatchListItem,
    WatchListUpdate,
    WatchStatus,
)
from anicompass.watchlist.repository import (
    DuplicateWatchListItemError,
    SQLiteWatchListRepository,
    WatchListItemNotFoundError,
)
from anicompass.watchlist.service import WatchListService

__all__ = [
    "DuplicateWatchListItemError",
    "SQLiteWatchListRepository",
    "WatchListBridge",
    "WatchListFilter",
    "WatchListItem",
    "WatchListItemNotFoundError",
    "WatchListService",
    "WatchListUpdate",
    "WatchStatus",
]

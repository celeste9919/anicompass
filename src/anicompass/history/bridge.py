"""Qt-facing bridge for recommendation history."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, Slot

from anicompass.history.repository import HistorySessionNotFoundError
from anicompass.history.service import HistoryService


class HistoryBridge(QObject):
    """Expose saved recommendation sessions to QML."""

    stateChanged = Signal()

    def __init__(self, service: HistoryService, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self._error_code = ""
        self._error_message = ""

    @Property(list, notify=stateChanged)
    def sessions(self) -> list[dict[str, object]]:
        return [
            self._session_to_qml(session)
            for session in self._service.list_sessions()
        ]

    @Property(int, notify=stateChanged)
    def sessionCount(self) -> int:
        return len(self.sessions)

    @Property(str, notify=stateChanged)
    def errorCode(self) -> str:
        return self._error_code

    @Property(str, notify=stateChanged)
    def errorMessage(self) -> str:
        return self._error_message

    @Slot(int)
    def deleteSession(self, session_id: int) -> None:
        try:
            self._service.delete_session(session_id)
            self._clear_error()
        except HistorySessionNotFoundError:
            self._set_error("not_found", "History session was not found.")
        self.stateChanged.emit()

    @Slot(str, result=str)
    def copyForStatus(self, language: str) -> str:
        if self._error_code:
            if language == "zh" and self._error_code == "not_found":
                return "??????????"
            return (
                self._error_message
                if language == "en"
                else "\u5386\u53f2\u64cd\u4f5c\u5931\u8d25\u3002"
            )
        if self.sessionCount == 0:
            return (
                "\u8fd8\u6ca1\u6709\u63a8\u8350\u5386\u53f2\u3002"
                if language == "zh"
                else "No history yet."
            )
        if language == "zh":
            return (
                f"\u6700\u8fd1 {self.sessionCount} "
                "\u6761\u63a8\u8350\u5386\u53f2\u3002"
            )
        return f"{self.sessionCount} recent recommendation sessions."

    def notifyChanged(self) -> None:
        self.stateChanged.emit()

    def _session_to_qml(self, session) -> dict[str, object]:
        return {
            "sessionId": session.session_id or 0,
            "preferences": session.preferences,
            "language": session.language,
            "verifiedCount": session.verified_count,
            "unresolvedCount": session.unresolved_count,
            "createdAt": session.created_at.isoformat(),
        }

    def _clear_error(self) -> None:
        self._error_code = ""
        self._error_message = ""

    def _set_error(self, code: str, message: str) -> None:
        self._error_code = code
        self._error_message = message

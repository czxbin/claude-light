from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QPoint, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QPainter
from PySide6.QtWidgets import QApplication, QMenu, QWidget

from claude_monitor.paths import default_status_path
from claude_monitor.status import parse_status, read_status
from claude_monitor.watcher import StatusWatcher


class MonitorWindow(QWidget):
    reload_requested = Signal()

    def __init__(self, status_file: Path | None = None) -> None:
        super().__init__()
        self.status_file = status_file or default_status_path()
        self.status = read_status(self.status_file)
        self.flash_on = False
        self.drag_start: QPoint | None = None

        self.setFixedSize(96, 52)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.flash_timer = QTimer(self)
        self.flash_timer.setInterval(500)
        self.flash_timer.timeout.connect(self._toggle_flash)

        self.reload_timer = QTimer(self)
        self.reload_timer.setSingleShot(True)
        self.reload_timer.setInterval(100)
        self.reload_timer.timeout.connect(self.reload_status)
        self.reload_requested.connect(self.request_reload)

        self.watcher = StatusWatcher(self.status_file, self.reload_requested.emit)
        self.watcher.start()

        self.apply_status(self.status)

    def apply_status(self, status: str) -> None:
        self.status = parse_status(status)
        if self.status == "waiting":
            if not self.flash_timer.isActive():
                self.flash_timer.start()
        else:
            self.flash_timer.stop()
            self.flash_on = False
        self.update()

    def request_reload(self) -> None:
        self.reload_timer.start()

    def reload_status(self) -> None:
        self.apply_status(read_status(self.status_file))

    def _toggle_flash(self) -> None:
        self.flash_on = not self.flash_on
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.status == "waiting":
            background = QColor(220, 38, 38) if self.flash_on else QColor(127, 29, 29)
            text = "WAIT"
        else:
            background = QColor(39, 39, 42)
            text = "idle"

        painter.setBrush(background)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 10, 10)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event) -> None:
        if self.drag_start is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_start)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = None

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)
        menu.exec(event.globalPos())

    def closeEvent(self, event) -> None:
        self.watcher.stop()
        super().closeEvent(event)


def place_bottom_right(window: QWidget) -> None:
    screen = QApplication.primaryScreen().availableGeometry()
    margin = 24
    window.move(
        screen.right() - window.width() - margin,
        screen.bottom() - window.height() - margin,
    )


def main() -> int:
    app = QApplication(sys.argv)
    window = MonitorWindow()
    place_bottom_right(window)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class StatusFileHandler(FileSystemEventHandler):
    def __init__(self, status_file: Path, on_changed: Callable[[], None]) -> None:
        self.status_file = status_file.resolve()
        self.on_changed = on_changed

    def on_modified(self, event: FileSystemEvent) -> None:
        self._maybe_notify(event)

    def on_created(self, event: FileSystemEvent) -> None:
        self._maybe_notify(event)

    def on_moved(self, event: FileSystemEvent) -> None:
        self._maybe_notify(event, include_dest=True)

    def _maybe_notify(
        self, event: FileSystemEvent, *, include_dest: bool = False
    ) -> None:
        if event.is_directory:
            return
        paths = [event.src_path]
        if include_dest:
            paths.append(getattr(event, "dest_path", ""))
        if any(path and Path(path).resolve() == self.status_file for path in paths):
            self.on_changed()


class StatusWatcher:
    def __init__(self, status_file: Path, on_changed: Callable[[], None]) -> None:
        self.status_file = status_file.resolve()
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self.handler = StatusFileHandler(self.status_file, on_changed)
        self.observer = Observer()
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self.observer.schedule(
            self.handler,
            str(self.status_file.parent),
            recursive=False,
        )
        self.observer.start()
        self._started = True

    def stop(self) -> None:
        if not self._started:
            return
        self.observer.stop()
        self.observer.join(timeout=2)
        self._started = False

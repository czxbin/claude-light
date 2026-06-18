from pathlib import Path

from claude_monitor import watcher
from claude_monitor.watcher import StatusFileHandler, StatusWatcher


class FakeEvent:
    def __init__(
        self,
        src_path: Path,
        *,
        dest_path: Path | str | None = None,
        is_directory: bool = False,
    ) -> None:
        self.src_path = str(src_path)
        self.is_directory = is_directory
        if dest_path is not None:
            self.dest_path = str(dest_path)


def test_created_and_modified_notify_for_target_source(tmp_path: Path):
    target = tmp_path / "status.txt"
    notifications: list[None] = []
    handler = StatusFileHandler(target, lambda: notifications.append(None))

    handler.on_created(FakeEvent(target, dest_path=""))
    handler.on_modified(FakeEvent(target, dest_path=""))

    assert len(notifications) == 2


def test_created_and_modified_ignore_other_source(tmp_path: Path):
    target = tmp_path / "status.txt"
    other = tmp_path / "other.txt"
    notifications: list[None] = []
    handler = StatusFileHandler(target, lambda: notifications.append(None))

    handler.on_created(FakeEvent(other, dest_path=""))
    handler.on_modified(FakeEvent(other, dest_path=""))

    assert notifications == []


def test_moved_notifies_when_target_is_source_or_destination(tmp_path: Path):
    target = tmp_path / "status.txt"
    other = tmp_path / "other.txt"
    notifications: list[None] = []
    handler = StatusFileHandler(target, lambda: notifications.append(None))

    handler.on_moved(FakeEvent(target, dest_path=other))
    handler.on_moved(FakeEvent(other, dest_path=target))

    assert len(notifications) == 2


def test_moved_ignores_unrelated_paths(tmp_path: Path):
    target = tmp_path / "status.txt"
    notifications: list[None] = []
    handler = StatusFileHandler(target, lambda: notifications.append(None))

    handler.on_moved(
        FakeEvent(tmp_path / "source.txt", dest_path=tmp_path / "dest.txt")
    )

    assert notifications == []


def test_status_watcher_start_and_stop_are_idempotent(
    tmp_path: Path, monkeypatch
):
    observers = []

    class FakeObserver:
        def __init__(self) -> None:
            self.schedule_calls = 0
            self.start_calls = 0
            self.stop_calls = 0
            self.join_calls = 0
            observers.append(self)

        def schedule(self, *args, **kwargs) -> None:
            self.schedule_calls += 1

        def start(self) -> None:
            self.start_calls += 1

        def stop(self) -> None:
            self.stop_calls += 1

        def join(self, timeout=None) -> None:
            self.join_calls += 1

    monkeypatch.setattr(watcher, "Observer", FakeObserver)
    status_watcher = StatusWatcher(tmp_path / "status.txt", lambda: None)

    status_watcher.stop()
    status_watcher.start()
    status_watcher.start()
    status_watcher.stop()
    status_watcher.stop()

    observer = observers[0]
    assert observer.schedule_calls == 1
    assert observer.start_calls == 1
    assert observer.stop_calls == 1
    assert observer.join_calls == 1

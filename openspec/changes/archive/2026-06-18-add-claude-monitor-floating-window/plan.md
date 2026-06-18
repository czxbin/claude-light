# Claude Code Monitor Floating Window Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows-only Claude Code monitor that shows a topmost floating signal window and reacts to silent hook-written `idle`/`waiting` status changes.

**Architecture:** Claude Code hooks invoke a small status writer that atomically writes a local status file. A PySide6 desktop app watches the file's parent directory with watchdog and updates a frameless topmost floating window on the UI thread.

**Tech Stack:** Python 3.11+, PySide6, watchdog, pytest, PyInstaller.

---

## File Structure

- Create: `pyproject.toml` — dependencies, scripts, pytest config.
- Create: `src/claude_monitor/__init__.py` — package marker.
- Create: `src/claude_monitor/paths.py` — default `%LOCALAPPDATA%` status path.
- Create: `src/claude_monitor/status.py` — status parsing and atomic writes.
- Create: `src/claude_monitor/hook_writer.py` — CLI entry point for Claude Code hooks.
- Create: `src/claude_monitor/watcher.py` — watchdog observer wrapper.
- Create: `src/claude_monitor/app.py` — PySide6 floating window and app startup.
- Create: `claude_hooks/settings.example.json` — Claude Code hook configuration example.
- Create: `README.md` — run, hook setup, test, and package instructions.
- Create: `tests/test_status.py` — status contract tests.
- Create: `tests/test_imports.py` — non-blocking smoke import tests.

Current workspace is not a Git repository, so commit steps are replaced with local checkpoints using `openspec.cmd status --change "add-claude-monitor-floating-window"`.

### Task 1: Project Structure and Status Path

**Files:**
- Create: `pyproject.toml`
- Create: `src/claude_monitor/__init__.py`
- Create: `src/claude_monitor/paths.py`

- [ ] **Step 1: Add project metadata and dependencies**

Create `pyproject.toml`:

```toml
[project]
name = "claude-monitor"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "PySide6>=6.7",
  "watchdog>=4.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "pyinstaller>=6.0",
]

[project.scripts]
claude-monitor = "claude_monitor.app:main"
claude-monitor-write-status = "claude_monitor.hook_writer:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: Add package marker**

Create `src/claude_monitor/__init__.py`:

```python
"""Claude Code Windows floating monitor."""
```

- [ ] **Step 3: Add default path helper**

Create `src/claude_monitor/paths.py`:

```python
from __future__ import annotations

import os
from pathlib import Path


APP_DIR_NAME = "ClaudeLight"
STATUS_FILE_NAME = "status.txt"


def default_status_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / APP_DIR_NAME / STATUS_FILE_NAME
    return Path.home() / "AppData" / "Local" / APP_DIR_NAME / STATUS_FILE_NAME
```

- [ ] **Step 4: Run import smoke check**

Run: `python -c "from claude_monitor.paths import default_status_path; print(default_status_path())"`

Expected: prints a path ending with `ClaudeLight\status.txt`.

- [ ] **Step 5: Local checkpoint**

Run: `openspec.cmd status --change "add-claude-monitor-floating-window"`

Expected: change remains valid and `plan` is present.

### Task 2: Status Contract and Atomic Writer

**Files:**
- Create: `src/claude_monitor/status.py`
- Create: `tests/test_status.py`

- [ ] **Step 1: Write failing status tests**

Create `tests/test_status.py`:

```python
from pathlib import Path

import pytest

from claude_monitor.status import parse_status, read_status, write_status


def test_parse_status_accepts_known_values():
    assert parse_status("idle") == "idle"
    assert parse_status("waiting") == "waiting"


def test_parse_status_falls_back_to_idle_for_monitor_reads():
    assert parse_status("") == "idle"
    assert parse_status("bad") == "idle"


def test_write_status_rejects_unknown_values(tmp_path: Path):
    target = tmp_path / "status.txt"
    with pytest.raises(ValueError):
        write_status(target, "bad")
    assert not target.exists()


def test_write_status_creates_parent_and_replaces_file(tmp_path: Path):
    target = tmp_path / "nested" / "status.txt"
    write_status(target, "idle")
    assert target.read_text(encoding="utf-8") == "idle"
    write_status(target, "waiting")
    assert target.read_text(encoding="utf-8") == "waiting"


def test_read_status_missing_file_is_idle(tmp_path: Path):
    assert read_status(tmp_path / "missing.txt") == "idle"
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_status.py -v`

Expected: FAIL because `claude_monitor.status` does not exist.

- [ ] **Step 3: Implement status module**

Create `src/claude_monitor/status.py`:

```python
from __future__ import annotations

import os
from pathlib import Path


VALID_STATUSES = {"idle", "waiting"}
DEFAULT_STATUS = "idle"


def parse_status(value: str | None) -> str:
    normalized = (value or "").strip().lower()
    if normalized in VALID_STATUSES:
        return normalized
    return DEFAULT_STATUS


def validate_status(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized not in VALID_STATUSES:
        raise ValueError(f"unsupported status: {value!r}")
    return normalized


def read_status(path: Path) -> str:
    try:
        return parse_status(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return DEFAULT_STATUS


def write_status(path: Path, status: str) -> None:
    normalized = validate_status(status)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.tmp")
    temp_path.write_text(normalized, encoding="utf-8")
    os.replace(temp_path, path)
```

- [ ] **Step 4: Run tests to verify pass**

Run: `pytest tests/test_status.py -v`

Expected: 5 tests pass.

- [ ] **Step 5: Local checkpoint**

Run: `openspec.cmd status --change "add-claude-monitor-floating-window"`

Expected: no OpenSpec artifact regression.

### Task 3: Hook Writer and Claude Code Example

**Files:**
- Create: `src/claude_monitor/hook_writer.py`
- Create: `claude_hooks/settings.example.json`
- Modify: `README.md`

- [ ] **Step 1: Implement CLI hook writer**

Create `src/claude_monitor/hook_writer.py`:

```python
from __future__ import annotations

import argparse
from pathlib import Path

from claude_monitor.paths import default_status_path
from claude_monitor.status import write_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write Claude monitor status.")
    parser.add_argument("status", choices=["idle", "waiting"])
    parser.add_argument("--status-file", type=Path, default=default_status_path())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    write_status(args.status_file, args.status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Add CLI test command**

Run: `python -m claude_monitor.hook_writer waiting --status-file .tmp-status.txt`

Expected: `.tmp-status.txt` contains `waiting`.

- [ ] **Step 3: Add Claude Code hook example**

Create `claude_hooks/settings.example.json`:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "pythonw.exe -m claude_monitor.hook_writer waiting"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "pythonw.exe -m claude_monitor.hook_writer idle"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 4: Document hook setup**

Create `README.md` with:

```markdown
# Claude Code Monitor

Windows floating monitor for Claude Code attention states.

## Status file

Default path: `%LOCALAPPDATA%\ClaudeLight\status.txt`

Valid values:

- `idle`
- `waiting`

## Hook setup

Copy the relevant entries from `claude_hooks/settings.example.json` into your Claude Code settings. The example uses `pythonw.exe` so status changes do not open a visible command prompt window.

If your Claude Code version uses different hook event names, keep the command shape and map the events that mean "needs attention" to `waiting`, and events that clear the alert to `idle`.

## Manual status test

```powershell
python -m claude_monitor.hook_writer waiting
python -m claude_monitor.hook_writer idle
```
```

- [ ] **Step 5: Run writer tests**

Run: `pytest tests/test_status.py -v`

Expected: 5 tests pass.

### Task 4: Floating Window UI

**Files:**
- Create: `src/claude_monitor/app.py`
- Create: `tests/test_imports.py`

- [ ] **Step 1: Add import smoke test**

Create `tests/test_imports.py`:

```python
def test_import_app_module():
    import claude_monitor.app

    assert claude_monitor.app.MonitorWindow is not None
```

- [ ] **Step 2: Run smoke test to verify failure**

Run: `pytest tests/test_imports.py -v`

Expected: FAIL because `claude_monitor.app` does not exist.

- [ ] **Step 3: Implement PySide6 monitor window**

Create `src/claude_monitor/app.py`:

```python
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QPainter
from PySide6.QtWidgets import QApplication, QMenu, QWidget

from claude_monitor.paths import default_status_path
from claude_monitor.status import read_status


class MonitorWindow(QWidget):
    def __init__(self, status_file: Path | None = None) -> None:
        super().__init__()
        self.status_file = status_file or default_status_path()
        self.status = read_status(self.status_file)
        self.flash_on = False
        self.drag_start: QPoint | None = None
        self.setFixedSize(96, 52)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.flash_timer = QTimer(self)
        self.flash_timer.setInterval(500)
        self.flash_timer.timeout.connect(self._toggle_flash)
        self.apply_status(self.status)

    def apply_status(self, status: str) -> None:
        self.status = status
        if status == "waiting":
            if not self.flash_timer.isActive():
                self.flash_timer.start()
        else:
            self.flash_timer.stop()
            self.flash_on = False
        self.update()

    def _toggle_flash(self) -> None:
        self.flash_on = not self.flash_on
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.status == "waiting":
            color = QColor(220, 38, 38) if self.flash_on else QColor(127, 29, 29)
            text = "WAIT"
        else:
            color = QColor(39, 39, 42)
            text = "idle"
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.rect(), Qt.AlignCenter, text)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event) -> None:
        if self.drag_start is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_start)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.drag_start = None

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)
        menu.exec(event.globalPos())


def place_bottom_right(window: QWidget) -> None:
    screen = QApplication.primaryScreen().availableGeometry()
    margin = 24
    window.move(screen.right() - window.width() - margin, screen.bottom() - window.height() - margin)


def main() -> int:
    app = QApplication(sys.argv)
    window = MonitorWindow()
    place_bottom_right(window)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run import smoke test**

Run: `pytest tests/test_imports.py -v`

Expected: 1 test passes.

### Task 5: Watchdog Integration

**Files:**
- Create: `src/claude_monitor/watcher.py`
- Modify: `src/claude_monitor/app.py`

- [ ] **Step 1: Implement watchdog wrapper**

Create `src/claude_monitor/watcher.py`:

```python
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
        self._maybe_notify(event)

    def _maybe_notify(self, event: FileSystemEvent) -> None:
        target = Path(getattr(event, "dest_path", event.src_path)).resolve()
        if target == self.status_file:
            self.on_changed()


class StatusWatcher:
    def __init__(self, status_file: Path, on_changed: Callable[[], None]) -> None:
        self.status_file = status_file
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self.observer = Observer()
        self.handler = StatusFileHandler(status_file, on_changed)

    def start(self) -> None:
        self.observer.schedule(self.handler, str(self.status_file.parent), recursive=False)
        self.observer.start()

    def stop(self) -> None:
        self.observer.stop()
        self.observer.join(timeout=2)
```

- [ ] **Step 2: Wire watcher into app**

Modify `src/claude_monitor/app.py`:

```python
from claude_monitor.watcher import StatusWatcher
```

Add inside `MonitorWindow.__init__` after `self.flash_timer.timeout.connect(...)`:

```python
        self.reload_timer = QTimer(self)
        self.reload_timer.setSingleShot(True)
        self.reload_timer.setInterval(100)
        self.reload_timer.timeout.connect(self.reload_status)
        self.watcher = StatusWatcher(self.status_file, self.request_reload)
        self.watcher.start()
```

Add methods to `MonitorWindow`:

```python
    def request_reload(self) -> None:
        self.reload_timer.start()

    def reload_status(self) -> None:
        self.apply_status(read_status(self.status_file))

    def closeEvent(self, event) -> None:
        self.watcher.stop()
        super().closeEvent(event)
```

- [ ] **Step 3: Run smoke tests**

Run: `pytest -v`

Expected: status tests and import smoke test pass.

- [ ] **Step 4: Manual UI verification**

Run: `python -m claude_monitor.app`

In another PowerShell window, run:

```powershell
python -m claude_monitor.hook_writer waiting
python -m claude_monitor.hook_writer idle
```

Expected: the floating window flashes red after `waiting` and returns to dark gray after `idle`.

### Task 6: Documentation and Packaging

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add run and test instructions**

Append to `README.md`:

```markdown
## Run

```powershell
python -m claude_monitor.app
```

## Test

```powershell
pytest -v
```
```

- [ ] **Step 2: Add packaging instructions**

Append to `README.md`:

```markdown
## Package as Windows exe

```powershell
pyinstaller --noconsole --onefile --name claude-monitor src/claude_monitor/app.py
pyinstaller --noconsole --onefile --name claude-monitor-write-status src/claude_monitor/hook_writer.py
```

Use the packaged `claude-monitor-write-status.exe` in Claude Code hook commands when Python is not installed globally.
```

- [ ] **Step 3: Final verification**

Run: `pytest -v`

Expected: all tests pass.

Run: `python -m claude_monitor.hook_writer waiting --status-file .tmp-status.txt`

Expected: `.tmp-status.txt` contains `waiting`.

Run: `openspec.cmd status --change "add-claude-monitor-floating-window"`

Expected: OpenSpec reports the change artifacts are ready through `plan`.

## Spec Coverage Review

- `desktop-status-monitor` floating presentation: Task 4.
- `desktop-status-monitor` topmost tool-window behavior: Task 4.
- `desktop-status-monitor` status visual mapping: Task 4.
- `desktop-status-monitor` file event updates: Task 5.
- `desktop-status-monitor` user controls: Task 4.
- `claude-hook-status-bridge` status file contract: Task 2 and Task 3.
- `claude-hook-status-bridge` atomic updates: Task 2.
- `claude-hook-status-bridge` silent execution: Task 3 and Task 6.
- `claude-hook-status-bridge` hook example: Task 3.
- `claude-hook-status-bridge` configurable status path: Task 1 and Task 3.


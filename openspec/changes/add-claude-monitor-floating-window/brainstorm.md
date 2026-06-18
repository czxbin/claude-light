Workspace: current directory (git/worktree unavailable)

# Brainstorm: Claude Code Smart Monitor Floating Window

## Background

The user wants a Windows desktop utility that acts as a persistent visual signal for Claude Code status. Claude Code can pause for tool authorization, y/n confirmation, or extra user input while the user is focused in an IDE or browser. The utility should make that waiting state obvious through a small always-on-top floating window.

The repository is not a Git checkout, so `superpowers:using-git-worktrees` could not create or confirm an isolated worktree. Work continues in the current directory.

## Confirmed Goal

Build an OpenSpec change using the `opsx-superpowers` schema for a Windows-only Claude Code monitor that includes:

- A compact, borderless, draggable floating window.
- Always-on-top behavior.
- No taskbar slot.
- Low-idle visual state for `idle`.
- Red flashing alert visual state for `waiting`.
- File-system-event based state updates, not polling loops.
- Claude Code hook configuration and hook-side code.
- Silent background execution with no flashing CMD windows during status changes.

## Approach Options

### Option 1: Python + PySide6 + watchdog

This is the selected approach.

Pros:
- Fastest to implement.
- PySide6 supports frameless windows, always-on-top flags, drag handling, context menus, and timers.
- `watchdog` provides file system event monitoring on Windows through native APIs instead of manual polling.
- PyInstaller can package the app into a single `.exe`.
- Hook helper scripts can be implemented in Python and launched through `pythonw.exe` or packaged helper `.exe` to avoid console windows.

Cons:
- Packaged `.exe` can be larger than native C# or Rust builds.
- Requires careful packaging to include Qt dependencies.

### Option 2: C# WPF + FileSystemWatcher

Pros:
- Native Windows UI behavior.
- `FileSystemWatcher` is built into .NET.
- Good fit for topmost windows, tray apps, and startup registration.

Cons:
- Requires introducing a .NET project.
- Larger upfront project scaffolding for the current lightweight repository.

### Option 3: Rust/Tauri or Native Win32

Pros:
- Lowest runtime overhead.
- Strong distribution story after setup.

Cons:
- Highest implementation cost.
- More complexity than needed for a first version.

## Decision

Use Option 1: Python + PySide6 + watchdog.

The first implementation should be intentionally narrow:

- Support only two states: `idle` and `waiting`.
- Store state in one local text file.
- Watch the parent directory for changes to that state file.
- Treat unknown or missing status as `idle`.
- Provide a Claude Code hooks JSON example and a silent status writer helper.
- Do not implement multi-session aggregation or terminal focusing in the first version.

## Proposed Runtime Shape

```text
Claude Code hook
    |
    v
silent status writer
    |
    v
%LOCALAPPDATA%\ClaudeLight\status.txt
    |
    v
watchdog file event
    |
    v
PySide6 floating monitor
```

## Status Mapping

| Status | Meaning | UI |
| --- | --- | --- |
| `idle` | Claude is idle, completed, or no alert is needed. | Dark gray compact rounded rectangle with low-emphasis text. |
| `waiting` | Claude needs user confirmation, tool permission, or input. | Red flashing or breathing alert with warning glyph/text. |

## Hook Design Direction

Claude Code hooks should call a silent status writer instead of directly controlling the UI.

Expected files:

- `claude_hooks/settings.example.json`: example Claude Code hook configuration.
- `claude_hooks/write_status.py`: silent helper that writes a status string atomically.
- `src/claude_monitor/`: desktop app source.
- `pyproject.toml` or `requirements.txt`: dependencies and packaging entry points.

The exact Claude Code hook event names should be encoded conservatively in an example config and documented as adjustable because hook schemas can vary by Claude Code version. The implementation should keep the hook writer generic: it accepts `idle` or `waiting` and writes the state file.

## Testing Direction

Minimum verification:

- Unit tests for status parsing and atomic status writes.
- App smoke test for importing GUI modules without launching a blocking desktop window.
- Manual test steps for running the floating window and writing `waiting`/`idle` into the status file.
- OpenSpec verify artifact should capture actual verification commands.


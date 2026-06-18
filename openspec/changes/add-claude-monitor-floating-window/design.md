## Context

Claude Code can pause while waiting for tool authorization, y/n confirmation, or additional user input. When the developer is focused in another window, that pause is easy to miss. The requested change adds a Windows-only desktop signal that stays visible and reacts to Claude Code hook events through a local status file.

The current repository only contains OpenSpec scaffolding. There is no existing app code or Git worktree. The first implementation can therefore introduce a small Python application and hook helper without needing to preserve an existing runtime architecture.

Key constraints:

- Windows is the only supported OS for the first version.
- The floating UI must be frameless, draggable, always on top, and not occupy a taskbar slot.
- State changes must be silent and must not flash command prompt windows.
- The monitor must use file system notifications rather than CPU-expensive polling.
- The implementation must include Claude Code hook configuration and hook-side code.

## Goals / Non-Goals

**Goals:**

- Provide a lightweight Windows floating monitor for Claude Code attention states.
- Support `idle` and `waiting` status values.
- React to status-file changes using OS-backed file events.
- Show `idle` as a low-emphasis dark gray state.
- Show `waiting` as a red flashing alert state.
- Provide a generic status writer that Claude Code hooks can invoke.
- Provide example Claude Code hook configuration.
- Keep the first version simple enough to package as a standalone `.exe`.

**Non-Goals:**

- No multi-session aggregation in the first version.
- No automatic activation or foregrounding of the terminal window.
- No Linux or macOS support.
- No network communication, daemon server, database, or cloud dependency.
- No custom configuration UI beyond command-line defaults and documented files.

## Decisions

### D1: Use Python + PySide6 + watchdog

- **Choice**: Implement the monitor in Python using PySide6 for the GUI and watchdog for file event monitoring.
- **Rationale**: This is the fastest path to a Windows desktop utility with frameless windows, topmost flags, context menus, timers, and native file notification support. It also keeps the hook helper and app in one language.
- **Alternatives considered**: C# WPF would be more native but requires more project scaffolding. Rust/Tauri or Win32 would reduce overhead but adds unnecessary implementation complexity for a first version.

### D2: Use local status-file IPC

- **Choice**: Hooks write a status string to a local text file. The monitor watches the file's parent directory and updates UI state when the file changes.
- **Rationale**: A file is simple, debuggable, resilient across process boundaries, and does not require sockets, services, named pipes, or long-running hook processes.
- **Alternatives considered**: Named pipes and localhost HTTP were rejected because they require a running endpoint and add lifecycle complexity. Clipboard or environment variables were rejected because they are not reliable state channels for independent processes.

### D3: Keep the status contract narrow

- **Choice**: Support only `idle` and `waiting` in the first version. Missing, empty, or unknown values resolve to `idle`.
- **Rationale**: The user's document defines exactly two states. A narrow contract reduces UI ambiguity and avoids speculative state mapping.
- **Alternatives considered**: Adding `running`, `error`, or per-session states was rejected as scope creep.

### D4: Separate hook writing from UI behavior

- **Choice**: Claude Code hooks call a silent writer helper; the writer only validates and writes status. The GUI owns all visual behavior.
- **Rationale**: This decouples Claude Code hook details from UI implementation and keeps hook execution short and predictable.
- **Alternatives considered**: Having hooks signal the GUI directly was rejected because it creates tighter coupling and harder failure modes.

### D5: Make silent execution explicit

- **Choice**: Provide hook examples that use `pythonw.exe` or a packaged console-free helper executable for status updates.
- **Rationale**: The PRD explicitly forbids command prompt flashes during state changes. A normal console Python invocation can briefly show a black window depending on how it is launched.
- **Alternatives considered**: Plain `.bat` or visible `python.exe` commands were rejected for violating the silent execution requirement.

## Risks / Trade-offs

[Risk] Claude Code hook event names and payload shapes can vary by Claude Code version. → Mitigation: provide a conservative example config and keep the writer generic so users can map any relevant hook event to `waiting` or `idle`.

[Risk] PyInstaller output may be larger than a native executable. → Mitigation: accept binary size for the first version in exchange for faster delivery and simpler code.

[Risk] Always-on-top behavior can be limited by some exclusive full-screen apps or elevated windows. → Mitigation: use Qt topmost/tool window flags and document the Windows limitation if an app runs at a higher integrity level.

[Risk] File writes may trigger multiple file events. → Mitigation: debounce UI reloads briefly and make status application idempotent.

[Risk] The hook writer could leave a partial file if interrupted. → Mitigation: write atomically by writing a temporary file and replacing the target.

## Migration Plan

1. Add the Python package structure for the monitor app and hook helper.
2. Add dependency metadata for PySide6, watchdog, and test tooling.
3. Add Claude Code hook example configuration and usage documentation.
4. Add tests for status parsing and writer behavior.
5. Package with PyInstaller after local verification.

Rollback strategy: remove the generated hook configuration from Claude Code settings and stop/delete the monitor executable. The monitor only writes and reads a local status file, so rollback does not affect project source code or Claude Code itself.

Acceptance criteria:

- Running the monitor shows a small frameless topmost window.
- Writing `waiting` to the configured status file makes it flash red.
- Writing `idle` returns it to the low-emphasis state.
- Hook writer updates are silent when launched through the documented command.
- Tests for status parsing and writer behavior pass.

## Open Questions

- The exact Claude Code hook event names should be verified against the user's installed Claude Code version during implementation.
- The final default status path should be documented; proposed default is `%LOCALAPPDATA%\ClaudeLight\status.txt`.


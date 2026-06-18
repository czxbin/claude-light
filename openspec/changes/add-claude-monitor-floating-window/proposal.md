## Why

Claude Code can pause for tool authorization or user input while the developer is working in another window. A small Windows floating monitor makes that waiting state immediately visible and reduces idle time caused by missed terminal prompts.

## What Changes

- Add a Windows desktop floating monitor that reads Claude Code status from a local text file.
- Add red flashing `waiting` and dark gray `idle` visual states.
- Add OS-backed file event watching instead of polling.
- Add a silent hook status writer for Claude Code hooks.
- Add example Claude Code hook configuration that maps attention-needed events to `waiting` and completion events to `idle`.
- Add packaging guidance for producing a standalone Windows `.exe`.

## Capabilities

### New Capabilities

- `desktop-status-monitor`: Covers the Windows floating window, status-file watching, UI state mapping, drag behavior, and exit behavior.
- `claude-hook-status-bridge`: Covers Claude Code hook configuration, silent status writer behavior, status file format, and atomic updates.

### Modified Capabilities

None.

## Impact

- Adds a Python desktop application using PySide6 and watchdog.
- Adds hook helper code and Claude Code settings example.
- Adds tests for status parsing and status writes.
- Adds local runtime files under `%LOCALAPPDATA%\ClaudeLight\` by default.
- No network API, database, or existing capability changes.


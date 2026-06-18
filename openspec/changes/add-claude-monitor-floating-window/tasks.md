## 1. Project Structure and Dependencies

- [x] 1.1 Add Python package structure for the monitor app and Claude hook helper
- [x] 1.2 Add dependency metadata for PySide6, watchdog, pytest, and packaging
- [x] 1.3 Add default path handling for the shared status file

## 2. Status Contract and Hook Bridge

- [x] 2.1 Implement status parsing and validation for `idle` and `waiting`
- [x] 2.2 Implement atomic status-file writes with parent directory creation
- [x] 2.3 Add a command-line status writer entry point for Claude Code hooks
- [x] 2.4 Add Claude Code hook configuration examples for `waiting` and `idle`

## 3. Desktop Floating Monitor

- [x] 3.1 Implement the frameless compact PySide6 floating window
- [x] 3.2 Implement always-on-top tool-window behavior without a normal taskbar slot
- [x] 3.3 Implement `idle` and `waiting` visual states, including red flashing alert animation
- [x] 3.4 Implement left-button dragging and right-click Exit behavior

## 4. File Watching and UI Integration

- [x] 4.1 Implement watchdog-based monitoring of the status file parent directory
- [x] 4.2 Debounce file change events and reload status idempotently
- [x] 4.3 Wire file watcher events to the PySide6 UI thread safely

## 5. Verification and Packaging

- [x] 5.1 Add unit tests for status parsing and atomic writer behavior
- [x] 5.2 Add a non-blocking smoke test for importing the monitor application modules
- [x] 5.3 Add documentation for running, testing, hook setup, and packaging as a Windows `.exe`
- [ ] 5.4 Run verification commands and record results in the OpenSpec verify artifact during apply

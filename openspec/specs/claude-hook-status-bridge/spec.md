# claude-hook-status-bridge Specification

## Purpose
TBD - created by archiving change add-claude-monitor-floating-window. Update Purpose after archive.
## Requirements
### Requirement: Status File Contract
The system SHALL use a local text status file as the communication contract between Claude Code hooks and the desktop monitor.

#### Scenario: Writer stores waiting status
- **WHEN** the hook status writer is invoked with `waiting`
- **THEN** the configured status file contains `waiting`

#### Scenario: Writer stores idle status
- **WHEN** the hook status writer is invoked with `idle`
- **THEN** the configured status file contains `idle`

#### Scenario: Writer rejects unsupported status
- **WHEN** the hook status writer is invoked with a value other than `idle` or `waiting`
- **THEN** it fails without writing that unsupported value to the status file

### Requirement: Atomic Status Updates
The system MUST write status updates atomically so the monitor never observes a partial status value.

#### Scenario: Status update replaces old value
- **WHEN** the writer updates the status file
- **THEN** it writes the new value through an atomic replace operation

#### Scenario: Parent directory is missing
- **WHEN** the configured status file parent directory does not exist
- **THEN** the writer creates the parent directory before writing the status

### Requirement: Silent Hook Execution
The hook bridge MUST provide a documented Windows launch path that updates status without flashing a command prompt window.

#### Scenario: Hook uses console-free launcher
- **WHEN** Claude Code invokes the documented hook command
- **THEN** status is updated without opening a visible command prompt window

### Requirement: Claude Code Hook Example
The system SHALL include an example Claude Code hook configuration that maps attention-needed events to `waiting` and completion or stop events to `idle`.

#### Scenario: Example config documents waiting transition
- **WHEN** a user reads the example hook configuration
- **THEN** it shows how to invoke the writer with `waiting` for events that require user attention

#### Scenario: Example config documents idle transition
- **WHEN** a user reads the example hook configuration
- **THEN** it shows how to invoke the writer with `idle` for events that clear the alert

### Requirement: Configurable Status Path
The system SHALL allow the status file path to be configured while providing a Windows default path under the user's local application data directory.

#### Scenario: Default status path is used
- **WHEN** no status path override is provided
- **THEN** the writer and monitor use a default path under `%LOCALAPPDATA%`

#### Scenario: Explicit status path is used
- **WHEN** a status path override is provided
- **THEN** the writer writes to that explicit path


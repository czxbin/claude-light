## ADDED Requirements

### Requirement: Floating Window Presentation
The system SHALL display a compact Windows floating window that is frameless, visually minimal, and positioned near the bottom-right of the primary display on first launch.

#### Scenario: First launch creates compact window
- **WHEN** the monitor application starts without a saved position
- **THEN** it displays a compact frameless window near the bottom-right of the primary display

#### Scenario: Window does not use standard chrome
- **WHEN** the floating window is visible
- **THEN** it has no standard Windows title bar or resize border

### Requirement: Topmost Tool Window Behavior
The system SHALL keep the floating window above normal application windows and MUST avoid creating a normal taskbar slot for the monitor.

#### Scenario: Monitor stays above normal windows
- **WHEN** the user switches from the terminal to another normal desktop application
- **THEN** the monitor window remains visible above that application

#### Scenario: Monitor avoids taskbar clutter
- **WHEN** the monitor application is running
- **THEN** it does not appear as a normal application button in the Windows taskbar

### Requirement: Status Visual Mapping
The system SHALL map `idle` to a low-emphasis dark gray visual state and `waiting` to a red flashing alert state.

#### Scenario: Idle status shows low-emphasis state
- **WHEN** the monitor reads status `idle`
- **THEN** the floating window displays a dark gray low-emphasis state

#### Scenario: Waiting status shows alert state
- **WHEN** the monitor reads status `waiting`
- **THEN** the floating window displays a red flashing or breathing alert state

#### Scenario: Unknown status is safe
- **WHEN** the monitor reads an empty, missing, or unknown status value
- **THEN** the floating window displays the `idle` visual state

### Requirement: File Event Based State Updates
The system MUST update UI status in response to operating-system file change notifications and MUST NOT use an unbounded polling loop to detect status changes.

#### Scenario: Status file changes to waiting
- **WHEN** the status file changes from `idle` to `waiting`
- **THEN** the monitor updates to the red alert state without requiring application restart

#### Scenario: Status file changes to idle
- **WHEN** the status file changes from `waiting` to `idle`
- **THEN** the monitor stops alerting and returns to the dark gray state without requiring application restart

### Requirement: User Window Controls
The system SHALL allow the user to drag the floating window with the left mouse button and exit the monitor from a right-click context menu.

#### Scenario: User drags window
- **WHEN** the user holds the left mouse button on the floating window and moves the mouse
- **THEN** the monitor window moves with the cursor

#### Scenario: User exits monitor
- **WHEN** the user chooses Exit from the floating window context menu
- **THEN** the monitor application terminates cleanly


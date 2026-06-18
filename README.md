# Claude Code Monitor

Windows floating monitor for Claude Code attention states.

## Status file

Default path: `%LOCALAPPDATA%\ClaudeLight\status.txt`

Valid values:

- `idle`
- `waiting`

## Hook setup

Copy the relevant entries from `claude_hooks/settings.example.json` into your Claude Code settings. The example uses `pythonw.exe` so status changes do not open a visible command prompt window.

From a source checkout, configure imports before using `pythonw.exe -m claude_monitor.hook_writer ...` in hooks:

```powershell
$env:PYTHONPATH = "src"
pythonw.exe -m claude_monitor.hook_writer waiting
pythonw.exe -m claude_monitor.hook_writer idle
```

After packaging, use `claude-monitor-write-status.exe waiting` and `claude-monitor-write-status.exe idle` in hook commands instead.

If your Claude Code version uses different hook event names, keep the command shape and map the events that mean "needs attention" to `waiting`, and events that clear the alert to `idle`.

## Manual status test

From a source checkout, install the package first or set the PowerShell import path:

```powershell
$env:PYTHONPATH = "src"
python -m claude_monitor.hook_writer waiting
python -m claude_monitor.hook_writer idle
```

## Run

```powershell
$env:PYTHONPATH = "src"
python -m claude_monitor.app
```

If `%LOCALAPPDATA%` is not writable in your current shell, point both the
monitor and hook writer at a project-local status file:

```powershell
$env:PYTHONPATH = "src"
python -m claude_monitor.app --status-file .\.runtime\status.txt
```

## Test

```powershell
pytest -v
```

If your environment cannot use the default test command, run the focused fallback with an explicit venv Python and temporary pytest directory:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_status.py tests\test_imports.py tests\test_watcher.py --basetemp=.\.tmp\pytest -p no:cacheprovider
```

## Package as Windows exe

```powershell
pyinstaller --paths src --noconsole --onefile --name claude-monitor src/claude_monitor/app.py
pyinstaller --paths src --noconsole --onefile --name claude-monitor-write-status src/claude_monitor/hook_writer.py
```

Use the packaged `claude-monitor-write-status.exe` in Claude Code hook commands when Python is not installed globally. Keep the hook event names adjustable: Claude Code hook event names can vary by version, so map whichever events mean "needs attention" to `waiting` and whichever events clear the alert to `idle`.

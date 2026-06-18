# Retrospective: add-claude-monitor-floating-window

> Written: 2026-06-18 (after verify passed)
> Commit range: `4b825dc..189da6f`
> Workspace: current directory (git/worktree unavailable during brainstorm; local git repository initialized later)
> Completion mode: local only (no push, no PR by Codex)

---

## 0. Evidence

- **Commits**: 2 (`4b825dc..189da6f`)
- **Diff size**: +2692 lines across 28 files
- **Tasks**: 18/18 completed
- **New external dependencies**: PySide6>=6.7, watchdog>=4.0; dev dependencies pytest>=8.0, pyinstaller>=6.0 (`pyproject.toml`)
- **Test coverage signal**: 12 pytest tests passed (`tests/test_status.py`, `tests/test_imports.py`, `tests/test_watcher.py`)
- **OpenSpec validate state**: pass (`openspec validate --all --json`)

---

## 1. Wins

- The local status-file contract stayed narrow and testable: `src/claude_monitor/status.py` supports only `idle` and `waiting`, and `tests/test_status.py` covers parsing, validation, missing files, atomic replacement, and fixed-temp-path regression.
- The hook bridge remained decoupled from the UI: `src/claude_monitor/hook_writer.py` only writes status, while `src/claude_monitor/app.py` owns visual behavior.
- The watchdog integration caught a real event-path bug before completion: `tests/test_watcher.py` now covers created, modified, moved-away, moved-into-place, unrelated events, and idempotent lifecycle behavior.
- The final verification used concrete commands: pytest reported 12 passing tests and `py_compile` succeeded for all monitor modules in `verify.md`.

---

## 2. Misses

- 🟡 [painful | evidence: `verify.md` Delta Spec Sync State] Delta specs are not yet synced into `openspec/specs/`; archive must do this rather than manual patching.
- 🟡 [painful | evidence: `brainstorm.md` workspace note] The workspace was not a Git repository during brainstorm/apply, so worktree isolation and normal commit-range verification could not work until Git was initialized later.
- 🟡 [painful | evidence: `README.md` documentation review] README initially used Unix-style `PYTHONPATH=src` and PyInstaller commands without `--paths src`; review caught this before completion.
- 📌 [nit | evidence: command output warnings] Git commands repeatedly warned that `C:\Users\wuxiaobin/.config/git/ignore` was not readable. This did not block the cycle but made command output noisier.

---

## 3. Plan deviations

| Plan task | What changed | Why |
|-----------|--------------|-----|
| 2.2 Atomic status-file writes | `write_status` moved from a fixed `status.txt.tmp` path to a unique same-directory temp file. | Code quality review identified concurrent hook writers could collide on a fixed temp file. |
| 4.1 Watchdog file monitoring | Event filtering was expanded to distinguish created/modified `src_path` from moved `src_path`/`dest_path`. | Code quality review identified watchdog 6 events could have empty `dest_path`, preventing reloads. |
| 5.3 Documentation | README commands were revised for PowerShell and `src` layout packaging. | Documentation review found the first version was not copyable for Windows users. |

---

## 4. Skill / workflow compliance

| Skill | State | Note |
|-------|-------|------|
| superpowers:using-git-worktrees | used, but no worktree created | Workspace was not a Git repository at brainstorm time. |
| superpowers:brainstorming | used | Captured approach selection in `brainstorm.md`. |
| superpowers:writing-plans | used | Produced `plan.md` with micro-steps. |
| superpowers:subagent-driven-development | used | Implementation and review tasks were dispatched to subagents. |
| (transitive) superpowers:test-driven-development | used | Red/green evidence appears in status and watcher task reports. |
| (transitive) superpowers:requesting-code-review | used | Spec and quality reviews caught watcher and docs issues. |
| superpowers:finishing-a-development-branch | pending local completion | Should run after retrospective and archive. |

### Deliberately Skipped Skills

- **None**

---

## 5. Surprises

- Assumption: The workspace would already be a Git repository. Reality: `git status` initially failed with `fatal: not a git repository`. Impact: worktree setup and verify commit-range evidence needed a later local `git init`.
- Assumption: A simple temp path would be sufficient for status writes. Reality: concurrent Claude hook writers can collide on `status.txt.tmp`. Impact: `write_status` needed unique same-directory temp files and a regression test.
- Assumption: Watchdog event objects could be handled uniformly with a preferred `dest_path`. Reality: created/modified events can have empty `dest_path`; moved events need both source and destination checks. Impact: watcher filtering and tests were tightened.

---

## 6. Promote candidates - long-term learning

- [ ] 🟡 Require Git repository setup before choosing `opsx-superpowers`
  -> **Promote to**: schema
  > **Why**: This schema's verify phase requires commit evidence and worktree decisions; starting in a non-Git directory created late-cycle friction.
  > **How to apply**: When `openspec/config.yaml` uses `opsx-superpowers`, require Git initialization or an explicit alternate verify path before artifact generation.

- [ ] 🟡 Prefer unique same-directory temp files for hook status writers
  -> **Promote to**: CLAUDE.md
  > **Why**: Fixed temp names can fail under concurrent hook invocations even when each individual write is atomic.
  > **How to apply**: Any local IPC writer that uses file replacement should create a unique temp file in the target directory before `os.replace`.

- [ ] 🟡 Test watchdog event filtering with fake events
  -> **Promote to**: skill
  > **Why**: The initial implementation looked correct but missed real watchdog event shape differences.
  > **How to apply**: For file-watcher code, add unit tests for created, modified, moved-away, moved-into-place, and unrelated paths.

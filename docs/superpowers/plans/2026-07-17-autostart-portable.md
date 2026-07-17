# Autostart Portable Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Windows user-level autostart toggle that launches JoyHarness minimized to tray, then rebuild the portable package.

**Architecture:** Keep registry writes isolated in `src/autostart.py`. `src/main.py` adds `--minimized`. `src/gui.py` exposes an autostart checkbox and hides the window on minimized startup.

**Tech Stack:** Python stdlib, Windows HKCU Run registry, existing ttkbootstrap UI, PyInstaller.

---

### Task 1: Autostart Registry Module

**Files:**
- Create: `src/autostart.py`
- Create: `tests/test_autostart.py`

- [ ] Test source-mode command uses `wscript.exe //nologo start.vbs --minimized`.
- [ ] Test frozen-mode command uses `JoyHarness.exe --minimized`.
- [ ] Test enabling writes HKCU Run and disabling removes it.

### Task 2: CLI and UI Integration

**Files:**
- Modify: `src/main.py`
- Modify: `src/gui.py`
- Modify: `src/config_loader.py`
- Modify: `start.vbs`
- Test: `tests/test_main_startup.py`, `tests/test_autostart.py`

- [ ] Add `--minimized` parser option.
- [ ] Add GUI autostart checkbox that calls the autostart module.
- [ ] Hide the window at startup when `--minimized` is passed.
- [ ] Make `start.vbs` forward arguments to Python.

### Task 3: Verification and Package

**Files:**
- Modify: `tasks/todo.md`

- [ ] Run targeted unit tests.
- [ ] Run `compileall` and `pip check`.
- [ ] Rebuild PyInstaller output with `JoyHarness.spec`.
- [ ] Recreate `release/JoyHarness-windows-x64-portable.zip`.

# Single Instance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent multiple JoyHarness controller-listening instances from running at the same time.

**Architecture:** Add a small `src/single_instance.py` module that owns process-wide locking. `src/main.py` acquires the lock after parsing/logging and before any Joy-Con access, and exits early if another instance owns it.

**Tech Stack:** Python stdlib only: Windows named mutex via `ctypes`; POSIX file lock via `fcntl`.

---

### Task 1: Single Instance Lock

**Files:**
- Create: `src/single_instance.py`
- Create: `tests/test_single_instance.py`

- [ ] Write tests proving a unique lock can be acquired once and a second acquire fails.
- [ ] Implement a `SingleInstanceLock` with `acquire()` and `release()`.
- [ ] Verify `python -m unittest tests.test_single_instance`.

### Task 2: Startup Guard

**Files:**
- Modify: `src/main.py`
- Modify: `tests/test_main_startup.py`

- [ ] Add a test proving `main()` returns before config/joystick work when the lock is unavailable.
- [ ] Acquire the lock before modes that touch Joy-Con hardware.
- [ ] Leave `--list-controls` free to run without the lock.
- [ ] Verify targeted startup tests.

### Task 3: Full Verification

**Files:**
- Modify: `tasks/todo.md`

- [ ] Run the targeted unit test suite.
- [ ] Run `compileall` and `pip check`.
- [ ] Restart JoyHarness and confirm a second launch exits without creating another active GUI/controller instance.

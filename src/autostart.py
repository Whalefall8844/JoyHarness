"""Windows user-level autostart integration."""

from __future__ import annotations

import sys
from pathlib import Path


RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE_NAME = "JoyHarness"


def is_supported() -> bool:
    return sys.platform == "win32"


def _quote(path: Path | str) -> str:
    return f'"{path}"'


def build_autostart_command(
    executable: Path | None = None,
    project_root: Path | None = None,
    frozen: bool | None = None,
) -> str:
    if executable is None:
        executable = Path(sys.executable)
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent
    if frozen is None:
        frozen = bool(getattr(sys, "frozen", False))

    if frozen:
        return f"{_quote(executable)} --minimized"
    return f"wscript.exe //nologo {_quote(project_root / 'start.vbs')} --minimized"


def _load_winreg(registry=None):
    if registry is not None:
        return registry
    import winreg
    return winreg


def _open_run_key(registry, access: int, create: bool = False):
    if create and hasattr(registry, "CreateKeyEx"):
        return registry.CreateKeyEx(registry.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, access)
    return registry.OpenKey(registry.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, access)


def _close_key(key) -> None:
    close = getattr(key, "Close", None)
    if close:
        close()


def set_autostart_enabled(enabled: bool, command: str | None = None, registry=None) -> bool:
    if not is_supported() and registry is None:
        return False

    reg = _load_winreg(registry)
    if command is None:
        command = build_autostart_command()

    access = reg.KEY_SET_VALUE
    key = _open_run_key(reg, access, create=enabled)
    try:
        if enabled:
            reg.SetValueEx(key, RUN_VALUE_NAME, 0, reg.REG_SZ, command)
        else:
            try:
                reg.DeleteValue(key, RUN_VALUE_NAME)
            except FileNotFoundError:
                pass
    finally:
        _close_key(key)
    return True


def is_autostart_enabled(expected_command: str | None = None, registry=None) -> bool:
    if not is_supported() and registry is None:
        return False

    reg = _load_winreg(registry)
    try:
        key = _open_run_key(reg, reg.KEY_QUERY_VALUE)
        try:
            value, _value_type = reg.QueryValueEx(key, RUN_VALUE_NAME)
        finally:
            _close_key(key)
    except FileNotFoundError:
        return False

    if expected_command is None:
        return True
    return value == expected_command

"""Platform-specific permission checks.

Windows: Administrator privileges (required by keyboard library).
macOS:   Accessibility permission (required by pynput).
"""

from __future__ import annotations

import sys
import logging

logger = logging.getLogger(__name__)


def has_required_permissions() -> bool:
    """Check if the process has the permissions needed for keyboard simulation."""
    if sys.platform == "win32":
        return _check_windows_admin()
    elif sys.platform == "darwin":
        return _check_macos_accessibility()
    return True


def get_permission_warning() -> str:
    """Return a user-facing warning message for missing permissions."""
    if sys.platform == "win32":
        return (
            "警告：当前没有以管理员身份运行，键盘模拟可能无法生效。\n"
            "      可尝试使用 run.bat，或在管理员 PowerShell 中启动。\n"
        )
    elif sys.platform == "darwin":
        return (
            "警告：尚未授予辅助功能权限。\n"
            "      请前往：系统设置 → 隐私与安全性 → 辅助功能\n"
            "      将当前终端应用（如 Terminal、iTerm2）加入允许列表。\n"
            "      然后重启 JoyHarness。\n"
        )
    return ""


def _check_windows_admin() -> bool:
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
        return False


def _check_macos_accessibility() -> bool:
    """Check macOS Accessibility permission by attempting a pynput operation."""
    try:
        import subprocess
        result = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to key code 0'],
            capture_output=True,
            timeout=3,
        )
        return result.returncode == 0
    except Exception:
        logger.debug("Accessibility check failed, assuming not granted")
        return False

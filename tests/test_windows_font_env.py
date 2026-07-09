import os
import sys
import unittest
from unittest.mock import patch

from src.main import _ensure_windows_font_repository_env, _install_crash_diagnostics


class WindowsFontEnvTest(unittest.TestCase):
    def test_sets_windir_from_systemroot_on_windows(self) -> None:
        with patch.object(sys, "platform", "win32"), patch.dict(
            os.environ,
            {"SystemRoot": r"C:\Windows"},
            clear=True,
        ):
            _ensure_windows_font_repository_env()

            self.assertEqual(os.environ["WINDIR"], r"C:\Windows")

    def test_leaves_existing_windir_unchanged(self) -> None:
        with patch.object(sys, "platform", "win32"), patch.dict(
            os.environ,
            {"WINDIR": r"D:\Windows", "SystemRoot": r"C:\Windows"},
            clear=True,
        ):
            _ensure_windows_font_repository_env()

            self.assertEqual(os.environ["WINDIR"], r"D:\Windows")

    def test_install_crash_diagnostics_enables_faulthandler(self) -> None:
        with patch("src.main.faulthandler.enable") as enable:
            _install_crash_diagnostics()

        enable.assert_called_once_with(all_threads=True)


if __name__ == "__main__":
    unittest.main()

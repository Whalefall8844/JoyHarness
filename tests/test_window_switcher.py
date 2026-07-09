import sys
import unittest

from src.window_switcher import _matches_app_name


class WindowSwitcherNameMatchingTest(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "Windows exe matching only")
    def test_windows_exe_matching_is_case_insensitive(self) -> None:
        self.assertTrue(_matches_app_name("codex.exe", ["Codex.exe"]))
        self.assertTrue(_matches_app_name("workbuddy.exe", ["WorkBuddy.exe"]))
        self.assertTrue(_matches_app_name("chrome.exe", ["chrome.exe"]))


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from unittest.mock import patch

from src import keyboard_output


@unittest.skipIf(sys.platform == "darwin", "Windows keyboard backend only")
class WindowsKeyboardOutputTest(unittest.TestCase):
    def tearDown(self) -> None:
        keyboard_output._held_keys.clear()

    def test_right_alt_aliases_use_extended_scan_code(self) -> None:
        for key_name in ("right alt", "alt_r"):
            with self.subTest(key_name=key_name):
                keyboard_output._held_keys.clear()
                with patch("src.keyboard_output._keyboard.press") as press_key:
                    keyboard_output.press(key_name)

                press_key.assert_called_once_with(57400)

    def test_right_ctrl_aliases_use_extended_scan_code(self) -> None:
        for key_name in ("right ctrl", "ctrl_r"):
            with self.subTest(key_name=key_name):
                keyboard_output._held_keys.clear()
                with patch("src.keyboard_output._keyboard.press") as press_key:
                    keyboard_output.press(key_name)

                press_key.assert_called_once_with(57373)

    def test_right_modifier_aliases_are_valid_keys(self) -> None:
        self.assertTrue(keyboard_output.is_valid_key("right alt"))
        self.assertTrue(keyboard_output.is_valid_key("alt_r"))
        self.assertTrue(keyboard_output.is_valid_key("right ctrl"))
        self.assertTrue(keyboard_output.is_valid_key("ctrl_r"))


if __name__ == "__main__":
    unittest.main()

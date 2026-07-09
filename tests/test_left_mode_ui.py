import unittest
import json
import tempfile
from unittest.mock import Mock, patch

from src.config_loader import load_config
from src.constants import DEFAULT_MAPPINGS_LEFT, get_button_indices, get_button_names
from src.gui import _app_target_label, _window_title
from src.settings_window import SettingsWindow, _app_target_help_text, _mappable_buttons_for_mode


class _Value:
    def __init__(self, value: str) -> None:
        self._value = value

    def get(self) -> str:
        return self._value


class LeftModeUITest(unittest.TestCase):
    def test_left_mode_title_uses_left_profile_label(self) -> None:
        title = _window_title("single_left")

        self.assertEqual(title, "JoyHarness [左手柄]")

    def test_app_target_labels_are_not_hard_coded_to_right_button(self) -> None:
        self.assertEqual(_app_target_label("single_left"), "窗口切换目标：")
        self.assertEqual(_app_target_help_text("single_left"), "设置窗口切换可在哪些应用间切换：")

    def test_left_mode_settings_use_left_side_buttons(self) -> None:
        buttons = _mappable_buttons_for_mode("single_left")

        self.assertIn("DPadUp", buttons)
        self.assertIn("DPadDown", buttons)
        self.assertIn("DPadLeft", buttons)
        self.assertIn("DPadRight", buttons)
        self.assertIn("L", buttons)
        self.assertIn("ZL", buttons)
        self.assertIn("Minus", buttons)
        self.assertIn("Capture", buttons)
        self.assertIn("LStick", buttons)
        self.assertIn("SL", buttons)
        self.assertIn("SR", buttons)
        self.assertNotIn("A", buttons)
        self.assertNotIn("B", buttons)
        self.assertNotIn("X", buttons)
        self.assertNotIn("Y", buttons)
        self.assertNotIn("R", buttons)
        self.assertNotIn("ZR", buttons)
        self.assertNotIn("Plus", buttons)
        self.assertNotIn("Home", buttons)
        self.assertNotIn("RStick", buttons)

    def test_left_mode_button_names_use_direction_pad_labels(self) -> None:
        button_names = set(get_button_names("single_left").values())

        self.assertTrue({"DPadUp", "DPadDown", "DPadLeft", "DPadRight"}.issubset(button_names))
        self.assertFalse({"A", "B", "X", "Y"} & button_names)

    def test_left_mode_button_indices_match_observed_physical_layout(self) -> None:
        indices = get_button_indices("single_left")

        self.assertEqual(indices["DPadUp"], 3)
        self.assertEqual(indices["DPadDown"], 0)
        self.assertEqual(indices["DPadLeft"], 1)
        self.assertEqual(indices["DPadRight"], 2)
        self.assertEqual(indices["Minus"], 6)
        self.assertEqual(indices["LStick"], 7)
        self.assertEqual(indices["L"], 17)
        self.assertEqual(indices["ZL"], 19)
        self.assertEqual(indices["SL"], 9)
        self.assertEqual(indices["SR"], 10)

    def test_left_default_mappings_use_direction_pad_labels(self) -> None:
        buttons = DEFAULT_MAPPINGS_LEFT["buttons"]
        stick_directions = DEFAULT_MAPPINGS_LEFT["stick_directions"]

        self.assertTrue({"DPadUp", "DPadDown", "DPadLeft", "DPadRight"}.issubset(buttons))
        self.assertFalse({"A", "B", "X", "Y"} & set(buttons))
        for direction in ("up", "down", "left", "right"):
            self.assertEqual(
                stick_directions[direction],
                {"action": "auto", "key": direction, "repeat": 100},
            )

    def test_old_left_abxy_config_is_migrated_to_direction_pad_labels(self) -> None:
        old_config = {
            "active_profile": "single_left",
            "profiles": {
                "single_left": {
                    "mappings": {
                        "buttons": {
                            "A": {"action": "tap", "key": "enter"},
                            "B": {"action": "tap", "key": "escape"},
                            "X": {"action": "tap", "key": "backspace"},
                            "Y": {"action": "sequence", "keys": ["alt", "tab"]},
                        },
                    },
                },
            },
        }

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(old_config, f)
            path = f.name

        config = load_config(path)
        buttons = config["profiles"]["single_left"]["mappings"]["buttons"]

        self.assertEqual(buttons["DPadDown"], {"action": "tap", "key": "enter"})
        self.assertEqual(buttons["DPadRight"], {"action": "tap", "key": "escape"})
        self.assertEqual(buttons["DPadLeft"], {"action": "tap", "key": "backspace"})
        self.assertEqual(buttons["DPadUp"], {"action": "sequence", "keys": ["alt", "tab"]})
        self.assertNotIn("A", buttons)
        self.assertNotIn("B", buttons)
        self.assertNotIn("X", buttons)
        self.assertNotIn("Y", buttons)

    def test_old_left_tap_stick_directions_are_migrated_to_auto_repeat(self) -> None:
        old_config = {
            "active_profile": "single_left",
            "profiles": {
                "single_left": {
                    "mappings": {
                        "stick_directions": {
                            "up": {"action": "tap", "key": "up"},
                            "down": {"action": "tap", "key": "down"},
                            "left": {"action": "tap", "key": "left"},
                            "right": {"action": "tap", "key": "right"},
                        },
                    },
                },
            },
        }

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(old_config, f)
            path = f.name

        config = load_config(path)
        stick_directions = config["profiles"]["single_left"]["mappings"]["stick_directions"]

        for direction in ("up", "down", "left", "right"):
            self.assertEqual(
                stick_directions[direction],
                {"action": "auto", "key": direction, "repeat": 100},
            )

    def test_apply_updates_left_profile_without_changing_right_profile(self) -> None:
        config = {
            "mappings": {
                "buttons": {
                    "L": {"action": "window_switch"},
                },
                "stick_directions": {},
            },
            "profiles": {
                "single_left": {
                    "mappings": {
                        "buttons": {
                            "L": {"action": "window_switch"},
                        },
                        "stick_directions": {},
                    },
                },
                "single_right": {
                    "mappings": {
                        "buttons": {
                            "R": {"action": "window_switch"},
                        },
                        "stick_directions": {},
                    },
                },
            },
        }

        window = SettingsWindow.__new__(SettingsWindow)
        window._mode = "single_left"
        window._config = config
        window._rows = {
            "L": {
                "action_var": _Value("按住"),
                "key_var": _Value("shift"),
            },
        }
        window._key_mapper = Mock()
        window._window_cycler = Mock()
        window._main_window = None
        window._win = Mock()
        window._collect_apps = Mock(return_value=({}, []))

        with (
            patch("src.settings_window.set_known_apps"),
            patch("src.config_loader.save_config"),
        ):
            SettingsWindow._apply(window)

        self.assertEqual(
            config["profiles"]["single_left"]["mappings"]["buttons"]["L"],
            {"action": "hold", "key": "shift"},
        )
        self.assertEqual(
            config["profiles"]["single_right"]["mappings"]["buttons"]["R"],
            {"action": "window_switch"},
        )
        window._key_mapper.switch_profile.assert_called_once_with(config, "single_left")
        window._win.destroy.assert_called_once()


if __name__ == "__main__":
    unittest.main()

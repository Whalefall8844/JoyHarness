import os
import sys
import unittest
from unittest.mock import Mock, patch

from src.main import _get_pairing_instructions, _resolve_initial_joystick, _run_rumble_test, build_parser, main


class MainStartupTest(unittest.TestCase):
    def test_normal_startup_disables_sdl_haptic_axes(self) -> None:
        self.assertEqual(os.environ.get("SDL_JOYSTICK_HAPTIC_AXES"), "0")

    def test_windows_pairing_instructions_are_not_right_only(self) -> None:
        with patch("src.main.sys.platform", "win32"):
            instructions = _get_pairing_instructions()

        self.assertIn("配对说明", instructions)
        self.assertIn("蓝牙", instructions)
        self.assertIn("Joy-Con L", instructions)
        self.assertIn("Joy-Con R", instructions)
        self.assertNotIn("select 'Joy-Con R' in Bluetooth list", instructions)

    def test_waits_for_joycon_when_initial_scan_finds_none(self) -> None:
        joystick = Mock()
        with (
            patch("src.main.find_joycon", return_value=None) as find,
            patch("src.main.wait_for_reconnection", return_value=joystick) as wait,
            patch("builtins.print"),
        ):
            result = _resolve_initial_joystick(None)

        find.assert_called_once_with(None)
        wait.assert_called_once_with(None)
        self.assertIs(result, joystick)

    def test_parser_accepts_rumble_test_flag(self) -> None:
        args = build_parser().parse_args(["--rumble-test"])

        self.assertTrue(args.rumble_test)

    def test_run_rumble_test_uses_current_joycon_once(self) -> None:
        joystick = Mock()
        with (
            patch("src.main.pygame.display.init") as display_init,
            patch("src.main.pygame.joystick.init") as joystick_init,
            patch("src.main.pygame.quit") as pygame_quit,
            patch("src.main.find_joycon", return_value=joystick) as find,
            patch("src.main.test_pygame_rumble", return_value=True) as rumble,
            patch("builtins.print"),
        ):
            result = _run_rumble_test(3)

        self.assertTrue(result)
        display_init.assert_called_once()
        joystick_init.assert_called_once()
        find.assert_called_once_with(3)
        rumble.assert_called_once_with(joystick)
        pygame_quit.assert_called_once()

    def test_rumble_test_does_not_load_config_or_start_gui(self) -> None:
        with (
            patch.object(sys, "argv", ["python", "--rumble-test"]),
            patch("src.main._run_rumble_test") as rumble,
            patch("src.main.load_config") as load_config,
            patch("src.main.has_required_permissions", return_value=True),
        ):
            main()

        rumble.assert_called_once_with(None)
        load_config.assert_not_called()


if __name__ == "__main__":
    unittest.main()

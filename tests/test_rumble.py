import unittest
from unittest.mock import Mock

from src.rumble import test_pygame_rumble


class RumbleTest(unittest.TestCase):
    def test_returns_true_when_pygame_rumble_succeeds(self) -> None:
        joystick = Mock()
        joystick.get_name.return_value = "Nintendo Switch Joy-Con (L)"
        joystick.rumble.return_value = True

        result = test_pygame_rumble(joystick)

        self.assertTrue(result)
        joystick.rumble.assert_called_once_with(0.25, 0.25, 120)

    def test_returns_false_when_pygame_rumble_is_not_supported(self) -> None:
        joystick = Mock()
        joystick.get_name.return_value = "Nintendo Switch Joy-Con (L)"
        joystick.rumble.return_value = False

        with self.assertLogs("src.rumble", level="WARNING"):
            result = test_pygame_rumble(joystick)

        self.assertFalse(result)

    def test_returns_false_when_pygame_rumble_raises(self) -> None:
        joystick = Mock()
        joystick.get_name.return_value = "Nintendo Switch Joy-Con (L)"
        joystick.rumble.side_effect = RuntimeError("SDL rumble failed")

        with self.assertLogs("src.rumble", level="WARNING"):
            result = test_pygame_rumble(joystick)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

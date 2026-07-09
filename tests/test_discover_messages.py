import unittest

from src.joycon_reader import _no_joystick_message


class DiscoverMessagesTest(unittest.TestCase):
    def test_no_joystick_message_is_not_right_only(self) -> None:
        message = _no_joystick_message()

        self.assertIn("未找到手柄", message)
        self.assertIn("Joy-Con", message)
        self.assertNotIn("Joy-Con R is connected", message)


if __name__ == "__main__":
    unittest.main()

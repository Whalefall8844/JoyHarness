import threading
import unittest
from unittest.mock import Mock

from src.tray_icon import _make_quit_handler


class TrayIconTest(unittest.TestCase):
    def test_quit_handler_requests_gui_shutdown(self) -> None:
        stop_event = threading.Event()
        icon = Mock()
        on_quit = Mock()

        handler = _make_quit_handler(stop_event, on_quit=on_quit)
        handler(icon, Mock())

        icon.stop.assert_called_once()
        self.assertTrue(stop_event.is_set())
        on_quit.assert_called_once()


if __name__ == "__main__":
    unittest.main()

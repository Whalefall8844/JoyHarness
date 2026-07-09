import queue
import threading
import tkinter as tk
import unittest
from unittest.mock import Mock

from src.switcher_overlay import SwitcherOverlay


class SwitcherOverlayScheduleTest(unittest.TestCase):
    def test_schedule_from_worker_thread_queues_without_calling_tk(self) -> None:
        overlay = object.__new__(SwitcherOverlay)
        overlay._root_tk = Mock()
        overlay._ui_queue = queue.Queue()
        overlay._closed = False

        worker = threading.Thread(target=lambda: overlay._schedule(lambda: None))
        worker.start()
        worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        overlay._root_tk.after.assert_not_called()
        self.assertEqual(overlay._ui_queue.qsize(), 1)

    def test_schedule_ignores_tcl_errors_after_root_is_unavailable(self) -> None:
        overlay = object.__new__(SwitcherOverlay)
        root = Mock()
        root.after.side_effect = tk.TclError("application has been destroyed")
        overlay._root_tk = root
        overlay._ui_queue = queue.Queue()
        overlay._closed = False

        overlay._drain_queue()

        root.after.assert_called_once()
        self.assertTrue(overlay._closed)


if __name__ == "__main__":
    unittest.main()

import unittest

from src.joycon_reader import _StickDirectionDebouncer


class StickDirectionDebouncerTest(unittest.TestCase):
    def test_single_frame_direction_spike_is_ignored(self) -> None:
        debouncer = _StickDirectionDebouncer(enter_frames=2, release_frames=2)

        self.assertEqual(debouncer.update("left"), (None, None))
        self.assertEqual(debouncer.update(None), (None, None))
        self.assertEqual(debouncer.update(None), (None, None))

    def test_direction_dispatches_after_consecutive_frames(self) -> None:
        debouncer = _StickDirectionDebouncer(enter_frames=2, release_frames=2)

        self.assertEqual(debouncer.update("left"), (None, None))
        self.assertEqual(debouncer.update("left"), ("direction", "left"))
        self.assertEqual(debouncer.update("left"), (None, None))

    def test_center_dispatches_after_consecutive_center_frames(self) -> None:
        debouncer = _StickDirectionDebouncer(enter_frames=2, release_frames=2)

        debouncer.update("left")
        self.assertEqual(debouncer.update("left"), ("direction", "left"))
        self.assertEqual(debouncer.update(None), (None, None))
        self.assertEqual(debouncer.update(None), ("centered", None))
        self.assertEqual(debouncer.update(None), (None, None))

    def test_direction_change_requires_consecutive_frames(self) -> None:
        debouncer = _StickDirectionDebouncer(enter_frames=2, release_frames=2)

        debouncer.update("left")
        self.assertEqual(debouncer.update("left"), ("direction", "left"))
        self.assertEqual(debouncer.update("right"), (None, None))
        self.assertEqual(debouncer.update("right"), ("direction", "right"))


if __name__ == "__main__":
    unittest.main()

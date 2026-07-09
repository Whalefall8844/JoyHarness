import unittest
from unittest.mock import patch

from src.joycon_reader import _calibrate_baseline


class FakeJoystick:
    def __init__(self, axes: list[float]) -> None:
        self._axes = axes

    def get_numaxes(self) -> int:
        return len(self._axes)

    def get_axis(self, index: int) -> float:
        return self._axes[index]


class FakeClock:
    def tick(self, _fps: int) -> None:
        pass


class JoyConBaselineTest(unittest.TestCase):
    def test_keeps_center_offset_when_it_is_inside_deadzone(self) -> None:
        joystick = FakeJoystick([0.196, 0.0])

        with (
            patch("src.joycon_reader.pygame.event.pump"),
            patch("src.joycon_reader.pygame.time.Clock", return_value=FakeClock()),
        ):
            baseline = _calibrate_baseline(
                joystick,
                axis_x=1,
                axis_y=0,
                samples=3,
                max_magnitude=0.2,
            )

        self.assertAlmostEqual(baseline[0], 0.0)
        self.assertAlmostEqual(baseline[1], 0.196)

    def test_rejects_reconnect_baseline_when_it_exceeds_deadzone(self) -> None:
        joystick = FakeJoystick([0.342, 0.0])

        with (
            patch("src.joycon_reader.pygame.event.pump"),
            patch("src.joycon_reader.pygame.time.Clock", return_value=FakeClock()),
            self.assertLogs("src.joycon_reader", level="WARNING"),
        ):
            baseline = _calibrate_baseline(
                joystick,
                axis_x=1,
                axis_y=0,
                samples=3,
                max_magnitude=0.2,
            )

        self.assertEqual(baseline, (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()

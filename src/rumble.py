"""One-shot pygame rumble capability probe."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def _joystick_name(joystick) -> str:
    try:
        return joystick.get_name()
    except Exception:
        return "unknown joystick"


def test_pygame_rumble(
    joystick,
    low_frequency: float = 0.25,
    high_frequency: float = 0.25,
    duration_ms: int = 120,
) -> bool:
    """Return whether the current pygame joystick accepts a rumble effect."""
    name = _joystick_name(joystick)
    rumble = getattr(joystick, "rumble", None)
    if not callable(rumble):
        logger.warning("Joy-Con does not support pygame rumble: %s (missing rumble method)", name)
        return False

    try:
        supported = bool(rumble(low_frequency, high_frequency, duration_ms))
    except Exception as exc:
        logger.warning("Joy-Con pygame rumble test failed for %s: %s", name, exc)
        return False

    if supported:
        logger.info("Joy-Con supports pygame rumble: %s", name)
    else:
        logger.warning("Joy-Con does not support pygame rumble: %s. Skipping haptics.", name)
    return supported

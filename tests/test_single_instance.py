import uuid
import unittest

from src.single_instance import SingleInstanceLock


class SingleInstanceLockTest(unittest.TestCase):
    def test_second_lock_with_same_name_is_not_acquired(self) -> None:
        name = f"joyharness-test-{uuid.uuid4()}"
        first = SingleInstanceLock(name)
        second = SingleInstanceLock(name)
        try:
            self.assertTrue(first.acquire())
            self.assertFalse(second.acquire())
        finally:
            second.release()
            first.release()

    def test_released_lock_can_be_acquired_again(self) -> None:
        name = f"joyharness-test-{uuid.uuid4()}"
        first = SingleInstanceLock(name)
        second = SingleInstanceLock(name)
        try:
            self.assertTrue(first.acquire())
            first.release()
            self.assertTrue(second.acquire())
        finally:
            second.release()
            first.release()


if __name__ == "__main__":
    unittest.main()

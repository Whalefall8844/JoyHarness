"""Process-wide single-instance guard for JoyHarness."""

from __future__ import annotations

import os
import sys
import tempfile


class SingleInstanceLock:
    """Cross-platform lock that prevents duplicate controller listeners."""

    def __init__(self, name: str = "JoyHarness") -> None:
        self.name = name
        self.acquired = False
        self._handle = None
        self._file = None

    def acquire(self) -> bool:
        if self.acquired:
            return True
        if sys.platform == "win32":
            return self._acquire_windows()
        return self._acquire_file_lock()

    def release(self) -> None:
        if not self.acquired:
            return
        if sys.platform == "win32":
            import ctypes

            if self._handle:
                ctypes.windll.kernel32.CloseHandle(self._handle)
                self._handle = None
        elif self._file is not None:
            import fcntl

            fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
            self._file.close()
            self._file = None
        self.acquired = False

    def _acquire_windows(self) -> bool:
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateMutexW.restype = ctypes.c_void_p
        handle = kernel32.CreateMutexW(None, False, f"Local\\{self.name}")
        if not handle:
            return False
        already_exists = ctypes.get_last_error() == 183
        if already_exists:
            kernel32.CloseHandle(handle)
            return False
        self._handle = handle
        self.acquired = True
        return True

    def _acquire_file_lock(self) -> bool:
        import fcntl

        path = os.path.join(tempfile.gettempdir(), f"{self.name}.lock")
        file_obj = open(path, "w", encoding="utf-8")
        try:
            fcntl.flock(file_obj.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            file_obj.close()
            return False
        self._file = file_obj
        self.acquired = True
        return True

    def __enter__(self) -> "SingleInstanceLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()


def acquire_single_instance(name: str = "JoyHarness") -> SingleInstanceLock:
    lock = SingleInstanceLock(name)
    lock.acquire()
    return lock

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src import autostart
from src.config_loader import merge_with_defaults


class FakeWinreg:
    HKEY_CURRENT_USER = "HKCU"
    KEY_SET_VALUE = 1
    KEY_QUERY_VALUE = 2
    REG_SZ = 1

    def __init__(self) -> None:
        self.values = {}
        self.deleted = []

    def OpenKey(self, root, path, reserved=0, access=0):
        return (root, path, access)

    def SetValueEx(self, key, name, reserved, value_type, value):
        self.values[name] = (value_type, value)

    def DeleteValue(self, key, name):
        self.deleted.append(name)
        if name not in self.values:
            raise FileNotFoundError(name)
        del self.values[name]

    def QueryValueEx(self, key, name):
        if name not in self.values:
            raise FileNotFoundError(name)
        value_type, value = self.values[name]
        return value, value_type


class AutostartTest(unittest.TestCase):
    def test_source_command_uses_start_vbs_minimized(self) -> None:
        command = autostart.build_autostart_command(
            executable=Path(r"C:\Python\python.exe"),
            project_root=Path(r"C:\JoyHarness"),
            frozen=False,
        )

        self.assertEqual(
            command,
            r'wscript.exe //nologo "C:\JoyHarness\start.vbs" --minimized',
        )

    def test_frozen_command_uses_executable_minimized(self) -> None:
        command = autostart.build_autostart_command(
            executable=Path(r"C:\JoyHarness\JoyHarness.exe"),
            project_root=Path(r"C:\JoyHarness"),
            frozen=True,
        )

        self.assertEqual(command, r'"C:\JoyHarness\JoyHarness.exe" --minimized')

    def test_enable_writes_run_key(self) -> None:
        fake = FakeWinreg()

        autostart.set_autostart_enabled(True, command="run-me", registry=fake)

        self.assertEqual(fake.values[autostart.RUN_VALUE_NAME], (fake.REG_SZ, "run-me"))

    def test_disable_deletes_run_key(self) -> None:
        fake = FakeWinreg()
        fake.values[autostart.RUN_VALUE_NAME] = (fake.REG_SZ, "run-me")

        autostart.set_autostart_enabled(False, registry=fake)

        self.assertNotIn(autostart.RUN_VALUE_NAME, fake.values)
        self.assertIn(autostart.RUN_VALUE_NAME, fake.deleted)

    def test_is_autostart_enabled_compares_expected_command(self) -> None:
        fake = FakeWinreg()
        fake.values[autostart.RUN_VALUE_NAME] = (fake.REG_SZ, "run-me")

        self.assertTrue(autostart.is_autostart_enabled("run-me", registry=fake))
        self.assertFalse(autostart.is_autostart_enabled("other", registry=fake))

    def test_main_window_toggle_updates_registry_and_config(self) -> None:
        from src.gui import MainWindow

        window = MainWindow.__new__(MainWindow)
        window._config = {}
        window._autostart_var = Mock()
        window._autostart_var.get.return_value = True

        with (
            patch("src.gui.autostart.set_autostart_enabled") as set_enabled,
            patch("src.gui.save_config") as save_config,
        ):
            MainWindow._on_autostart_toggle(window)

        self.assertTrue(window._config["autostart_enabled"])
        set_enabled.assert_called_once_with(True)
        save_config.assert_called_once_with(window._config)

    def test_config_defaults_autostart_to_disabled(self) -> None:
        config = merge_with_defaults({})

        self.assertFalse(config["autostart_enabled"])


if __name__ == "__main__":
    unittest.main()

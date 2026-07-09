import copy
import io
import unittest
from contextlib import redirect_stdout

from src.constants import DEFAULT_CONFIG_LEFT
from src.main import build_parser, list_controls


class LocalizationTest(unittest.TestCase):
    def test_visible_labels_are_chinese_while_internal_values_stay_english(self) -> None:
        from src.labels import action_label, action_value, button_label, direction_label

        self.assertEqual(button_label("DPadUp"), "方向键上")
        self.assertEqual(button_label("SL"), "SL 侧键")
        self.assertEqual(action_label("window_switch"), "窗口切换")
        self.assertEqual(action_value("窗口切换"), "window_switch")
        self.assertEqual(direction_label("up"), "上")

    def test_list_controls_uses_chinese_visible_text(self) -> None:
        config = copy.deepcopy(DEFAULT_CONFIG_LEFT)
        config["active_profile"] = "single_left"
        config["profiles"] = {"single_left": copy.deepcopy(DEFAULT_CONFIG_LEFT)}

        out = io.StringIO()
        with redirect_stdout(out):
            list_controls(config)

        text = out.getvalue()
        self.assertIn("当前配置", text)
        self.assertIn("按键映射", text)
        self.assertIn("摇杆方向映射", text)
        self.assertIn("方向键上", text)
        self.assertIn("窗口切换", text)
        self.assertNotIn("Button Mappings", text)
        self.assertNotIn("Stick Direction Mappings", text)

    def test_help_text_uses_chinese_headings(self) -> None:
        help_text = build_parser().format_help()

        self.assertIn("用法：", help_text)
        self.assertIn("选项：", help_text)
        self.assertIn("显示帮助信息并退出", help_text)
        self.assertNotIn("usage:", help_text)
        self.assertNotIn("options:", help_text)
        self.assertNotIn("show this help message and exit", help_text)


if __name__ == "__main__":
    unittest.main()

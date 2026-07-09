"""Visible Chinese labels for UI and CLI output.

Internal config values stay English; only display text is localized here.
"""

from __future__ import annotations

BUTTON_LABELS = {
    "A": "A 键",
    "B": "B 键",
    "X": "X 键",
    "Y": "Y 键",
    "DPadUp": "方向键上",
    "DPadDown": "方向键下",
    "DPadLeft": "方向键左",
    "DPadRight": "方向键右",
    "R": "R 键",
    "ZR": "ZR 键",
    "L": "L 键",
    "ZL": "ZL 键",
    "Plus": "＋ 键",
    "Minus": "－ 键",
    "Home": "Home 键",
    "Capture": "截图键",
    "RStick": "右摇杆按下",
    "LStick": "左摇杆按下",
    "SL": "SL 侧键",
    "SR": "SR 侧键",
    "SL_L": "左 SL 侧键",
    "SR_L": "左 SR 侧键",
    "SL_R": "右 SL 侧键",
    "SR_R": "右 SR 侧键",
}

ACTION_LABELS = {
    "tap": "点击",
    "hold": "按住",
    "auto": "自动/连发",
    "combination": "组合键",
    "sequence": "序列键",
    "window_switch": "窗口切换",
    "macro": "宏",
    "exec": "执行命令",
}

ACTION_VALUES = {label: value for value, label in ACTION_LABELS.items()}

DIRECTION_LABELS = {
    "up": "上",
    "down": "下",
    "left": "左",
    "right": "右",
    "up-left": "左上",
    "up-right": "右上",
    "down-left": "左下",
    "down-right": "右下",
}

MODE_LABELS_CN = {
    "single_right": "右手柄",
    "single_left": "左手柄",
    "dual": "左右手柄",
}


def button_label(name: str) -> str:
    return BUTTON_LABELS.get(name, name)


def action_label(action: str) -> str:
    return ACTION_LABELS.get(action, action)


def action_value(label_or_value: str) -> str:
    return ACTION_VALUES.get(label_or_value, label_or_value)


def action_choices(actions: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(action_label(action) for action in actions)


def direction_label(direction: str) -> str:
    return DIRECTION_LABELS.get(direction, direction)


def mode_label(mode: str) -> str:
    return MODE_LABELS_CN.get(mode, mode)

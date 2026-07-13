"""NS Joy-Con Keyboard Mapper — CLI entry point.

Maps Nintendo Switch Joy-Con controller inputs to keyboard shortcuts.
Supports configurable key mappings via JSON config files.
Cross-platform: Windows and macOS.

Usage:
    python -m src                    # Run with default mappings
    python src/main.py               # Also supported
    python -m src --discover         # Calibrate button indices
    python -m src --config my.json   # Use custom config
"""

from __future__ import annotations

import argparse
import faulthandler
import logging
import os
import sys
import threading
from pathlib import Path


def _ensure_windows_font_repository_env() -> None:
    """Ensure Pillow can resolve fonts from the Windows font repository."""
    if sys.platform != "win32":
        return
    os.environ.setdefault("WINDIR", os.environ.get("SystemRoot", r"C:\Windows"))


def _install_crash_diagnostics() -> None:
    """Dump Python thread stacks on fatal crashes."""
    try:
        faulthandler.enable(all_threads=True)
    except (RuntimeError, OSError):
        pass


_install_crash_diagnostics()

# Ensure the project root is on sys.path so that `src` is importable
# as a package when running `python src/main.py` directly.
if __package__ is None:
    _project_root = str(Path(__file__).resolve().parent.parent)
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)
    __package__ = "src"

# Prevent SDL2 from merging Joy-Con L+R into a single combined device.
# Without this, SDL2 exclusively consumes Joy-Con R's HID report stream,
# making it impossible for the battery reader to receive any reports from R.
# With this set, both Joy-Cons remain independent Joystick devices and
# hidapi can concurrently read battery reports from each one.
os.environ.setdefault("SDL_JOYSTICK_HIDAPI_COMBINE_JOY_CONS", "0")
# Normal input mode does not need SDL haptics, and some Joy-Con drivers fail
# while enabling vibration during Joystick construction.
if "--rumble-test" not in sys.argv:
    os.environ.setdefault("SDL_JOYSTICK_HAPTIC_AXES", "0")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
_ensure_windows_font_repository_env()

# macOS: prevent SDL2 from installing its NSApplication subclass.
# SDLApplication doesn't implement -macOSVersion, which Tk 9.0+ calls,
# causing a crash on GUI startup. We don't need video — only joystick —
# so the dummy video driver is safe and avoids the Cocoa hook.
if sys.platform == "darwin":
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from .battery_reader import BatteryReader
from .config_loader import load_config, get_profile, get_platform_config_path, USER_CONFIG_PATH
from .gui import MainWindow
from .joycon_reader import find_joycon, detect_connection_mode, run_discover_mode, run_polling_loop, wait_for_reconnection
from .keep_alive import KeepAliveManager
from .key_mapper import KeyMapper
from .platform.permission import has_required_permissions, get_permission_warning
from .rumble import test_pygame_rumble
from .tray_icon import create_tray_icon, run_tray

logger = logging.getLogger(__name__)


def _append_file_handler(handlers: list[logging.Handler], path: Path) -> None:
    """Append a file log handler, falling back if the target log is locked."""
    try:
        handlers.append(logging.FileHandler(path, encoding="utf-8"))
    except OSError:
        fallback = path.with_name("joyharness-rumble.log")
        try:
            handlers.append(logging.FileHandler(fallback, encoding="utf-8"))
        except OSError:
            pass


class ChineseArgumentParser(argparse.ArgumentParser):
    """ArgumentParser with Chinese built-in help headings."""

    def format_usage(self) -> str:
        return super().format_usage().replace("usage:", "用法：")

    def format_help(self) -> str:
        return (
            super().format_help()
            .replace("usage:", "用法：")
            .replace("options:", "选项：")
        )

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: 错误：{message}\n")


def list_controls(config: dict) -> None:
    """Print all configured button/direction mappings."""
    from .labels import action_label, button_label, direction_label, mode_label

    active_profile = config.get("active_profile", "single_right")
    profile_label = mode_label(active_profile)
    print(f"\n当前配置：{profile_label} ({active_profile})")

    mappings = config.get("mappings", {})

    print("\n=== 按键映射 ===")
    for btn_name, mapping in mappings.get("buttons", {}).items():
        action = mapping["action"]
        if action == "combination":
            target = "+".join(mapping["keys"])
        elif action == "sequence":
            target = "+".join(mapping.get("keys", []))
        elif action == "window_switch":
            target = "切换窗口"
        elif action == "macro":
            target = "宏"
        elif action == "exec":
            target = "命令"
        else:
            target = mapping.get("key", "?")
        print(f"  {button_label(btn_name):10s} [{action_label(action):8s}] → {target}")

    print("\n=== 摇杆方向映射 ===")
    for direction, mapping in mappings.get("stick_directions", {}).items():
        action = mapping["action"]
        if action == "combination":
            target = "+".join(mapping["keys"])
        elif action == "sequence":
            target = "+".join(mapping.get("keys", []))
        else:
            target = mapping.get("key", "?")
        print(f"  {direction_label(direction):10s} [{action_label(action):8s}] → {target}")

    print(f"\n摇杆死区：{config.get('deadzone', 0.15)}")
    print(f"摇杆模式：{config.get('stick_mode', '4dir')}")
    print(f"轮询间隔：{config.get('poll_interval', 0.01) * 1000:.0f}ms")

    profiles = config.get("profiles", {})
    if profiles:
        print("\n可用配置：")
        for mode in profiles:
            label = mode_label(mode)
            marker = "（当前）" if mode == active_profile else ""
            print(f"  {label} ({mode}){marker}")


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = ChineseArgumentParser(
        usage="python -m src [选项]",
        description="JoyHarness — 将 Joy-Con 手柄映射为键盘快捷键",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python -m src --discover            # 校准按钮和轴索引
  python -m src                       # 使用默认配置运行
  python -m src --config custom.json  # 使用自定义配置
  python -m src --deadzone 0.2        # 临时覆盖摇杆死区
  python -m src --list-controls       # 显示当前映射
        """,
        add_help=False,
    )

    parser.add_argument(
        "-h", "--help",
        action="help",
        help="显示帮助信息并退出",
    )

    parser.add_argument(
        "--config", "-c",
        type=str,
        default=None,
        help="JSON 配置文件路径（默认自动选择）",
    )
    parser.add_argument(
        "--discover", "-d",
        action="store_true",
        help="发现模式：显示原始按钮/轴索引用于校准",
    )
    parser.add_argument(
        "--deadzone",
        type=float,
        default=None,
        help="临时覆盖摇杆死区（0.0 到 0.99）",
    )
    parser.add_argument(
        "--joystick", "-j",
        type=int,
        default=None,
        help="指定要使用的手柄设备索引",
    )
    parser.add_argument(
        "--list-controls", "-l",
        action="store_true",
        help="列出当前按键映射后退出",
    )
    parser.add_argument(
        "--rumble-test",
        action="store_true",
        help="检测当前 Joy-Con 是否支持 pygame rumble 震动",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="启用调试日志",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"NSJC {__import__('src.constants', fromlist=['__version__']).__version__}",
        help="显示版本号并退出",
    )
    parser.add_argument(
        "--no-admin-warn",
        action="store_true",
        help="隐藏管理员/权限提示",
    )

    return parser


def _get_pairing_instructions() -> str:
    """Return platform-specific Joy-Con pairing instructions."""
    if sys.platform == "darwin":
        return (
            "\n配对说明（macOS）：\n"
            "  1. 打开系统设置 → 蓝牙\n"
            "  2. 按住 Joy-Con 滑轨上的小配对按钮 3 秒\n"
            "  3. 指示灯快速闪烁后，在蓝牙列表中选择 'Joy-Con (R)' 或 'Joy-Con (L)'\n"
            "  4. 运行 --discover 验证连接"
        )
    else:
        return (
            "\n配对说明：\n"
            "  1. 打开 Windows 设置 → 蓝牙和设备 → 添加设备\n"
            "  2. 按住 Joy-Con 滑轨上的小配对按钮 3 秒\n"
            "  3. 指示灯快速闪烁后，在蓝牙列表中选择 'Joy-Con L' 或 'Joy-Con R'\n"
            "  4. 运行 --discover 验证连接"
        )


def _resolve_initial_joystick(joystick_index: int | None):
    """Find a joystick, waiting for reconnection if none is available yet."""
    js = find_joycon(joystick_index)
    if js is not None:
        return js

    print("未检测到 Joy-Con。")
    print(_get_pairing_instructions())
    print("\n正在等待 Joy-Con 连接。按 Ctrl+C 退出。")
    return wait_for_reconnection(joystick_index)


def _run_rumble_test(joystick_index: int | None) -> bool:
    """Probe whether the current Joy-Con supports pygame rumble."""
    pygame.display.init()
    pygame.joystick.init()
    try:
        js = find_joycon(joystick_index)
        if js is None:
            logger.warning("Rumble test skipped: no Joy-Con detected")
            print("未检测到 Joy-Con，无法测试 pygame rumble。")
            return False

        supported = test_pygame_rumble(js)
        if supported:
            print("Joy-Con 支持 pygame rumble。")
        else:
            print("Joy-Con 不支持 pygame rumble，后续跳过震动功能。")
        return supported
    finally:
        pygame.quit()


def main() -> None:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    handlers: list[logging.Handler] = [
        logging.StreamHandler(),
    ]
    if args.verbose:
        log_path = Path(__file__).resolve().parent.parent / "nsjc.log"
        _append_file_handler(handlers, log_path)
    if args.rumble_test:
        log_path = Path(__file__).resolve().parent.parent / "joyharness.log"
        _append_file_handler(handlers, log_path)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )

    # One-shot rumble capability probe. Keep this independent from config/GUI.
    if args.rumble_test:
        _run_rumble_test(args.joystick)
        return

    # Permission check
    if not args.no_admin_warn and not has_required_permissions():
        print(get_permission_warning())

    # Load config — prefer platform-specific user config if it exists
    config_path = args.config
    if config_path is None:
        config_path = get_platform_config_path()
    try:
        config = load_config(config_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"配置错误：{e}")
        sys.exit(1)

    # Override deadzone if specified
    if args.deadzone is not None:
        if not 0.0 <= args.deadzone < 1.0:
            print(f"无效的摇杆死区：{args.deadzone}（必须在 0.0 到 0.99 之间）")
            sys.exit(1)
        config["deadzone"] = args.deadzone

    # List controls mode
    if args.list_controls:
        list_controls(config)
        return

    # Discover mode
    if args.discover:
        run_discover_mode(args.joystick)
        return

    # Normal mode — selectively init only the pygame subsystems we need.
    # pygame.init() starts ALL subsystems (video, audio, font, mixer, etc.)
    # which on macOS causes SDL2 to install Cocoa event handlers that
    # interfere with tkinter's window management (blocking minimize button).
    # We only need display (for event pump), joystick, and implicitly timer.
    pygame.display.init()
    pygame.joystick.init()

    js = _resolve_initial_joystick(args.joystick)
    if js is None:
        pygame.quit()
        sys.exit(1)

    print(f"控制器：{js.get_name()}")
    print(f"按钮数量：{js.get_numbuttons()}，轴数量：{js.get_numaxes()}")

    # Detect connection mode and load the appropriate profile
    connection_mode = detect_connection_mode()
    profile = get_profile(config, connection_mode)
    profile_mappings = profile.get("mappings", config.get("mappings", {}))
    config["mappings"] = profile_mappings
    config["active_profile"] = connection_mode

    from .labels import mode_label
    profile_label = mode_label(connection_mode)
    print(f"连接模式：{profile_label} ({connection_mode})")
    print(f"摇杆死区：{config['deadzone']}，摇杆模式：{config['stick_mode']}")

    # Restore KNOWN_APPS from saved config
    from .window_switcher import set_known_apps
    known_apps = config.get("known_apps")
    if known_apps:
        set_known_apps(known_apps)

    key_mapper = KeyMapper(config, mode=connection_mode)
    stop_event = threading.Event()

    # Initialize WindowCycler with selected apps from config
    selected_apps = config.get("selected_apps")
    if selected_apps:
        key_mapper._window_cycler.app_names = selected_apps

    # Start battery reader
    battery_reader = BatteryReader(stop_event)
    battery_reader.start()

    # Start keep-alive manager (read enabled state from config)
    keep_alive_manager = KeepAliveManager(stop_event)
    keep_alive_manager.set_enabled(config.get("keep_alive_enabled", True))

    # Create GUI first so we can pass its mode-change callback to polling loop
    gui = MainWindow(
        key_mapper, key_mapper._window_cycler, config, stop_event,
        connection_mode=connection_mode,
        battery_reader=battery_reader,
        keep_alive_manager=keep_alive_manager,
    )
    key_mapper.set_tk_root(gui.root)

    # Start polling loop in background thread (after GUI so callback is available)
    poll_thread = threading.Thread(
        target=_run_polling,
        args=(js, key_mapper, config, stop_event, gui.update_connection_mode),
        daemon=True,
    )
    poll_thread.start()

    # Start tray icon in background thread (Windows only)
    # macOS: pystray requires NSApplication.run on the main thread, which
    # conflicts with tkinter's mainloop. Since macOS has Dock + Cmd+Tab for
    # app switching, the tray icon is not essential. Skipping it avoids a
    # 99% CPU spin caused by NSApplication threading violations.
    icon = None
    tray_thread = None
    if sys.platform != "darwin":
        icon = create_tray_icon(
            stop_event,
            on_show_window=gui.show,
            on_quit=lambda: gui.root.after(0, gui._on_close),
        )
        tray_thread = threading.Thread(target=run_tray, args=(icon,), daemon=True)
        tray_thread.start()

    if sys.platform == "darwin":
        print("界面已启动。关闭窗口即可退出。")
    else:
        print("界面和托盘已启动。关闭窗口或右键托盘退出。")

    # Run GUI in main thread (blocks until window closed)
    gui.run()

    # Cleanup
    stop_event.set()
    if icon is not None:
        icon.stop()
    poll_thread.join(timeout=2.0)
    battery_reader.join(timeout=2.0)
    keep_alive_manager.join(timeout=2.0)
    key_mapper.release_all()
    pygame.joystick.quit()
    pygame.display.quit()
    print("已干净退出，所有按键已释放。")


def _run_polling(
    joystick,
    key_mapper: KeyMapper,
    config: dict,
    stop_event: threading.Event,
    on_mode_change=None,
) -> None:
    """Run polling loop in a background thread, handling exceptions."""
    try:
        run_polling_loop(joystick, key_mapper, config, stop_event, on_mode_change=on_mode_change)
    except Exception:
        logger.exception("Polling thread error")


if __name__ == "__main__":
    main()

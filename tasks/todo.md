# JoyHarness 打包版 vibration 初始化崩溃

- [x] 定位崩溃栈：`find_joycon()` 打开 `pygame.joystick.Joystick(...)` 时 SDL 启用 vibration 失败。
- [x] 增加启动环境变量回归测试，并确认修复前失败。
- [x] 在普通启动路径导入 pygame 前禁用 SDL haptic axes 初始化。
- [x] 跑定向测试、编译检查、依赖检查，并重新打包便携版。

## Review

- 根因：普通启动路径打开 Joy-Con 时，SDL/pygame 在 `Joystick(...)` 构造阶段尝试启用 vibration/haptics，当前驱动返回 `Couldn't enable vibration` 导致打包版直接退出。
- 修复：普通运行在导入 pygame 前设置 `SDL_JOYSTICK_HAPTIC_AXES=0`，保留 Joy-Con HIDAPI 映射；显式 `--rumble-test` 不设置该 hint，仍可作为震动诊断入口。
- 验证：31 个定向单元测试通过，`compileall` 通过，`pip check` 通过；新打包的 exe 启动 4 秒后仍在运行；已重新生成本地便携包。

# JoyHarness L 短按窗口切换排查

- [x] 采集 JoyHarness 日志中 `window_switch` 的目标应用和实际命中窗口。
- [x] 对比 `config/user.json` 中的 `selected_apps` / `known_apps` 与 Windows 当前实际可见进程名。
- [x] 用项目自己的 `find_windows()` 最小复现窗口枚举结果。
- [x] 根据根因做最小修复，优先修配置；只有确认是枚举逻辑缺陷才改代码。
- [x] 验证 L 短按可枚举到多个目标窗口，必要时重启程序。

## Review

- 根因：Windows 端 `_get_process_name()` 返回小写 exe 名，但 `selected_apps` 允许 `Codex.exe` / `WorkBuddy.exe` 这种大小写写法，旧逻辑大小写敏感，导致只有小写配置的 `chrome.exe` 命中。
- 验证：`find_windows(['Doubao.exe','chrome.exe','Codex.exe','WorkBuddy.exe'])` 从 1 个窗口变为 3 个窗口；`WindowCycler.next()` 顺序切换到 Codex、WorkBuddy、Chrome。

# JoyHarness pygame rumble 探测

- [x] 增加 rumble 探测单元测试，覆盖支持、不支持、异常三种结果。
- [x] 增加 `--rumble-test` CLI 参数测试。
- [x] 实现一次性 rumble 探测，不改变正常启动流程。
- [x] 运行定向测试、编译检查、依赖检查。

## Review

- 新增 `--rumble-test`，在配置加载和 GUI 启动之前执行，只检测当前 Joy-Con 的 pygame rumble 支持情况。
- 日志优先写入 `joyharness.log`；如果主程序正在运行导致文件被占用，则回退写入 `joyharness-rumble.log`。
- 真实检测结果：当前 `Nintendo Switch Joy-Con (L)` 支持 pygame rumble。

# JoyHarness 摇杆上误触发排查

- [x] 对比日志中的摇杆基线和实时原始轴采样。
- [x] 增加异常基线单元测试，复现重连后错误校准导致方向误触发。
- [x] 修复 `_calibrate_baseline()`，拒绝超过死区的异常基线。
- [x] 运行定向测试、编译检查，并重启程序验证新基线。

## Review

- 根因：外部 pygame/rumble 探测曾触发 Joy-Con 断连重连，重连后 `_calibrate_baseline()` 立即采样，把异常轴值 `y=0.3419` 当成回中基线；真实回中接近 `0.0~0.19`，相减后会被误判为摇杆上。
- 修复：校准出的基线幅度如果超过当前 deadzone，就视为异常并回退 `(0,0)`，同时写 warning。
- 验证：重启后基线为 `x=-0.0000, y=0.1892`，在 `deadzone=0.2` 内；外部 `--rumble-test` 后主程序未再出现异常重连基线。

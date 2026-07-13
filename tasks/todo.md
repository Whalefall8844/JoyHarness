# JoyHarness 摇杆偶发自主触发排查

- [x] 查看当前日志：启动基线 `x=-0.0000, y=0.0178`，未显示持续漂移。
- [x] 采集 10 秒静置原始轴值：`x` 基本 0，`y` 约 0.0009，无越过 `deadzone=0.2` 的尖峰。
- [x] 定位触发路径：当前代码只对回中做 2 帧防抖，对进入方向没有防抖，一帧越过死区就会触发。
- [x] 增加摇杆方向进入防抖测试：单帧尖峰不触发，连续两帧才触发。
- [x] 实现方向进入防抖，并跑定向测试、编译检查。

## Review

- 结论：当前静置原始轴值稳定，没有持续漂移；“上”和“左”先后出现说明更像偶发单帧轴尖峰或重连瞬间抖动。
- 根因：旧逻辑只对回中做 2 帧防抖，进入方向没有防抖；任意一帧越过死区就会立刻触发摇杆动作。
- 修复：新增摇杆进入方向防抖，默认同一方向连续 2 帧才触发；回中仍保留 2 帧防抖。
- 验证：41 个定向单元测试通过，`compileall` 通过，`pip check` 通过；已重启开发版，Joy-Con L 正常连接。


# JoyHarness 单实例启动防重复任务

- [x] 确认当前 Windows venv 启动会保留一个无窗口 launcher 进程，实际 GUI 在子进程中运行。
- [x] 增加单实例锁测试，覆盖第一次获取成功、第二次获取失败。
- [x] 增加主流程启动守卫测试，覆盖拿不到锁时不加载配置、不初始化手柄。
- [x] 实现跨平台单实例锁，并接入 `main()`。
- [x] 跑定向测试、编译检查、依赖检查，并用真实启动验证第二次启动会退出。

## Review

- 修复：新增 `src/single_instance.py`，Windows 使用本机命名 mutex，非 Windows 使用临时目录文件锁。
- 接入：`main()` 在访问 Joy-Con 前获取锁；拿不到锁时打印“JoyHarness 已在运行，本次启动退出。”并返回。
- 例外：`--list-controls` 不访问手柄，保留无锁读取配置。
- 验证：37 个定向单元测试通过，`compileall` 通过，`pip check` 通过；真实运行时再次执行 `python -m src` 会立即退出，且只保留一个 JoyHarness GUI/controller 实例。


# JoyHarness SL 右 Alt 和左手柄摇杆左右反向

- [x] 确认当前 `config/user.json` 已把左手柄 `SL` 配成 `right alt`。
- [x] 确认 Windows `keyboard` 后端不识别 `alt_r` / `ctrl_r`，但识别 `right alt` / `right ctrl`。
- [x] 增加 Windows 按键别名回归测试，覆盖 `alt_r -> right alt`、`ctrl_r -> right ctrl`。
- [x] 修复 Windows 按键名归一化，避免右侧修饰键写法不一致导致失效。
- [x] 修正左手柄当前摇杆左右映射，并跑定向测试、编译检查。

## Review

- 根因：Windows `keyboard.press("right alt")` 会经由 `key_to_scan_codes("right alt")` 得到多个扫描码，并实际取第一个 `56`，等价于左 Alt；必须直接发送右 Alt 扩展扫描码 `57400`。
- 修复：Windows 后端将 `right alt` / `alt_r` 统一成 `57400`，将 `right ctrl` / `ctrl_r` 统一成 `57373`；当前左手柄 `SL` 保持 `right alt` 配置。
- 摇杆：当前 `single_left` 配置和左手柄默认映射已将物理左/右对调，匹配你的实测方向。
- 验证：34 个定向单元测试通过，`config/user.json` 加载后当前 active profile 值正确，`compileall` 和 `pip check` 通过。


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

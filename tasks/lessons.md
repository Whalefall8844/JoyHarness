# Lessons

- Windows 窗口切换的 exe 名比较必须大小写不敏感；用户配置里出现 `Codex.exe` / `WorkBuddy.exe` 是正常输入，不能要求他们手动改成小写。
- 排查窗口切换问题时，同时采集三类证据：JoyHarness 日志中的目标列表、`config/user.json` 的配置、Windows 当前 `Get-Process` / `find_windows()` 的实际枚举结果。
- 处理 pygame/SDL 硬件初始化崩溃时，优先使用更窄的 SDL hint 保留 Joy-Con HIDAPI 映射；不要为了绕过 vibration 问题直接关闭整个 Joy-Con HIDAPI。
- Windows `keyboard` 库的右侧修饰键不要信字符串名的第一个扫描码；右 Alt 应直接发送扩展扫描码 `57400`，右 Ctrl 应直接发送 `57373`。
- Windows venv `python.exe` 可能只是无窗口 launcher，真实 GUI 在其子进程中；排查重复实例时要看窗口归属和命令行，不能只按 python 进程数量判断。
- 摇杆误触发如果方向不固定且静置采样稳定，优先怀疑单帧尖峰；进入方向也需要和回中一样做帧级防抖，不能一帧越过死区就触发动作。

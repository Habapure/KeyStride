# KeyStride（键步如飞）

**KeyStride** 是一个 Windows 桌面工具，可以自动将剪贴板内容打字到任何输入框中。支持三种打字模式（真实模拟、快速、即时），静默在系统托盘中运行。

## ✨ 主要功能

- **快速粘贴到输入框**：按下热键，自动将剪贴板内容打字到目标输入框
- **三种打字模式**：
  - **真实模拟输入**：模拟真实人类打字，带有自然的打字节奏和随机延迟
  - **快速粘贴**：极快速度输入，最小化延迟
  - **即时输入**：使用 Windows 低层 SendInput API，最快速度
- **暂停/恢复**：打字过程中按 ESC 暂停
- **提示音**：打字开始和完成时可选择提示音
- **智能粘贴**：智能处理标点符号、空格、文本格式
- **持久配置**：所有设置保存到 config.json
- **轻量级**：单一 exe 文件，从系统托盘中运行

## 💻 系统要求

- Windows 10/11（64 位）
- 宽松的 CPU 和内存占用需求

## 📦 安装

### 方式一：从源码构建

\\\powershell
# 安装依赖
pip install PySide6>=6.5.0 pyperclip>=1.8.2 pynput>=1.7.6 pynput pillow>=10.0.0 pywin32>=306 pyinstaller>=6.0

# 构建可执行文件
python build.py

# 生成的 exe 在 dist/ 目录下
\\\

### 方式二：下载预构建 EXE

从 Releases 下载 \KeyStride.exe\（或项目根目录下已有）。

## 🚀 使用方法

### 基本工作流

1. 在设置中选择打字模式：
   - **真实模拟输入**（Human 模式）：模拟真实打字，带有自然延迟和随机性
   - **快速粘贴**（Fast 模式）：快速输入，最小化延迟
   - **即时输入**（Instant 模式）：使用低层 SendInput API，极快速度

2. 设置触发热键（默认：Ctrl+Shift+V）
   - 在应用中选择 → 触发延迟 → 修改热键

3. 可选：启用提示音

4. 将需要的内容复制到剪贴板

5. 按下热键开始打字 — 内容自动出现在目标输入框中

6. 按 ESC 暂停正在进行的打字

### 打字模式说明

| 模式 | 适用场景 | 打字速度 | 特点 |
|------|----------|----------|------|
| **真实模拟** | 写消息、评论或任何需要自然节奏的内容 | 中等（略快于人类） | 随机延迟；智能标点间距；随机微暂停真实感 |
| **快速粘贴** | 批量粘贴代码片段、日志数据或重复文本 | 快（每个字符 8-20ms） | 字符间延迟最小化 |
| **即时输入** | 极速场景（大块代码、JSON、文本数据） | 极快 | 使用 Windows SendInput；每批 500 字符 |

### 默认热键

- **触发热键**：Ctrl+Shift+V（可配置）
- **暂停打字**：ESC

### 自定义打字行为

你可以在应用中修改以下设置：

- **触发热键**：自定义组合键
- **触发延迟**：
  - 立即（0 秒）
  - 打字开始前延迟 1.5 秒
  - 打字开始前延迟 3 秒
- **提示音**：开关提示音
- **启用/禁用**：切换自动打字功能

> ⚠️ 注意：此工具粘贴的是剪贴板内容 — 触发前请确认剪贴板中有你想要的文本，并根据场景选择合适的模式。

### 剪贴板不粘贴到目标输入框的考虑

- 确保目标输入框已聚焦且激活（点击它或切换到该窗口）
- 检查目标输入框是否支持粘贴（某些带粘贴限制的网页输入可能不可用）
- 确认剪贴板内容是有效的文本（不是图片或格式化内容）

## ⚙️ 配置文件

设置保存到与 KeyStride.exe 同目录的 \config.json\：

\\\json
{
  "mode": "human",
  "enabled": true,
  "delay_seconds": 1.5,
  "hotkey": "ctrl+shift+v",
  "sound_enabled": false
}
\\\

字段说明：
- \mode\：打字模式（"human"、"fast" 或 "instant"）
- \enabled\：按下热键是否开始打字（true/false）
- \delay_seconds\：开始打字前的延迟（0.0、1.5 或 3.0）
- \hotkey\：热键组合（如 "ctrl+shift=v"）
- \sound_enabled\：启用提示音（true/false）

## 🔐 隐私与安全

KeyStride 是一个本地应用：
- 仅打字当前系统剪贴板中的内容
- 完全在你的电脑上运行 — 无网络连接或云端处理
- 无法收集或上传数据
- 它粘贴的是剪贴板中的内容，触发前请检查

## 💻 开发指南

### 项目结构

\\\
KeyStride/
├── core/              # 核心功能
│   ├── engine.py      # 打字引擎协调器
│   ├── keyboard.py    # 低层键盘输入处理
│   └── clipboard.py   # 剪贴板操作
├── modes/             # 打字模式
│   ├── base.py        # 模式基类
│   ├── human.py       # 真实模拟模式
│   ├── fast.py        # 快速打字模式
│   └── instant.py     # 即时打字模式
├── ui/                # PyQt6 界面
│   └── main_window.py # 主应用程序窗口
├── main.py            # 程序入口
├── tray.py            # 系统托盘图标
├── hotkey.py          # 热键监听
├── config.py          # 配置管理
└── build.py           # PyInstaller 构建脚本
\\\

### 本地开发

\\\powershell
# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py

# 运行测试
python -m pytest tests/
\\\

## 🐛 常见问题

### 热键不起作用

- 杀毒软件可能阻止了全局热键注册。尝试将 KeyStride.exe 添加到杀毒软件白名单。
- 另一个应用可能已注册相同的组合键。在设置中修改热键。
- 重装应用，并在重装 Python 和依赖项之后重试。

### 文本不粘贴到目标输入框

- 确保目标输入框已聚焦且激活（点击它或切换到该窗口）。
- 检查目标输入框是否支持粘贴（某些带粘贴限制的网页输入可能不可用）。
- 确认剪贴板内容是有效的文本（不是图片或格式化内容）。

### 应用意外关闭

- 在 KeyStride.exe 同目录下查看 \error.log\ 文件了解详细错误信息。
- 重装应用。
- 临时禁用杀毒软件测试是否干扰。

## 🤝 贡献

欢迎提交 Issue、Request Features 和 Pull Request。在 GitHub 上打开 PR 即可。

## 📄 许可证

[你的许可证] — 欢迎用于个人或商业用途。

---

**快乐打字！** 🚀

# KeyStride

**KeyStride** is a Windows desktop tool that automatically types clipboard contents into any input field. It supports three typing modes (human simulation, fast, instant) and runs quietly in the system tray.

## ✨ Features

- **Fast clipboard-to-input**: Press a hotkey to instantly paste clipboard text into your target input field
- **Three typing modes**:
  - **Human simulation**: Mimics realistic human typing with natural rhythm and random delays
  - **Fast paste**: Minimal delay between characters
  - **Instant input**: Uses Windows low-level SendInput API for maximum speed
- **Pause/Resume**: Press ESC to pause typing in progress
- **Sound notifications**: Optional beep when typing starts/completes
- **Smart paste**: Intelligent punctuation handling, spacing, and text formatting
- **Persistent configuration**: All settings saved to config.json
- **Lightweight**: Single exe file, runs from system tray

## 💻 System Requirements

- Windows 10/11 (64-bit)
- Minimal CPU and memory usage when idle

## 📦 Installation

### Option 1: Build from Source

\\\powershell
# Install dependencies
pip install PySide6>=6.5.0 pyperclip>=1.8.2 pynput>=1.7.6 pynput pillow>=10.0.0 pywin32>=306 pyinstaller>=6.0

# Build the executable
python build.py

# The built exe will be in the dist/ directory
\\\

### Option 2: Download Pre-built EXE

Download \KeyStride.exe\ from the releases section (or use the exe in project root).

## 🚀 Usage

### Basic Workflow

1. Select your preferred typing mode in the settings:
   - **Human simulation** (Human mode): Mimics realistic typing with natural delay and randomness
   - **Fast paste** (Fast mode): Very fast typing with minimal delays
   - **Instant input** (Instant mode): Uses low-level SendInput API, blazing fast

2. Set trigger hotkey (default: Ctrl+Shift+V)
   - Settings → Trigger Delay → Change Hotkey

3. Optionally enable sound notifications

4. Copy desired text to clipboard

5. Press the hotkey to start typing - text will automatically appear in your target input field

6. Press ESC to pause typing in progress

### Typing Modes Explained

| Mode | Use Case | Typing Speed | Key Characteristics |
|------|----------|--------------|---------------------|
| **Human** | Writing messages, comments, or any content that benefits from natural rhythm | Moderate (slightly faster than actual human) | Randomized delays; intelligent punctuation spacing; random micro-pauses for realism |
| **Fast** | Bulk paste code snippets, log data, or repetitive text quickly | Fast (8-20ms per char) | Minimal delay between characters |
| **Instant** | Maximum speed scenarios (large code blocks, JSON, textual data) | Very Fast | Uses low-level Windows SendInput; batches 500 chars per API call |

### Default Hotkeys

- **Trigger hotkey**: Ctrl+Shift+V (configurable)
- **Pause typing**: ESC

### Customizing Typing Behavior

You can modify the following settings in the application:

- **Trigger hotkey**: Customize the key combination
- **Trigger delay**: 
  - Immediate (0s)
  - Delay before typing starts (1.5s or 3s)
- **Sound**: Toggle beep notifications
- **Enable/Disable**: Toggle the automatic typing feature

> ⚠️ Important: This tool pastes clipboard contents - check what's currently in your clipboard before triggering
- Ensure the target input field is focused and active (click on it or switch to the window)
- Check if the target input field supports paste (some web inputs with paste restrictions may not work)
- Ensure the clipboard contains valid text (not images or formatted content)

## ⚙️ Configuration

Settings are saved to \config.json\ in the same directory as KeyStride.exe:

\\\json
{
  "mode": "human",
  "enabled": true,
  "delay_seconds": 1.5,
  "hotkey": "ctrl+shift+v",
  "sound_enabled": false
}
\\\

Field meanings:
- \mode\: Typing mode ("human", "fast", or "instant")
- \enabled\: Whether to start typing when hotkey is pressed (true/false)
- \delay_seconds\: Delay before starting to type (0.0, 1.5, or 3.0)
- \hotkey\**: Hotkey combination (e.g., "ctrl+shift=v")
- \sound_enabled\: Enable sound notifications (true/false)

## 🔐 Privacy & Security

KeyStride is a local application that:
- Only types text currently in your system clipboard
- Runs entirely on your machine - no network connections or cloud processing
- No telemetry or data collection
- It pastes exactly what is in your clipboard, so check content before triggering

## 💻 Development

### Project Structure

\\\
KeyStride/
├── core/              # Core functionality
│   ├── engine.py      # Typing engine orchestrator
│   ├── keyboard.py    # Low-level keyboard input handling
│   └── clipboard.py   # Clipboard operations
├── modes/             # Typing modes
│   ├── base.py        # Base mode implementation
│   ├── human.py       # Human simulation mode
│   ├── fast.py        # Fast typing mode
│   └── instant.py     # Instant typing mode
├── ui/                # PyQt6 GUI
│   └── main_window.py # Main application window
├── main.py            # Application entry point
├── tray.py            # System tray icon
├── hotkey.py          # Hotkey listener
├── config.py          # Configuration management
└── build.py           # Build script for PyInstaller
\\\

### Local Development

\\\powershell
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py

# Run tests
python -m pytest tests/
\\\

## 🐛 Troubleshooting

### Hotkey not working

- Antivirus software may block global hotkey registration. Try adding KeyStride.exe to antivirus exceptions.
- Another application may have already registered the same combination. Change the hotkey in the settings.
- Reinstall the application after reinstalling Python and its dependencies.

### Text not pasting into target input field

- Make sure the target input field is focused and active (click on it or switch to the window).
- Check if the target input field supports paste (some web inputs with paste restrictions may not work).
- Ensure the clipboard contains valid text (not images or formatted content).

### Application closes unexpectedly

- Check the \error.log\ file in the same directory as KeyStride.exe for detailed error messages.
- Reinstall the application.
- Disable any antivirus software temporarily to test if it's interfering.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open a pull request or submit an issue on GitHub.

## 📄 License

[Your License Here] - Feel free to use and modify this project for personal or commercial use.

---

**Happy typing!** 🚀
# KeyStride / 键步如飞
> **切换语言：** [English](#keystride) | [中文](#键步如飞)

---

<a name="keystride"></a>
## English
Paste clipboard text into any input field with three typing modes, quiet tray operation, and one default hotkey.

### Install
```powershell
pip install -r requirements.txt
python main.py
```

### Build
```powershell
python build.py
```

### Config
```json
{
  "mode": "human",
  "enabled": true,
  "delay_seconds": 1.5,
  "hotkey": "ctrl+shift+v",
  "sound_enabled": false
}
```

### Modes
- Human
- Fast
- Instant

### Notes
- Run on Windows.
- Keep the target field focused.
- Press `ESC` to abort.

---

<a name="键步如飞"></a>
## 中文 / 键步如飞
将剪贴板内容输入到任意输入框，提供三种输入模式、托盘后台运行和默认热键。

### 安装
```powershell
pip install -r requirements.txt
python main.py
```

### 构建
```powershell
python build.py
```

### 配置
```json
{
  "mode": "human",
  "enabled": true,
  "delay_seconds": 1.5,
  "hotkey": "ctrl+shift+v",
  "sound_enabled": false
}
```

### 输入模式
- 仿真输入
- 快速输入
- 瞬间输入

### 注意事项
- 仅支持 Windows。
- 目标输入框需保持聚焦。
- 按 `ESC` 可中断输入。

# KeyStride / 键步如飞

> **切换语言：** [English](#keystride) | [中文](#键步如飞)

---

<a name="keystride"></a>
## English
## 简介

KeyStride (键步如飞) 是一款 Windows 桌面工具，能够把剪贴板内容自动粘贴到任何输入框。支持三种输入模式（仿真、快速、瞬间），支持托盘后台运行，默认热键为 `Ctrl+Shift+V`。

### 安装
```powershell
# 克隆仓库
git clone https://github.com/Habapure/KeyStride.git
cd KeyStride
# 安装依赖
pip install -r requirements.txt
```

### 运行
```
python main.py
```

### 打包
```powershell
python build.py
# 打包后会在 dist/ 目录下生成 KeyStride_v1.<##>.exe
```

### 配置
```json
{
  "mode": "human", // 类型：human / fast / instant
  "enabled": true,
  "delay_seconds": 1.5,
  "hotkey": "ctrl+shift+v",
  "sound_enabled": false
}
```

### 模式
- **Human**：仿真输入，随机停顿，随着文本写作节奏自然打字。
- **Fast**：短时间间隔，每字符 8-20ms，速度非常快。
- **Instant**：批量 SendInput，最快速度，适合粘贴代码等内容。

### 使用
1. 按 `Ctrl+Shift+V` 触发。
2. 如果想改变模式或热键，打开主窗口菜单或托盘菜单进行设置。
3. 打字过程中按 `Esc` 或相同组合键取消。

---

<a name="键步如飞"></a>
## 中文 / 键步如飞
键步如飞（KeyStride）是一款 Windows 桌面工具，能够将剪贴板内容自动粘贴到任意输入框。提供三种输入模式（仿真、快速、瞬间），支持托盘后台运行，默认热键为 `Ctrl+Shift+V`。

### 安装
```powershell
# 克隆仓库
git clone https://github.com/Habapure/KeyStride.git
cd KeyStride
# 安装依赖
pip install -r requirements.txt
```

### 运行
```
python main.py
```

### 打包
```powershell
python build.py
# 打包后会在 dist/ 目录下生成 KeyStride_v1.<##>.exe
```

### 配置
```json
{
  "mode": "human", // 类型：human / fast / instant
  "enabled": true,
  "delay_seconds": 1.5,
  "hotkey": "ctrl+shift+v",
  "sound_enabled": false
}
```

### 模式
- **仿真**：模拟真实人类打字，随机停顿。
- **快速**：短时间间隔，每字符 8-20ms，速度非常快。
- **瞬间**：批量 SendInput，最快速度，适合粘贴代码等内容。

### 使用
1. 按 `Ctrl+Shift+V` 触发。
2. 若需改变模式或热键，打开主窗口菜单或托盘菜单进行设置。
3. 打字过程中按 `Esc` 或相同组合键取消。

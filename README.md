# KeyStride (键步如飞)

KeyStride is a Windows desktop application that automatically types clipboard contents into any input field. It supports three typing modes (human simulation, fast, instant) and runs quietly in the system tray.

## Features

- **Fast clipboard-to-input**: Press a hotkey to instantly paste clipboard text
- **Three typing modes**:
  - *Real-time input*: Mimics human typing with realistic timing and randomness
  - *Fast paste*: Rapid typing with minimal delay
  - *Instant input*: Blazing fast typing using low-level SendInput API
- **Pause/Resume support**: Press ESC to pause typing in progress
- **Sound notifications**: Optional beep when typing starts/completes
- **Smart paste**: Intelligent punctuation handling, spacing, and text adjustments
- **Persistent configuration**: All settings saved to config.json
- **Lightweight**: Single exe file, runs from system tray

## System Requirements

- Windows 10/11 (64-bit)
- Minimal CPU and memory usage when idle

## Installation

### Option 1: Build from Source

```powershell
# Install required dependencies
pip install PySide6>=6.5.0 pyperclip>=1.8.2 pynput>=1.7.6 pynput pillow>=10.0.0 pywin32>=306 pyinstaller>=6.0

# Build the executable
python build.py

# The built exe will be in the dist/ directory
```

### Option 2: Download Pre-built EXE

Download `KeyStride.exe` from the releases section (or use the exe in project root).

## Usage

### Basic Workflow

1. Select your preferred typing mode in the settings:
   - **Real-time input** (Human mode): Mimics realistic human typing with natural timing variations
   - **Fast paste** (Fast mode): Rapid typing with minimal delays
   - **Instant input** (Instant mode): Blazing fast typing using low-level SendInput API

2. Set trigger hotkey (default: Ctrl+Shift+V):
   - Press Select Mode → Trigger Delay → Change Hotkey

3. Optionally enable sound notifications

4. Copy desired text to clipboard

5. Press the hotkey to start typing - text will automatically appear in your target input field

6. Press ESC to pause typing in progress

### Typing Modes Explained

| Mode | Use Case | Typing Speed | Key Characteristics |
|------|----------|--------------|---------------------|
| **Human** | Writing messages, comments, or any content that benefits from natural timing | Moderate (slightly faster than actual human) | Randomized delays; intelligent punctuation spacing; random micro-pauses for realism |
| **Fast** | Past bulk code snippets, log data, or repetitive text quickly | Fast (8-20ms per char) | Minimal delay between characters |
| **Instant** | Maximum speed scenarios (large code blocks, JSON, text data) | Very Fast | Uses low-level Windows SendInput; batches 500 chars per API call |

### Default Hotkeys

- **Trigger hotkey**: Ctrl+Shift+V (configurable)
- **Pause typing**: ESC

### Customizing Typing Behavior

You can modify the following settings in the application:

- **Trigger hotkey**: Customize the key combination
- **Trigger delay**: 
  - Immediate (0s)
  - 1.5 seconds delay before typing starts
  - 3 seconds delay before typing starts
- **Sound**: Toggle beep notifications
- **Enable/Disable**: Toggle the automatic typing feature

Notes:
- This tool pastes clipboard contents - check what is currently in your clipboard before triggering
- Select an appropriate mode based on your use case
- Works best when the target input field is focused and active

## Configuration

Settings are saved to `config.json` in the same directory as KeyStride.exe:

```json
{
  "mode": "human",
  "enabled": true,
  "delay_seconds": 1.5,
  "hotkey": "ctrl+shift+v",
  "sound_enabled": false
}
```

Field meanings:
- `mode`: Typing mode ("human", "fast", or "instant")
- `enabled`: Whether to start typing when hotkey is pressed (true/false)
- `delay_seconds`: Delay before starting to type (0.0, 1.5, or 3.0)
- `hotkey`**: Hotkey combination (e.g., "ctrl+shift+v")
- `sound_enabled`: Enable sound notifications (true/false)

## Privacy & Security

KeyStride is a local application that:
- Only types text currently in your system clipboard
- Runs entirely on your machine - no network connections or cloud processing
- No telemetry or data collection
- It pastes exactly what is in your clipboard, so check content before triggering

## Development

### Project Structure

```
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
```

### Local Development

```powershell
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py

# Run tests
python -m pytest tests/
```

## Troubleshooting

### Hotkey not working

- Antivirus software may block global hotkey registration. Try adding KeyStride.exe to antivirus exceptions.
- Another application may have already registered the same combination. Change the hotkey in the settings.
- Reinstall the application after reinstalling Python and its dependencies.

### Text not pasting into target field

- Make sure the target input field is focused and active (click on it or switch to the window).
- Check if the target field supports paste operations (some web inputs with paste restrictions may not work).
- Ensure the clipboard contains valid text (not images or formatted content).

### Application closes unexpectedly

- Check the `error.log` file in the same directory as KeyStride.exe for detailed error messages.
- Reinstall the application.
- Disable any antivirus software temporarily to test if it's interfering.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to open a pull request or submit an issue on GitHub.

## License

[Your License Here] - Feel free to use and modify this project for personal or commercial use.

---

**Happy typing!** 🚀

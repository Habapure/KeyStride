"""剪贴板读取。"""

from __future__ import annotations

import pyperclip


def get_clipboard_text() -> str:
    """读取剪贴板文本；失败或非文本时返回空字符串。"""
    try:
        text = pyperclip.paste()
    except Exception:
        return ""
    if text is None:
        return ""
    return str(text)

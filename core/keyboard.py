"""Win32 SendInput 键盘事件封装。"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

VK_RETURN = 0x0D
VK_TAB = 0x09

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class KEYBDINPUT(ctypes.Structure):
    _fields_ = (
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    )


class MOUSEINPUT(ctypes.Structure):
    _fields_ = (
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    )


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    )


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT))

    _anonymous_ = ("_input",)
    _fields_ = (("type", wintypes.DWORD), ("_input", _INPUT))


LPINPUT = ctypes.POINTER(INPUT)

user32.SendInput.argtypes = (wintypes.UINT, LPINPUT, ctypes.c_int)
user32.SendInput.restype = wintypes.UINT


def _vk_event(vk: int, *, key_up: bool = False) -> INPUT:
    flags = KEYEVENTF_KEYUP if key_up else 0
    return INPUT(
        type=INPUT_KEYBOARD,
        ki=KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0),
    )


def _unicode_event(code: int, *, key_up: bool = False) -> INPUT:
    flags = KEYEVENTF_UNICODE | (KEYEVENTF_KEYUP if key_up else 0)
    return INPUT(
        type=INPUT_KEYBOARD,
        ki=KEYBDINPUT(wVk=0, wScan=code, dwFlags=flags, time=0, dwExtraInfo=0),
    )


def char_to_events(char: str) -> list[INPUT]:
    """将单个字符转为按下+释放事件列表。"""
    if char in ("\n", "\r"):
        return [_vk_event(VK_RETURN), _vk_event(VK_RETURN, key_up=True)]
    if char == "\t":
        return [_vk_event(VK_TAB), _vk_event(VK_TAB, key_up=True)]

    code = ord(char)
    # 代理对：码点超出 BMP
    if code > 0xFFFF:
        code -= 0x10000
        high = 0xD800 + (code >> 10)
        low = 0xDC00 + (code & 0x3FF)
        return [
            _unicode_event(high),
            _unicode_event(high, key_up=True),
            _unicode_event(low),
            _unicode_event(low, key_up=True),
        ]

    return [_unicode_event(code), _unicode_event(code, key_up=True)]


def send_inputs(inputs: list[INPUT]) -> int:
    """Send one INPUT batch or raise when Windows accepts only part of it."""
    if not inputs:
        return 0
    arr = (INPUT * len(inputs))(*inputs)
    sent = user32.SendInput(len(inputs), arr, ctypes.sizeof(INPUT))
    if sent != len(inputs):
        error = ctypes.get_last_error()
        if error:
            raise ctypes.WinError(error)
        raise OSError(f"SendInput sent {sent} of {len(inputs)} keyboard events")
    return int(sent)


def send_char(char: str) -> int:
    """发送单个字符。"""
    return send_inputs(char_to_events(char))


def normalize_text(text: str) -> str:
    """统一换行：\\r\\n / \\r → \\n，后续按 Enter 处理。"""
    return text.replace("\r\n", "\n").replace("\r", "\n")

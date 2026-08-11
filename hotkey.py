"""全局热键监听：Ctrl+Shift+V 触发，ESC / 同热键中断。"""

from __future__ import annotations

import threading
from collections.abc import Callable

from pynput import keyboard

from config import MODIFIER_NAMES, normalize_hotkey
from logger import log_exception


class HotkeyListener:
    def __init__(
        self,
        on_trigger: Callable[[], None],
        on_cancel: Callable[[], None],
        hotkey: str = "ctrl+shift+v",
    ) -> None:
        """初始化热键监听器。
        hotkey: 例如 "ctrl+shift+v"，支持 ctrl、shift、alt、win 和单字符键。
        """
        self._on_trigger = on_trigger
        self._on_cancel = on_cancel
        self._listener: keyboard.Listener | None = None
        self._pressed: set = set()
        self._trigger_latched = False
        self._lock = threading.Lock()
        # 解析热键字符串为标准化集合，如 {"ctrl", "shift", "v"}
        self._hotkey_set = frozenset(normalize_hotkey(hotkey).split("+"))

    def start(self) -> bool:
        """Start the global listener and report whether startup succeeded."""
        if self._listener is not None:
            return True
        try:
            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
            )
            self._listener.daemon = True
            self._listener.start()
            return True
        except Exception as e:
            log_exception(f"Hotkey registration failed: {e}")
            self._listener = None
            return False

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def _norm(self, key) -> object:
        if isinstance(key, keyboard.KeyCode):
            # With Ctrl held, pynput may expose a control character instead of the key.
            if key.vk is not None and 0x30 <= key.vk <= 0x5A:
                return chr(key.vk).lower()
            if key.char:
                return key.char.lower()
            return key
        return key

    def _is_modifier(self, mod_name: str) -> bool:
        """检查指定的修饰键是否被按下。"""
        mapping = {
            "ctrl": [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r],
            "shift": [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r],
            "alt": [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r],
            "win": [keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r],
        }
        keys = mapping.get(mod_name.lower())
        if not keys:
            return False
        return any(k in self._pressed for k in keys)

    def _combo_active(self) -> bool:
        """判断是否满足配置的热键组合。"""
        # 必须的修饰键集合
        required_mods = self._hotkey_set & MODIFIER_NAMES
        # 必须的主键（单字符）
        required_key = next((p for p in self._hotkey_set if p not in MODIFIER_NAMES), None)
        if required_key is None:
            return False
        # 检查所有修饰键是否被按下
        if not all(self._is_modifier(mod) for mod in required_mods):
            return False
        # 检查主键是否在 pressed 集合中（已归一化为小写字符）
        return required_key in self._pressed


    def _on_press(self, key) -> None:
        nk = self._norm(key)
        self._pressed.add(nk)

        if key == keyboard.Key.esc:
            self._on_cancel()
            return

        if self._combo_active():
            with self._lock:
                if self._trigger_latched:
                    return
                self._trigger_latched = True
            self._on_trigger()

    def _on_release(self, key) -> None:
        nk = self._norm(key)
        self._pressed.discard(nk)
        if self._is_hotkey_part(nk):
            with self._lock:
                if not self._combo_active():
                    self._trigger_latched = False

    def _is_hotkey_part(self, key: object) -> bool:
        if key in self._hotkey_set:
            return True
        modifier_keys = {
            "ctrl": (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r),
            "shift": (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r),
            "alt": (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r),
            "win": (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r),
        }
        return any(
            modifier in self._hotkey_set and key in keys
            for modifier, keys in modifier_keys.items()
        )

"""全局热键监听：Ctrl+Shift+V 触发，ESC / 同热键中断。"""

from __future__ import annotations

import threading
from collections.abc import Callable

from pynput import keyboard


class HotkeyListener:
    def __init__(
        self,
        on_trigger: Callable[[], None],
        on_cancel: Callable[[], None],
    ) -> None:
        self._on_trigger = on_trigger
        self._on_cancel = on_cancel
        self._listener: keyboard.Listener | None = None
        self._pressed: set = set()
        self._trigger_latched = False
        self._lock = threading.Lock()

    def start(self) -> None:
        if self._listener is not None:
            return
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def _norm(self, key) -> object:
        if isinstance(key, keyboard.KeyCode):
            # Ctrl+V 时 char 常为 None 或 '\x16'
            if key.vk is not None and key.vk in (0x56, ord("v"), ord("V")):
                return "v"
            if key.char:
                ch = key.char.lower()
                if ch == "v" or ch == "\x16":
                    return "v"
                return ch
            return key
        return key

    def _is_ctrl(self) -> bool:
        return (
            keyboard.Key.ctrl_l in self._pressed
            or keyboard.Key.ctrl_r in self._pressed
            or keyboard.Key.ctrl in self._pressed
        )

    def _is_shift(self) -> bool:
        return (
            keyboard.Key.shift_l in self._pressed
            or keyboard.Key.shift_r in self._pressed
            or keyboard.Key.shift in self._pressed
        )

    def _combo_active(self) -> bool:
        return self._is_ctrl() and self._is_shift() and "v" in self._pressed

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
        # 任一修饰键或 V 松开后允许再次触发
        if nk in (
            "v",
            keyboard.Key.ctrl,
            keyboard.Key.ctrl_l,
            keyboard.Key.ctrl_r,
            keyboard.Key.shift,
            keyboard.Key.shift_l,
            keyboard.Key.shift_r,
        ):
            with self._lock:
                if not self._combo_active():
                    self._trigger_latched = False

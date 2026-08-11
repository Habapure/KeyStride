"""快速输入：短固定延时。"""

from __future__ import annotations

import random
import threading
import time

from core.keyboard import send_char

from .base import TypeResult, TypingMode


class FastMode(TypingMode):
    name = "fast"
    label = "快速输入"

    def type_text(
        self,
        text: str,
        stop_event: threading.Event,
        start: int = 0,
    ) -> TypeResult:
        i = start
        n = len(text)
        while i < n:
            if stop_event.is_set():
                return TypeResult(False, i)
            char = text[i]
            if char == "\r":
                i += 1
                continue
            send_char(char)
            i += 1
            delay_ms = random.randint(8, 20)
            end = time.monotonic() + delay_ms / 1000.0
            while time.monotonic() < end:
                if stop_event.is_set():
                    return TypeResult(False, i)
                time.sleep(min(0.01, max(0.0, end - time.monotonic())))
        return TypeResult(True, n)

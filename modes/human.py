"""仿真输入：随机延时 + 自然节奏。"""

from __future__ import annotations

import random
import threading
import time

from core.keyboard import send_char

from .base import TypeResult, TypingMode

PUNCTUATION = set("，。！？；：、.…—～,.!?;:")


def get_delay(char: str, prev_char: str) -> int:
    if char in PUNCTUATION:
        return random.randint(150, 350)
    if char in " \t\n":
        return random.randint(60, 150)
    if prev_char in PUNCTUATION:
        return random.randint(100, 250)
    if random.random() < 0.03:
        return random.randint(300, 600)
    return random.randint(40, 180)


class HumanMode(TypingMode):
    name = "human"
    label = "仿真输入"

    def type_text(
        self,
        text: str,
        stop_event: threading.Event,
        start: int = 0,
    ) -> TypeResult:
        prev = text[start - 1] if start > 0 else ""
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
            delay_ms = get_delay(char, prev)
            end = time.monotonic() + delay_ms / 1000.0
            while time.monotonic() < end:
                if stop_event.is_set():
                    return TypeResult(False, i)
                time.sleep(min(0.02, max(0.0, end - time.monotonic())))
            prev = char
        return TypeResult(True, n)

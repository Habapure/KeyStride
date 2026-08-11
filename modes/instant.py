"""瞬间输入：批量 SendInput。"""

from __future__ import annotations

import threading

from core.keyboard import char_to_events, send_inputs

from .base import TypeResult, TypingMode

CHUNK_CHARS = 500


class InstantMode(TypingMode):
    name = "instant"
    label = "瞬间输入"

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
            end = min(i + CHUNK_CHARS, n)
            chunk = text[i:end]
            events = []
            for ch in chunk:
                if ch == "\r":
                    continue
                events.extend(char_to_events(ch))
            if events:
                send_inputs(events)
            i = end
        return TypeResult(True, n)

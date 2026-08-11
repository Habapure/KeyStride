"""打字引擎：按模式逐字/批量发送，支持中断与断点续打。"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import TYPE_CHECKING

from .keyboard import normalize_text

if TYPE_CHECKING:
    from modes.base import TypingMode


class TypingEngine:
    def __init__(self) -> None:
        self._stop = threading.Event()
        self._busy = threading.Event()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        # 断点续打状态（同一段文本）
        self._resume_text: str = ""
        self._resume_index: int = 0

    @property
    def is_busy(self) -> bool:
        return self._busy.is_set()

    @property
    def resume_index(self) -> int:
        return self._resume_index

    @property
    def has_resume(self) -> bool:
        return bool(self._resume_text) and 0 < self._resume_index < len(self._resume_text)

    def clear_resume(self) -> None:
        self._resume_text = ""
        self._resume_index = 0

    def stop(self) -> None:
        """请求中断当前打字。"""
        self._stop.set()

    def type_async(
        self,
        text: str,
        mode: TypingMode,
        *,
        delay_seconds: float = 0.0,
        on_start: Callable[[int, int], None] | None = None,
        on_done: Callable[[bool, bool], None] | None = None,
    ) -> bool:
        """
        在后台线程打字。
        若剪贴板文本与上次中断时相同，则从断点续打。
        on_start(start_index, total)
        on_done(completed, was_resume)
        """
        with self._lock:
            if self._busy.is_set():
                return False
            self._stop.clear()
            self._busy.set()
            self._thread = threading.Thread(
                target=self._run,
                args=(text, mode, delay_seconds, on_start, on_done),
                daemon=True,
                name="KeyStrideTyping",
            )
            self._thread.start()
            return True

    def _run(
        self,
        text: str,
        mode: TypingMode,
        delay_seconds: float,
        on_start: Callable[[int, int], None] | None,
        on_done: Callable[[bool, bool], None] | None,
    ) -> None:
        completed = False
        was_resume = False
        try:
            text = normalize_text(text)
            if not text:
                self.clear_resume()
                return

            # 同一段文本 → 续打；换了内容 → 从头
            if text == self._resume_text and 0 < self._resume_index < len(text):
                start = self._resume_index
                was_resume = True
            else:
                start = 0
                self._resume_text = text
                self._resume_index = 0

            if delay_seconds > 0:
                deadline = time.monotonic() + delay_seconds
                while time.monotonic() < deadline:
                    if self._stop.is_set():
                        # 倒计时阶段中断：保留原断点（若是续打）或仍为 0
                        return
                    time.sleep(0.05)

            if self._stop.is_set():
                return

            if on_start:
                on_start(start, len(text))

            result = mode.type_text(text, self._stop, start=start)
            completed = result.completed
            self._resume_index = result.next_index
            self._resume_text = text
            if completed:
                self.clear_resume()
        finally:
            self._busy.clear()
            if on_done:
                on_done(completed, was_resume)

"""打字模式基类。"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TypeResult:
    """打字结果：是否完成，以及下次应从哪一字符续打。"""

    completed: bool
    next_index: int


class TypingMode(ABC):
    name: str = "base"
    label: str = "未命名"

    @abstractmethod
    def type_text(
        self,
        text: str,
        stop_event: threading.Event,
        start: int = 0,
    ) -> TypeResult:
        """
        从 start 起输入文本。
        完成时 next_index == len(text)；中断时 next_index 为尚未输入的下一字符下标。
        """

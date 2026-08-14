"""热键冲突检测模块"""

from __future__ import annotations

import json
import threading
from collections.abc import Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import TYPE_CHECKING

from pynput import keyboard

from config import MODIFIER_NAMES, normalize_hotkey
from logger import log, log_exception

if TYPE_CHECKING:
    from config import AppConfig

CONFLICTS_PATH = Path(__file__).resolve().parent / "conflicts.json"


@dataclass
class HotkeyConflict:
    """热键冲突记录"""
    hotkey: str
    process: str
    timestamp: float


class HotkeyConflictDetector:
    """检测系统中的热键冲突"""
    
    def __init__(self) -> None:
        self._listener: keyboard.Listener | None = None
        self._pressed: set = set()
        self._known_hotkeys: set = set()
        self._conflicts: list[HotkeyConflict] = []
        self._lock = threading.Lock()
        self._conflict_callbacks: list[Callable[[list], None]] = []
    
    def add_known_hotkey(self, hotkey: str) -> None:
        """添加已知热键到排除列表"""
        self._known_hotkeys.add(normalize_hotkey(hotkey).lower())
    
    def start(self) -> bool:
        """启动冲突检测"""
        if self._listener is not None:
            return True
        try:
            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
            )
            self._listener.daemon = True
            self._listener.start()
            log("Conflict detector started")
            return True
        except Exception as e:
            log_exception(f"Conflict detector failed: {e}")
            return False
    
    def stop(self) -> None:
        """停止冲突检测"""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
    
    def _on_press(self, key) -> None:
        """监听按键按下"""
        nk = self._normalize(key)
        self._pressed.add(nk)
        
        # 检查是否与已知热键匹配
        for known in self._known_hotkeys:
            if self._matches_keycombo(known, self._pressed):
                self._record_conflict(known)
                break
    
    def _on_release(self, key) -> None:
        """监听按键释放"""
        nk = self._normalize(key)
        self._pressed.discard(nk)
    
    def _normalize(self, key) -> object:
        """规范化按键对象"""
        if isinstance(key, keyboard.KeyCode):
            if key.vk is not None and 0x30 <= key.vk <= 0x5A:
                return chr(key.vk).lower()
            if key.char:
                return key.char.lower()
            return key
        return key
    
    def _matches_keycombo(self, hotkey: str, pressed: set) -> bool:
        """检查当前按键组合是否匹配热键"""
        parts = frozenset(hotkey.split("+"))
        return parts.issubset(pressed)
    
    def _record_conflict(self, hotkey: str) -> None:
        """记录冲突事件"""
        conflict = HotkeyConflict(
            hotkey=hotkey,
            process="unknown",  # 简化版不检测具体进程
            timestamp=__import__("time").monotonic(),
        )
        with self._lock:
            self._conflicts.append(conflict)
            # 只保留最近10个冲突
            self._conflicts = self._conflicts[-10:]
            callbacks = self._conflict_callbacks.copy()
        
        for cb in callbacks:
            try:
                cb(self._conflicts.copy())
            except Exception as e:
                log_exception(f"Conflict callback failed: {e}")
    
    def get_conflicts(self) -> list[HotkeyConflict]:
        """获取最近的冲突记录"""
        with self._lock:
            return self._conflicts.copy()
    
    def clear_conflicts(self) -> None:
        """清除冲突记录"""
        with self._lock:
            self._conflicts.clear()
    
    def save_conflicts(self) -> None:
        """保存冲突记录到文件"""
        try:
            data = [asdict(c) for c in self._conflicts]
            CONFLICTS_PATH.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            log_exception(f"Failed to save conflicts: {e}")
    
    def load_conflicts(self) -> list[HotkeyConflict]:
        """从文件加载冲突记录"""
        try:
            if CONFLICTS_PATH.exists():
                data = json.loads(CONFLICTS_PATH.read_text(encoding="utf-8"))
                return [HotkeyConflict(**c) for c in data]
        except Exception as e:
            log_exception(f"Failed to load conflicts: {e}")
        return []
    
    def on_conflict(self, callback: Callable[[list], None]) -> None:
        """注册冲突回调"""
        with self._lock:
            self._conflict_callbacks.append(callback)

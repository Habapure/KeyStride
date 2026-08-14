"""本地配置持久化。"""

from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"

DELAY_OPTIONS = (0.0, 1.5, 3.0)
MODE_NAMES = frozenset(("human", "fast", "instant"))
MODIFIER_NAMES = frozenset(("ctrl", "shift", "alt", "win"))


def normalize_hotkey(value: object, default: str = "ctrl+shift+v") -> str:
    """Return a supported hotkey string, or the supplied default."""
    if not isinstance(value, str):
        return default
    parts = [part.strip().lower() for part in value.split("+") if part.strip()]
    if len(parts) < 2 or len(parts) != len(set(parts)):
        return default
    main_keys = [part for part in parts if part not in MODIFIER_NAMES]
    if len(main_keys) != 1 or len(main_keys[0]) != 1:
        return default
    if any(part not in MODIFIER_NAMES and part != main_keys[0] for part in parts):
        return default
    return "+".join(parts)


@dataclass
class AppConfig:
    mode: str = "human"
    enabled: bool = True
    delay_seconds: float = 1.5
    hotkey: str = "ctrl+shift+v"
    sound_enabled: bool = False

    def save(self, path: Path = CONFIG_PATH) -> None:
        """Atomically persist the configuration so an interrupted write is harmless."""
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_suffix(path.suffix + ".tmp")
        temporary_path.write_text(
            json.dumps(asdict(self), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary_path, path)

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> AppConfig:
        if not path.exists():
            cfg = cls()
            cfg.save(path)
            return cfg
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return cls()
        if not isinstance(data, dict):
            return cls()

        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known}
        cfg = cls(**filtered)
        if not isinstance(cfg.mode, str) or cfg.mode not in MODE_NAMES:
            cfg.mode = "human"
        if (
            isinstance(cfg.delay_seconds, bool)
            or not isinstance(cfg.delay_seconds, (int, float))
            or not math.isfinite(cfg.delay_seconds)
        ):
            cfg.delay_seconds = cls.delay_seconds
        else:
            cfg.delay_seconds = min(DELAY_OPTIONS, key=lambda x: abs(x - cfg.delay_seconds))
        if not isinstance(cfg.enabled, bool):
            cfg.enabled = cls.enabled
        if not isinstance(cfg.sound_enabled, bool):
            cfg.sound_enabled = cls.sound_enabled
        cfg.hotkey = normalize_hotkey(cfg.hotkey, cls.hotkey)
        return cfg
# GitHub Actions test

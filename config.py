"""本地配置持久化。"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"

DELAY_OPTIONS = (0.0, 1.5, 3.0)


@dataclass
class AppConfig:
    mode: str = "human"
    enabled: bool = True
    delay_seconds: float = 1.5
    hotkey: str = "ctrl+shift+v"
    sound_enabled: bool = False

    def save(self, path: Path = CONFIG_PATH) -> None:
        path.write_text(
            json.dumps(asdict(self), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> AppConfig:
        if not path.exists():
            cfg = cls()
            cfg.save(path)
            return cfg
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()

        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known}
        cfg = cls(**filtered)
        if cfg.mode not in ("human", "fast", "instant"):
            cfg.mode = "human"
        if cfg.delay_seconds not in DELAY_OPTIONS:
            # 允许接近值，否则回退默认
            closest = min(DELAY_OPTIONS, key=lambda x: abs(x - cfg.delay_seconds))
            cfg.delay_seconds = closest
        return cfg

"""运行日志（排查闪退）。"""

from __future__ import annotations

import traceback
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "runtime.log"


def log(msg: str) -> None:
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}\n"
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass


def log_exception(prefix: str) -> None:
    log(prefix + "\n" + traceback.format_exc())

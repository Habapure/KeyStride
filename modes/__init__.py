from .base import TypingMode
from .fast import FastMode
from .human import HumanMode
from .instant import InstantMode

MODE_MAP: dict[str, TypingMode] = {
    "human": HumanMode(),
    "fast": FastMode(),
    "instant": InstantMode(),
}

MODE_LABELS = {
    "human": "仿真输入",
    "fast": "快速输入",
    "instant": "瞬间输入",
}


def get_mode(name: str) -> TypingMode:
    return MODE_MAP.get(name, MODE_MAP["human"])

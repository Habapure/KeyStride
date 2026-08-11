"""KeyStride core modules.

Imports stay lazy so the typing engine can be used without a clipboard backend.
"""

__all__ = ["get_clipboard_text", "TypingEngine"]


def __getattr__(name: str):
    if name == "get_clipboard_text":
        from .clipboard import get_clipboard_text

        return get_clipboard_text
    if name == "TypingEngine":
        from .engine import TypingEngine

        return TypingEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

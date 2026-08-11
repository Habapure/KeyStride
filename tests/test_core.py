from __future__ import annotations

import tempfile
import threading
import unittest
from pathlib import Path

from config import AppConfig, normalize_hotkey
from core.engine import TypingEngine
from hotkey import HotkeyListener
from modes.base import TypeResult, TypingMode
from pynput import keyboard


class CompleteMode(TypingMode):
    def type_text(self, text, stop_event, start=0):
        return TypeResult(True, len(text))


class BlockingMode(TypingMode):
    def __init__(self):
        self.started = threading.Event()

    def type_text(self, text, stop_event, start=0):
        self.started.set()
        while not stop_event.wait(0.01):
            pass
        return TypeResult(False, start + 1)


class ConfigTests(unittest.TestCase):
    def test_hotkey_validation(self):
        self.assertEqual(normalize_hotkey("ctrl + alt + x"), "ctrl+alt+x")
        self.assertEqual(normalize_hotkey("ctrl+shift+f12"), "ctrl+shift+v")
        self.assertEqual(normalize_hotkey("ctrl+ctrl+x"), "ctrl+shift+v")

    def test_invalid_config_values_fall_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(
                '{"mode": 7, "enabled": "yes", "delay_seconds": "now", '
                '"hotkey": "ctrl+f12", "sound_enabled": 1}',
                encoding="utf-8",
            )
            config = AppConfig.load(path)
        self.assertEqual(config.mode, "human")
        self.assertTrue(config.enabled)
        self.assertEqual(config.delay_seconds, 1.5)
        self.assertEqual(config.hotkey, "ctrl+shift+v")
        self.assertFalse(config.sound_enabled)


class TypingEngineTests(unittest.TestCase):
    def test_completed_job_clears_resume_state(self):
        engine = TypingEngine()
        finished = threading.Event()
        self.assertTrue(engine.type_async("hello", CompleteMode(), on_done=lambda *_: finished.set()))
        self.assertTrue(finished.wait(1))
        self.assertFalse(engine.is_busy)
        self.assertFalse(engine.has_resume)

    def test_stopped_job_keeps_resume_position(self):
        engine = TypingEngine()
        mode = BlockingMode()
        finished = threading.Event()
        self.assertTrue(engine.type_async("hello", mode, on_done=lambda *_: finished.set()))
        self.assertTrue(mode.started.wait(1))
        engine.stop()
        self.assertTrue(finished.wait(1))
        self.assertTrue(engine.has_resume)
        self.assertEqual(engine.resume_index, 1)


class HotkeyTests(unittest.TestCase):
    def test_configured_main_key_is_not_hard_coded_to_v(self):
        triggers: list[str] = []
        listener = HotkeyListener(
            lambda: triggers.append("trigger"),
            lambda: triggers.append("cancel"),
            "ctrl+alt+x",
        )
        listener._on_press(keyboard.Key.ctrl_l)
        listener._on_press(keyboard.Key.alt_l)
        listener._on_press(keyboard.KeyCode.from_char("x"))
        listener._on_release(keyboard.KeyCode.from_char("x"))
        listener._on_release(keyboard.Key.alt_l)
        listener._on_release(keyboard.Key.ctrl_l)
        self.assertEqual(triggers, ["trigger"])


if __name__ == "__main__":
    unittest.main()

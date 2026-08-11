"""键步如飞·KeyStride — 入口。"""

from __future__ import annotations

import atexit
import sys
import threading
import traceback
import winsound
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "error.log"


def _show_error(message: str) -> None:
    try:
        LOG_PATH.write_text(message, encoding="utf-8")
    except OSError:
        pass
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            0,
            message[:1500],
            "键步如飞 KeyStride 启动失败",
            0x10,
        )
    except Exception:
        print(message, file=sys.stderr)


try:
    from config import AppConfig
    from core.clipboard import get_clipboard_text
    from core.engine import TypingEngine
    from hotkey import HotkeyListener
    from logger import log, log_exception
    from modes import MODE_LABELS, get_mode
    from tray import TrayApp
except Exception:
    _show_error("导入依赖失败：\n\n" + traceback.format_exc())
    raise SystemExit(1) from None


def _acquire_single_instance() -> object | None:
    """防止重复启动导致托盘异常；已运行则提示并退出。"""
    import ctypes

    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, "Local\\KeyStride_SingleInstance")
    if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        kernel32.CloseHandle(mutex)
        ctypes.windll.user32.MessageBoxW(
            0,
            "键步如飞已经在运行中。\n请到右下角托盘（^ 隐藏图标）查找蓝色图标。",
            "KeyStride",
            0x40,
        )
        return None
    return mutex


class App:
    def __init__(self) -> None:
        self.config = AppConfig.load()
        self.engine = TypingEngine()
        self.tray: TrayApp | None = None
        self._status = ""
        self._status_lock = threading.Lock()
        self.hotkey = HotkeyListener(
            on_trigger=self.on_hotkey,
            on_cancel=self.on_cancel,
        )

    def set_status(self, text: str) -> None:
        # 不从后台线程刷新托盘（会导致 pystray 闪退）
        with self._status_lock:
            self._status = text
        log(f"status: {text}")

    def get_status(self) -> str:
        with self._status_lock:
            return self._status

    def beep(self, ok: bool = True) -> None:
        if not self.config.sound_enabled:
            return
        try:
            freq, dur = (750, 120) if ok else (400, 200)
            winsound.Beep(freq, dur)
        except Exception:
            pass

    def on_cancel(self) -> None:
        if self.engine.is_busy:
            self.engine.stop()
            self.set_status("已中断")

    def on_hotkey(self) -> None:
        if self.engine.is_busy:
            self.engine.stop()
            self.set_status("已中断")
            return

        if not self.config.enabled:
            self.set_status("未启用")
            self.beep(False)
            return

        text = get_clipboard_text()
        if not text:
            self.set_status("剪贴板为空")
            self.beep(False)
            return

        mode = get_mode(self.config.mode)
        delay = self.config.delay_seconds
        mode_label = MODE_LABELS.get(self.config.mode, self.config.mode)

        if delay > 0:
            self.set_status(f"{delay:g}s 后开始 ({mode_label})")
            self.beep(True)
        else:
            self.set_status(f"输入中 ({mode_label})")

        def on_start(start: int, total: int) -> None:
            if start > 0:
                self.set_status(f"续打 {start}/{total} ({mode_label})")
            else:
                self.set_status(f"输入中 ({mode_label})")

        started = self.engine.type_async(
            text,
            mode,
            delay_seconds=delay,
            on_start=on_start,
            on_done=self._on_done,
        )
        if not started:
            self.engine.stop()

    def _on_done(self, completed: bool, was_resume: bool = False) -> None:
        if completed:
            self.set_status("完成")
            self.beep(True)
            return
        if self.engine.has_resume:
            idx = self.engine.resume_index
            self.set_status(f"已中断，断点 {idx}（再按热键续打）")
        elif self.get_status() != "已中断":
            self.set_status("已停止")

    def on_toggle_enabled(self, enabled: bool) -> None:
        self.config.enabled = enabled
        self.config.save()
        self.set_status("已启用" if enabled else "已禁用")
        if self.tray:
            self.tray.refresh()

    def on_mode_change(self, mode: str) -> None:
        self.config.mode = mode
        self.config.save()
        self.set_status(f"模式: {MODE_LABELS.get(mode, mode)}")
        if self.tray:
            self.tray.refresh()

    def on_delay_change(self, seconds: float) -> None:
        self.config.delay_seconds = seconds
        self.config.save()
        self.set_status("延迟: 立即" if seconds <= 0 else f"延迟: {seconds:g}s")
        if self.tray:
            self.tray.refresh()

    def on_sound_toggle(self, enabled: bool) -> None:
        self.config.sound_enabled = enabled
        self.config.save()
        self.set_status("提示音: 开" if enabled else "提示音: 关")
        if self.tray:
            self.tray.refresh()

    def on_quit(self) -> None:
        log("app: on_quit")
        self.engine.stop()
        self.hotkey.stop()
        if self.tray:
            self.tray.stop()

    def run(self) -> int:
        if sys.platform != "win32":
            print("仅支持 Windows")
            return 1

        log("app: start")
        self.tray = TrayApp(
            self.config,
            on_toggle_enabled=self.on_toggle_enabled,
            on_mode_change=self.on_mode_change,
            on_delay_change=self.on_delay_change,
            on_sound_toggle=self.on_sound_toggle,
            on_quit=self.on_quit,
            status_text=self.get_status,
        )
        try:
            self.hotkey.start()
            log("app: hotkey started")
        except Exception:
            log_exception("hotkey start failed")
            _show_error("全局热键启动失败（可能被杀软拦截）：\n\n" + traceback.format_exc())
            return 1

        self.set_status("就绪 Ctrl+Shift+V")
        self.beep(True)
        self.tray.run()
        log("app: exit normally")
        return 0


def main() -> int:
    log("=== process boot ===")
    mutex = _acquire_single_instance()
    if mutex is None:
        log("already running - exit")
        return 0

    def _release() -> None:
        try:
            import ctypes

            ctypes.windll.kernel32.CloseHandle(mutex)
        except Exception:
            pass

    atexit.register(_release)
    return App().run()


if __name__ == "__main__":
    try:
        code = main()
        log(f"SystemExit: {code}")
        raise SystemExit(code)
    except SystemExit:
        raise
    except Exception:
        log_exception("fatal")
        _show_error("运行出错：\n\n" + traceback.format_exc())
        raise SystemExit(1) from None

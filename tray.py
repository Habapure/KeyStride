"""系统托盘界面。"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pystray
from PIL import Image, ImageDraw

from logger import log, log_exception
from modes import MODE_LABELS

if TYPE_CHECKING:
    from config import AppConfig


def _make_icon(size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = size // 10
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=size // 8,
        fill=(32, 120, 200, 255),
    )
    pad = size // 4
    gap = size // 10
    r = size // 14
    for row in range(2):
        for col in range(3):
            cx = pad + col * (r * 2 + gap) + r
            cy = pad + row * (r * 2 + gap) + r + size // 16
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 230))
    return img


class TrayApp:
    def __init__(
        self,
        config: AppConfig,
        *,
        on_toggle_enabled: Callable[[bool], None],
        on_mode_change: Callable[[str], None],
        on_delay_change: Callable[[float], None],
        on_sound_toggle: Callable[[bool], None],
        on_quit: Callable[[], None],
        status_text: Callable[[], str] | None = None,
    ) -> None:
        self.config = config
        self._on_toggle_enabled = on_toggle_enabled
        self._on_mode_change = on_mode_change
        self._on_delay_change = on_delay_change
        self._on_sound_toggle = on_sound_toggle
        self._on_quit = on_quit
        self._status_text = status_text
        self.icon: pystray.Icon | None = None

    def _title(self) -> str:
        mode = MODE_LABELS.get(self.config.mode, self.config.mode)
        state = "已启用" if self.config.enabled else "已禁用"
        base = f"KeyStride - {mode} ({state})"
        if self._status_text:
            extra = self._status_text()
            if extra:
                return f"{base} | {extra}"
        return base

    def _build_menu(self) -> pystray.Menu:
        cfg = self.config

        def set_mode(mode: str):
            def handler(icon, item):  # noqa: ARG001
                self._on_mode_change(mode)

            return handler

        def set_delay(seconds: float):
            def handler(icon, item):  # noqa: ARG001
                self._on_delay_change(seconds)

            return handler

        def toggle_enabled(icon, item):  # noqa: ARG001
            self._on_toggle_enabled(not cfg.enabled)

        def toggle_sound(icon, item):  # noqa: ARG001
            self._on_sound_toggle(not cfg.sound_enabled)

        def quit_app(icon, item):  # noqa: ARG001
            log("tray: quit clicked")
            self._on_quit()

        return pystray.Menu(
            pystray.MenuItem("键步如飞 KeyStride", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                lambda item: "启用（开）" if cfg.enabled else "启用（关）",
                toggle_enabled,
                checked=lambda item: cfg.enabled,
            ),
            pystray.MenuItem(
                lambda item: "提示音（开）" if cfg.sound_enabled else "提示音（关）",
                toggle_sound,
                checked=lambda item: cfg.sound_enabled,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "打字模式",
                pystray.Menu(
                    pystray.MenuItem(
                        MODE_LABELS["human"],
                        set_mode("human"),
                        checked=lambda item: cfg.mode == "human",
                        radio=True,
                    ),
                    pystray.MenuItem(
                        MODE_LABELS["fast"],
                        set_mode("fast"),
                        checked=lambda item: cfg.mode == "fast",
                        radio=True,
                    ),
                    pystray.MenuItem(
                        MODE_LABELS["instant"],
                        set_mode("instant"),
                        checked=lambda item: cfg.mode == "instant",
                        radio=True,
                    ),
                ),
            ),
            pystray.MenuItem(
                "触发延迟",
                pystray.Menu(
                    pystray.MenuItem(
                        "立即 (0秒)",
                        set_delay(0.0),
                        checked=lambda item: cfg.delay_seconds == 0.0,
                        radio=True,
                    ),
                    pystray.MenuItem(
                        "1.5 秒",
                        set_delay(1.5),
                        checked=lambda item: cfg.delay_seconds == 1.5,
                        radio=True,
                    ),
                    pystray.MenuItem(
                        "3 秒",
                        set_delay(3.0),
                        checked=lambda item: cfg.delay_seconds == 3.0,
                        radio=True,
                    ),
                ),
            ),
            pystray.MenuItem(f"热键: {self.config.hotkey.upper()}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", quit_app),
        )

    def refresh(self) -> None:
        """Refresh title and menu after a tray-menu configuration change."""
        if self.icon is None:
            return
        try:
            self.icon.title = self._title()
            self.icon.menu = self._build_menu()
            self.icon.update_menu()
        except Exception:
            log_exception("tray.refresh failed")


    def run(self) -> None:
        log("tray: creating icon")
        self.icon = pystray.Icon(
            "KeyStride",
            _make_icon(),
            self._title(),
            self._build_menu(),
        )

        def setup(icon: pystray.Icon) -> None:
            icon.visible = True
            log("tray: icon visible")

        log("tray: entering run loop")
        try:
            self.icon.run(setup=setup)
        except Exception:
            log_exception("tray.run crashed")
            raise
        log("tray: run loop ended")

    def stop(self) -> None:
        if self.icon is not None:
            log("tray: stop()")
            try:
                self.icon.stop()
            except Exception:
                log_exception("tray.stop failed")

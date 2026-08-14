"""键步如飞 KeyStride — 主窗口"""

from __future__ import annotations

import ctypes
import sys
from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QSystemTrayIcon,
    QMenu,
    QButtonGroup,
)

from logger import log, log_exception
from modes import MODE_LABELS, get_mode

if TYPE_CHECKING:
    from config import AppConfig


# ═══════════════════════════════════════════
#  模式卡片（可点击的 Frame）
# ═══════════════════════════════════════════

class ModeCard(QFrame):
    """一个可点击的模式选择卡片。"""

    clicked = Signal(str)  # mode_id

    MODE_DATA = [
        ("human", "🧑‍💻", "仿真输入", "随机延时 + 自然停顿\n模拟真人打字节奏"),
        ("fast", "⚡", "快速输入", "短延时逐字打出\n速度远快于真人"),
        ("instant", "🚀", "瞬间输入", "批量 SendInput\n一眨眼完成全部内容"),
    ]

    def __init__(self, mode_id: str, icon: str, title: str, desc: str, parent=None):
        super().__init__(parent)
        self._mode_id = mode_id
        self._active = False
        self.setObjectName("modeCard")
        self.setProperty("active", "false")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(156, 120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 8)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        self._icon_label = QLabel(icon)
        self._icon_label.setObjectName("modeIcon")
        self._icon_label.setAlignment(Qt.AlignCenter)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("modeTitle")
        self._title_label.setAlignment(Qt.AlignCenter)

        self._desc_label = QLabel(desc)
        self._desc_label.setObjectName("modeDesc")
        self._desc_label.setAlignment(Qt.AlignCenter)
        self._desc_label.setWordWrap(True)

        layout.addWidget(self._icon_label)
        layout.addWidget(self._title_label)
        layout.addWidget(self._desc_label)

    @property
    def mode_id(self) -> str:
        return self._mode_id

    def set_active(self, active: bool) -> None:
        self._active = active
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        super().mousePressEvent(event)
        self.clicked.emit(self._mode_id)


# ═══════════════════════════════════════════
#  状态指示器（圆形点 + 标签）
# ═══════════════════════════════════════════

class StatusDot(QFrame):
    """彩色状态圆点。"""

    COLORS = {
        "ready": "#10b981",      # 绿
        "typing": "#2563eb",     # 蓝
        "idle": "#94a3b8",       # 灰
        "error": "#ef4444",      # 红
        "paused": "#f59e0b",     # 黄
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusDot")
        self.set_color("idle")

    def set_color(self, state: str) -> None:
        color = self.COLORS.get(state, "#94a3b8")
        self.setStyleSheet(f"#statusDot {{ background-color: {color}; }}")
        self.setToolTip(
            {"ready": "就绪", "typing": "输入中", "idle": "待机",
             "error": "错误", "paused": "已暂停"}.get(state, "")
        )


# ═══════════════════════════════════════════
#  主窗口
# ═══════════════════════════════════════════

class MainWindow(QMainWindow):
    """键步如飞主界面。"""

    signal_enabled_changed = Signal(bool)
    signal_mode_changed = Signal(str)
    signal_delay_changed = Signal(float)
    signal_sound_changed = Signal(bool)
    signal_minimize_changed = Signal(bool)
    signal_quit = Signal()

    def __init__(
        self,
        config: AppConfig,
        *,
        on_toggle_enabled: Callable[[bool], None] | None = None,
        on_mode_change: Callable[[str], None] | None = None,
        on_delay_change: Callable[[float], None] | None = None,
        on_sound_toggle: Callable[[bool], None] | None = None,
        on_hotkey_change: Callable[[str], None] | None = None,
        on_quit: Callable[[], None] | None = None,
        status_text: Callable[[], str] | None = None,
        status_setter: Callable[[str], None] | None = None,
        on_conflict_check: Callable[[], list] | None = None,
    ):
        super().__init__()
        self.config = config
        self._on_toggle_enabled = on_toggle_enabled
        self._on_mode_change = on_mode_change
        self._on_delay_change = on_delay_change
        self._on_sound_toggle = on_sound_toggle
        self._on_hotkey_change = on_hotkey_change
        self._on_quit = on_quit
        self._status_text = status_text
        self._status_setter = status_setter
        self._on_conflict_check = on_conflict_check
        self._conflicts: list = []

        self._card_widgets: dict[str, ModeCard] = {}
        self._tray: QSystemTrayIcon | None = None
        self._resizer: WindowResizer | None = None

        self._build_ui()
        self._create_tray()
        self._connect_signals()
        self._sync_from_config()
        
        # 启用窗口可调整大小
        self.setFixedSize(560, 720)
        self.setMinimumSize(480, 640)
        self.setSizeIncrement(10, 10)

        # 定时刷新状态
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._refresh_status)
        self._status_timer.start(500)

        self._apply_stylesheet()

    # ── UI 构建 ──────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("键步如飞 · KeyStride")
        self.setMinimumSize(480, 640)
        self.resize(480, 640)
        self.setObjectName("mainWindow")

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── 标题栏 ──
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 0, 20, 0)

        app_title = QLabel("✦ 键步如飞")
        app_title.setObjectName("appTitle")
        app_sub = QLabel("· KeyStride")
        app_sub.setObjectName("appSubtitle")

        title_layout.addWidget(app_title)
        title_layout.addWidget(app_sub)
        title_layout.addStretch()

        # ── 可滚动内容区 ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(20)

        # ── 状态卡片 ──
        self._status_card = QFrame()
        self._status_card.setObjectName("statusCard")
        status_layout = QHBoxLayout(self._status_card)
        status_layout.setContentsMargins(16, 12, 16, 12)
        status_layout.setSpacing(12)

        self._status_dot = StatusDot()
        status_text_col = QVBoxLayout()
        status_text_col.setSpacing(2)
        self._status_label = QLabel("就绪")
        self._status_label.setObjectName("statusLabel")
        self._hotkey_hint = QLabel("热键: Ctrl+Shift+V  ·  ESC 中断")
        self._hotkey_hint.setObjectName("hotkeyHint")
        status_text_col.addWidget(self._status_label)
        status_text_col.addWidget(self._hotkey_hint)

        self._toggle_btn = QPushButton("禁用")
        self._toggle_btn.setObjectName("statusActionBtn")
        self._toggle_btn.setFixedWidth(72)
        self._toggle_btn.clicked.connect(self._on_toggle_clicked)

        status_layout.addWidget(self._status_dot)
        status_layout.addLayout(status_text_col)
        status_layout.addStretch()
        status_layout.addWidget(self._toggle_btn)

        content_layout.addWidget(self._status_card)

        # ── 打字模式 ──
        mode_title = QLabel("打字模式")
        mode_title.setProperty("class", "sectionTitle")
        content_layout.addWidget(mode_title)

        card_row = QHBoxLayout()
        card_row.setSpacing(12)

        for mid, icon, title, desc in ModeCard.MODE_DATA:
            card = ModeCard(mid, icon, title, desc)
            card.clicked.connect(self._on_mode_card_clicked)
            self._card_widgets[mid] = card
            card_row.addWidget(card)

        card_row.addStretch()
        content_layout.addLayout(card_row)

        # ── 设置面板 ──
        settings_group = QFrame()
        settings_group.setObjectName("settingsGroup")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(14)

        # 触发延迟
        delay_title = QLabel("触发延迟")
        delay_title.setProperty("class", "settingLabel")
        settings_layout.addWidget(delay_title)

        delay_row = QHBoxLayout()
        delay_row.setSpacing(16)
        self._delay_group = QButtonGroup(self)
        self._delay_radios: dict[float, QRadioButton] = {}
        for val, label in [(0.0, "立即发送"), (1.5, "1.5 秒"), (3.0, "3 秒")]:
            rb = QRadioButton(label)
            self._delay_group.addButton(rb, int(val * 10))
            self._delay_radios[val] = rb
            delay_row.addWidget(rb)
        delay_row.addStretch()
        settings_layout.addLayout(delay_row)

        # 分隔
        settings_layout.addSpacing(4)

        # 提示音
        self._sound_cb = QCheckBox("启用提示音（开始/完成/中断时响一声）")
        settings_layout.addWidget(self._sound_cb)

        # 最小化到托盘
        self._minimize_cb = QCheckBox("关闭窗口时最小化到托盘（不退出程序）")
        self._minimize_cb.setChecked(True)
        settings_layout.addWidget(self._minimize_cb)

        content_layout.addWidget(settings_group)
        content_layout.addStretch()

        scroll.setWidget(content)
        root_layout.addWidget(title_bar)
        root_layout.addWidget(scroll, 1)

        # ── 底部栏 ──
        bottom_bar = QWidget()
        bottom_bar.setObjectName("bottomBar")
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(20, 0, 20, 0)

        self._about_btn = QPushButton("关于")
        self._about_btn.clicked.connect(self._show_about)
        self._exit_btn = QPushButton("退出")
        self._exit_btn.clicked.connect(self._on_quit_clicked)

        bottom_layout.addWidget(self._about_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self._exit_btn)

        root_layout.addWidget(bottom_bar)

    # ── 系统托盘 ──────────────────────────────

    def _make_tray_icon(self) -> QIcon:
        """生成蓝色键盘托盘图标。"""
        size = 64
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing)

        # 圆角矩形底
        painter.setBrush(QColor("#2563eb"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(6, 6, 52, 52, 8, 8)

        # 白色小方块（模拟键盘按键）
        painter.setBrush(QColor(255, 255, 255, 220))
        key_w, key_h, gap = 10, 10, 4
        ox, oy = 13, 14
        for row in range(3):
            for col in range(4):
                x = ox + col * (key_w + gap)
                y = oy + row * (key_h + gap)
                painter.drawRoundedRect(x, y, key_w, key_h, 2, 2)

        painter.end()
        return QIcon(pix)

    def _create_tray(self) -> None:
        self._tray = QSystemTrayIcon(self._make_tray_icon(), self)
        self._tray.setToolTip("键步如飞 · KeyStride")

        menu = QMenu()

        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)

        menu.addSeparator()

        # 模式快速切换
        for mid, data in [("human", "仿真输入"), ("fast", "快速输入"), ("instant", "瞬间输入")]:
            act = QAction(data, self)
            act.setCheckable(True)
            act.setChecked(self.config.mode == mid)
            act.triggered.connect(lambda checked, m=mid: self._on_mode_card_clicked(m))
            menu.addAction(act)

        menu.addSeparator()

        delay_menu = QMenu("触发延迟", self)
        for val, label in [(0.0, "立即"), (1.5, "1.5秒"), (3.0, "3秒")]:
            act = QAction(label, delay_menu)
            act.setCheckable(True)
            act.setChecked(self.config.delay_seconds == val)
            act.triggered.connect(lambda checked, v=val: self._on_delay_radio_changed(v))
            delay_menu.addAction(act)
        menu.addMenu(delay_menu)

        menu.addSeparator()

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self._on_quit_clicked)
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    # ── 信号连接 ──────────────────────────────

    def _connect_signals(self) -> None:
        self._delay_group.idClicked.connect(self._on_delay_group_changed)
        self._sound_cb.stateChanged.connect(
            lambda: self._on_sound_toggled(self._sound_cb.isChecked())
        )
        self._minimize_cb.stateChanged.connect(
            lambda: self._on_minimize_toggled(self._minimize_cb.isChecked())
        )

        self.signal_enabled_changed.connect(self._on_enabled_changed_ui)
        self.signal_mode_changed.connect(self._on_mode_changed_ui)
        self.signal_delay_changed.connect(self._on_delay_changed_ui)
        self.signal_sound_changed.connect(self._on_sound_changed_ui)

    def _apply_stylesheet(self) -> None:
        from ui.styles import STYLESHEET
        self.setStyleSheet(STYLESHEET)

    # ── 同步配置到 UI ─────────────────────────

    def _sync_from_config(self) -> None:
        cfg = self.config
        self._on_enabled_changed_ui(cfg.enabled)
        self._on_mode_changed_ui(cfg.mode)
        self._on_delay_changed_ui(cfg.delay_seconds)
        self._on_sound_changed_ui(cfg.sound_enabled)
        self._minimize_cb.setChecked(True)

    # ── 状态刷新 ──────────────────────────────

    def _refresh_status(self) -> None:
        if self._status_text:
            txt = self._status_text()
            if txt:
                self._status_label.setText(txt)
                if "输入中" in txt or "续打" in txt:
                    self._status_dot.set_color("typing")
                elif "中断" in txt or "完成" in txt:
                    self._status_dot.set_color("ready")
                elif "禁用" in txt or "未启用" in txt:
                    self._status_dot.set_color("paused")
                else:
                    self._status_dot.set_color("ready")
            else:
                if self.config.enabled:
                    self._status_label.setText("就绪")
                    self._status_dot.set_color("ready")
                else:
                    self._status_label.setText("已禁用")
                    self._status_dot.set_color("paused")

    # ── 内部事件处理 ───────────────────────────

    def _on_toggle_clicked(self) -> None:
        new_state = not self.config.enabled
        if self._on_toggle_enabled:
            self._on_toggle_enabled(new_state)

    def _on_mode_card_clicked(self, mode_id: str) -> None:
        if self._on_mode_change:
            self._on_mode_change(mode_id)

    def _on_delay_group_changed(self, radio_id: int) -> None:
        seconds = radio_id / 10.0
        if self._on_delay_change:
            self._on_delay_change(seconds)

    def _on_delay_radio_changed(self, seconds: float) -> None:
        if self._on_delay_change:
            self._on_delay_change(seconds)

    def _on_sound_toggled(self, enabled: bool) -> None:
        if self._on_sound_toggle:
            self._on_sound_toggle(enabled)

    def _on_minimize_toggled(self, enabled: bool) -> None:
        pass  # 由 closeEvent 处理

    def set_status(self, text: str) -> None:
        """Push a status string from any thread (typing engine callback)."""
        if not QApplication.instance():
            return
        if self._status_setter:
            self._status_setter(text)

    def refresh_hotkey_label(self) -> None:
        if hasattr(self, "_hotkey_hint"):
            hk = self.config.hotkey.upper()
            self._hotkey_hint.setText("hotkey: " + hk + "  |  ESC to abort")

    def _on_quit_clicked(self) -> None:
        if self._tray:
            self._tray.hide()
        if self._on_quit:
            self._on_quit()
        QApplication.quit()

    def _show_about(self) -> None:
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "关于 键步如飞 · KeyStride",
            "<h3>✦ 键步如飞 KeyStride</h3>"
            "<p>版本 1.0</p>"
            "<p>复制内容 → Ctrl+Shift+V → 模拟真人逐字输入</p>"
            "<hr>"
            "<p style='color:#64748b; font-size:12px;'>"
            "三种模式：仿真输入 · 快速输入 · 瞬间输入<br>"
            "支持中文、英文、符号、空格、换行<br>"
            "引擎：Win32 SendInput (Unicode)</p>"
        )

    def _show_window(self) -> None:
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    # ── UI 更新槽（可从任意线程安全调用） ───────

    def _on_enabled_changed_ui(self, enabled: bool) -> None:
        self._toggle_btn.setText("禁用" if enabled else "启用")
        self._toggle_btn.setStyleSheet(
            "" if enabled else "background-color: #64748b;"
        )
        self._status_dot.set_color("ready" if enabled else "paused")
        if enabled:
            self._status_label.setText("就绪")
        else:
            self._status_label.setText("已禁用")

    def _on_mode_changed_ui(self, mode_id: str) -> None:
        for mid, card in self._card_widgets.items():
            card.set_active(mid == mode_id)
        # 更新托盘菜单选中态
        if self._tray:
            menu = self._tray.contextMenu()
            if menu:
                for i, mid in enumerate(["human", "fast", "instant"]):
                    act = menu.actions()[2 + i]  # 前2项是 Show + separator
                    if act:
                        act.setChecked(mid == mode_id)

    def _on_delay_changed_ui(self, seconds: float) -> None:
        rb = self._delay_radios.get(seconds)
        if rb:
            rb.setChecked(True)

    def _on_sound_changed_ui(self, enabled: bool) -> None:
        self._sound_cb.setChecked(enabled)

    # ── 窗口事件 ──────────────────────────────

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._minimize_cb.isChecked() and self._tray and self._tray.isVisible():
            event.ignore()
            self.hide()
            self._tray.showMessage(
                "键步如飞 · KeyStride",
                "程序仍在后台运行，双击托盘图标可显示窗口",
                QSystemTrayIcon.Information,
                3000,
            )
        else:
            self._on_quit_clicked()
            event.accept()

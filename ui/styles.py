"""键步如飞 KeyStride — QSS 样式表"""

STYLESHEET = """
/* ===== 全局 ===== */
QMainWindow {
    background-color: #f0f2f5;
    border: none;
}

QWidget {
    font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC", "Helvetica Neue", sans-serif;
    color: #1e293b;
}

/* ===== 标题栏区域 ===== */
#titleBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    min-height: 52px;
    max-height: 52px;
    padding: 0px 20px;
}

#titleBar QLabel#appTitle {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: 0.3px;
}

#titleBar QLabel#appSubtitle {
    font-size: 12px;
    color: #94a3b8;
    font-weight: 400;
    margin-left: 4px;
}

/* ===== 状态卡片 ===== */
#statusCard {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    padding: 16px 20px;
}

#statusCard #statusDot {
    min-width: 12px;
    max-width: 12px;
    min-height: 12px;
    max-height: 12px;
    border-radius: 6px;
}

#statusCard #statusLabel {
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
}

#statusCard #hotkeyHint {
    font-size: 12px;
    color: #94a3b8;
}

#statusCard #statusActionBtn {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 6px 18px;
    font-size: 12px;
    font-weight: 600;
}
#statusCard #statusActionBtn:hover {
    background-color: #1d4ed8;
}
#statusCard #statusActionBtn:pressed {
    background-color: #1e40af;
}

/* ===== 分节标题 ===== */
.sectionTitle {
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 0px;
    margin: 0px;
}

/* ===== 模式卡片 ===== */
#modeCard {
    background-color: #ffffff;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 12px;
    cursor: pointer;
}

#modeCard:hover {
    border-color: #93c5fd;
    background-color: #f8faff;
}

#modeCard[active="true"] {
    border-color: #2563eb;
    background-color: #eff6ff;
}

#modeCard #modeIcon {
    font-size: 22px;
}

#modeCard #modeTitle {
    font-size: 13px;
    font-weight: 700;
    color: #0f172a;
}

#modeCard[active="true"] #modeTitle {
    color: #1d4ed8;
}

#modeCard #modeDesc {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 1px;
}

/* ===== 设置面板 ===== */
#settingsGroup {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 20px;
}

#settingsGroup QLabel.settingLabel {
    font-size: 13px;
    font-weight: 500;
    color: #334155;
}

/* 自定义 RadioButton */
QRadioButton {
    font-size: 13px;
    color: #475569;
    spacing: 8px;
    padding: 4px 0px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #cbd5e1;
    background-color: #ffffff;
}

QRadioButton::indicator:hover {
    border-color: #93c5fd;
}

QRadioButton::indicator:checked {
    border-color: #2563eb;
    background-color: #2563eb;
    image: url(none);
}

/* 自定义 CheckBox */
QCheckBox {
    font-size: 13px;
    color: #475569;
    spacing: 8px;
    padding: 4px 0px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #cbd5e1;
    background-color: #ffffff;
}

QCheckBox::indicator:hover {
    border-color: #93c5fd;
}

QCheckBox::indicator:checked {
    border-color: #2563eb;
    background-color: #2563eb;
}

/* ===== 底部操作栏 ===== */
#bottomBar {
    background-color: #ffffff;
    border-top: 1px solid #e2e8f0;
    min-height: 48px;
    max-height: 48px;
    padding: 0px 20px;
}

#bottomBar QPushButton {
    background: transparent;
    border: none;
    font-size: 12px;
    font-weight: 500;
    color: #64748b;
    padding: 4px 12px;
    border-radius: 6px;
}

#bottomBar QPushButton:hover {
    background-color: #f1f5f9;
    color: #334155;
}

/* 主按钮 */
QPushButton#primaryBtn {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 24px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#primaryBtn:hover {
    background-color: #1d4ed8;
}
QPushButton#primaryBtn:pressed {
    background-color: #1e40af;
}
QPushButton#primaryBtn:disabled {
    background-color: #94a3b8;
    color: #e2e8f0;
}

/* ===== 滚动区域 ===== */
QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    width: 6px;
    background: transparent;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ===== 工具提示 ===== */
QToolTip {
    background-color: #0f172a;
    color: #f8fafc;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""

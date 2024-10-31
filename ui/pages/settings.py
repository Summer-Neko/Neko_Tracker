from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox


class SettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        # 主窗口引用，用于调用保存配置方法
        self.main_window = main_window

        layout = QVBoxLayout()

        # 开机自启动选项
        self.auto_start_checkbox = QCheckBox("开机自启动")
        self.auto_start_checkbox.stateChanged.connect(self.save_settings)  # 连接信号
        layout.addWidget(self.auto_start_checkbox)

        # 关闭后最小化选项
        self.minimize_to_tray_checkbox = QCheckBox("关闭后最小化到托盘")
        self.minimize_to_tray_checkbox.stateChanged.connect(self.save_settings)  # 连接信号
        layout.addWidget(self.minimize_to_tray_checkbox)

        self.setLayout(layout)

    def save_settings(self):
        """调用主窗口的保存设置方法，实现实时保存"""
        self.main_window.save_settings()

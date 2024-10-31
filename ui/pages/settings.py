import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox

from utils.utils import create_shortcut, remove_shortcut, get_startup_folder


class SettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        # 主窗口引用，用于调用保存配置方法
        self.main_window = main_window

        layout = QVBoxLayout()


        # 开机自启动复选框
        self.auto_start_checkbox = QCheckBox("开机自启动")
        self.auto_start_checkbox.stateChanged.connect(self.toggle_autostart)
        self.auto_start_checkbox.stateChanged.connect(self.save_settings)  # 连接信号
        # 加载当前状态
        self.load_autostart_status()
        layout.addWidget(self.auto_start_checkbox)

        # 关闭后最小化选项
        self.minimize_to_tray_checkbox = QCheckBox("关闭后最小化到托盘")
        self.minimize_to_tray_checkbox.stateChanged.connect(self.save_settings)  # 连接信号
        layout.addWidget(self.minimize_to_tray_checkbox)

        self.setLayout(layout)

    def load_autostart_status(self):
        """检测启动文件夹中是否存在应用快捷方式，并更新复选框状态"""
        shortcut_path = os.path.join(get_startup_folder(), "NekoGame.lnk")
        self.auto_start_checkbox.setChecked(os.path.exists(shortcut_path))

    def toggle_autostart(self, state):
        """根据复选框状态创建或删除快捷方式"""
        if state == 2:  # 2 表示勾选状态
            create_shortcut("NekoGame")  # 创建快捷方式
        else:
            remove_shortcut("NekoGame")  # 删除快捷方式

    def save_settings(self):
        """调用主窗口的保存设置方法，实现实时保存"""
        self.main_window.save_settings()

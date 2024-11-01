import os

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox

from utils.utils import create_vbs_autostart, remove_vbs_autostart


class SettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        # 主窗口引用，用于调用保存配置方法
        self.main_window = main_window

        layout = QVBoxLayout()

        # 无感模式选项
        self.stealth_mode_checkbox = QCheckBox("无感模式（开启时默认进入托盘）")
        self.stealth_mode_checkbox.stateChanged.connect(self.save_settings)
        layout.addWidget(self.stealth_mode_checkbox)


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
        """检查启动文件夹中是否存在 VBS 自启动脚本，并更新复选框状态"""
        startup_folder = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
        vbs_path = os.path.join(startup_folder, "MyApp.vbs")
        self.auto_start_checkbox.setChecked(os.path.exists(vbs_path))

    def toggle_autostart(self, state):
        """根据复选框状态创建或删除 VBS 自启动脚本"""
        if state == 2:  # 勾选状态
            create_vbs_autostart("NekoGame")
        else:
            remove_vbs_autostart("NekoGame")

    def save_settings(self):
        """调用主窗口的保存设置方法，实现实时保存"""
        self.main_window.save_settings()

# main_window.py
import os
import json
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QHBoxLayout, QSystemTrayIcon
from PyQt6.QtCore import Qt
from ui.pages.home import HomePage
from ui.pages.game_manager import GameManagerPage
from ui.pages.settings import SettingsPage
from tray.tray_icon import TrayIcon


class MainWindow(QMainWindow):
    CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Game Manager")
        self.setGeometry(100, 100, 800, 600)

        # 加载样式文件
        with open("resources/styles/main.qss", "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        # 主窗口布局
        main_layout = QHBoxLayout()

        # 侧边栏
        sidebar = QVBoxLayout()
        self.home_button = self.create_sidebar_button("主页")
        self.game_manager_button = self.create_sidebar_button("游戏管理")
        self.settings_button = self.create_sidebar_button("设置")

        sidebar.addWidget(self.home_button)
        sidebar.addWidget(self.game_manager_button)
        sidebar.addWidget(self.settings_button)
        sidebar.addStretch()

        # 页面区域
        self.pages = QStackedWidget()

        # 添加页面并记录索引
        self.home_page = HomePage()
        self.game_manager_page = GameManagerPage()
        self.settings_page = SettingsPage(self)  # 传入主窗口引用

        self.pages.addWidget(self.home_page)  # Index 0 - 主页
        self.pages.addWidget(self.game_manager_page)  # Index 1 - 游戏管理
        self.pages.addWidget(self.settings_page)  # Index 2 - 设置

        # 将布局添加到窗口
        container = QWidget()
        main_layout.addLayout(sidebar, 1)
        main_layout.addWidget(self.pages, 3)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 设置默认显示主页
        self.pages.setCurrentIndex(0)
        self.home_button.setChecked(True)

        # 初始化托盘图标
        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()

        # 加载配置
        self.load_settings()

    def create_sidebar_button(self, text):
        button = QPushButton(text)
        button.setCheckable(True)
        button.setObjectName("sidebarButton")
        button.clicked.connect(lambda: self.on_button_click(button))
        return button

    def on_button_click(self, button):
        # 设置按钮状态
        self.home_button.setChecked(button == self.home_button)
        self.game_manager_button.setChecked(button == self.game_manager_button)
        self.settings_button.setChecked(button == self.settings_button)

        # 切换页面，根据按钮设置 QStackedWidget 的页面索引
        page_index = {
            self.home_button: 0,
            self.game_manager_button: 1,
            self.settings_button: 2
        }.get(button, 0)
        self.pages.setCurrentIndex(page_index)

    # 重写关闭事件，实现关闭最小化功能
    def closeEvent(self, event):
        if self.settings_page.minimize_to_tray_checkbox.isChecked():
            event.ignore()  # 忽略关闭事件
            self.hide()  # 隐藏窗口
            self.tray_icon.showMessage(
                "My Game Manager",
                "已最小化到托盘，右键托盘图标退出。",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            event.accept()  # 正常关闭应用

    # 持久化保存设置
    def save_settings(self):
        settings = {
            "auto_start": self.settings_page.auto_start_checkbox.isChecked(),
            "minimize_to_tray": self.settings_page.minimize_to_tray_checkbox.isChecked()
        }
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(settings, f)

    # 加载设置
    def load_settings(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as f:
                settings = json.load(f)
                self.settings_page.auto_start_checkbox.setChecked(settings.get("auto_start", False))
                self.settings_page.minimize_to_tray_checkbox.setChecked(settings.get("minimize_to_tray", False))

import os
import json
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QHBoxLayout, \
    QSystemTrayIcon, QScrollArea
from PyQt6.QtCore import Qt
from database import get_latest_game
from game_tracker import GameTracker
from ui.pages.game_dialog import GameDialog
from ui.pages.home import HomePage
from ui.pages.game_manager import GameManagerPage
from ui.pages.settings import SettingsPage
from tray.tray_icon import TrayIcon
from utils.utils import resource_path, app_root_path


class MainWindow(QMainWindow):
    CONFIG_FILE = app_root_path("config.json")

    def __init__(self):
        super().__init__()

        # 初始化追踪器和托盘图标
        self.tracker = GameTracker()
        self.tracker.initialize_tracking()
        self.tracker.game_status_updated.connect(self.refresh_home_page)

        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()

        # 设置主窗口属性
        self.setWindowTitle("Neko Games")
        self.setGeometry(100, 100, 1000, 600)

        qss_path = resource_path("resources/styles/main.qss")
        # 加载样式
        with open(qss_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())



        # 主布局
        main_layout = QHBoxLayout()
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)

        # 左侧栏内容
        sidebar_content = QWidget()
        sidebar_layout = QVBoxLayout()
        self.home_button = self.create_sidebar_button("主页")
        self.game_manager_button = self.create_sidebar_button("游戏管理")
        self.settings_button = self.create_sidebar_button("设置")
        sidebar_layout.addWidget(self.home_button)
        sidebar_layout.addWidget(self.game_manager_button)
        sidebar_layout.addWidget(self.settings_button)
        sidebar_layout.addStretch()
        sidebar_content.setLayout(sidebar_layout)
        sidebar_scroll.setWidget(sidebar_content)
        main_layout.addWidget(sidebar_scroll, 1)

        # 中央内容区域
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        self.pages = QStackedWidget()
        self.home_page = HomePage()
        self.game_manager_page = GameManagerPage()
        self.settings_page = SettingsPage(self)
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.game_manager_page)
        self.pages.addWidget(self.settings_page)
        right_scroll.setWidget(self.pages)
        main_layout.addWidget(right_scroll, 3)

        # 设置主窗口布局
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 默认显示主页
        self.pages.setCurrentIndex(0)
        self.home_button.setChecked(True)

        # 加载设置
        self.load_settings()

        # 设置对话框信号
        self.dialog = GameDialog()
        self.dialog.game_saved.connect(self.add_game_to_tracker)

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

        # 切换页面
        page_index = {
            self.home_button: 0,
            self.game_manager_button: 1,
            self.settings_button: 2
        }.get(button, 0)
        self.pages.setCurrentIndex(page_index)

    def closeEvent(self, event):
        """重写关闭事件，实现最小化到托盘功能"""
        if self.settings_page.minimize_to_tray_checkbox.isChecked():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "My Game Manager",
                "已最小化到托盘，右键托盘图标退出。",
                QSystemTrayIcon.MessageIcon.Information,
                1000
            )
        else:
            event.accept()

    def save_settings(self):
        """持久化保存设置到配置文件"""
        settings = {
            "auto_start": self.settings_page.auto_start_checkbox.isChecked(),
            "minimize_to_tray": self.settings_page.minimize_to_tray_checkbox.isChecked()
        }
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        """加载持久化设置"""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as f:
                settings = json.load(f)
                self.settings_page.auto_start_checkbox.setChecked(settings.get("auto_start", False))
                self.settings_page.minimize_to_tray_checkbox.setChecked(settings.get("minimize_to_tray", False))

    def add_game_to_tracker(self):
        """在添加或编辑游戏后，将新游戏添加到检测列表中"""
        game = get_latest_game()
        if game:
            game_id = game[0]
            exe_filename = game[3]
            self.tracker.add_game_to_tracking(game_id, exe_filename)

        # 立即刷新主页，确保新游戏可见
        self.refresh_home_page()

    def refresh_home_page(self):
        """刷新主页内容"""
        self.home_page.load_games()

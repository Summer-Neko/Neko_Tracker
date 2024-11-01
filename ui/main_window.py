import os
import json
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QHBoxLayout, \
    QSystemTrayIcon, QScrollArea, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from database import get_latest_game
from game_tracker import GameTracker
from ui.pages.game_details import GameDetails
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
        # 初始设置窗口为隐藏状态，防止一启动就显示
        self.hide()
        # 设置主窗口初始为隐藏，以便在无感模式下不会闪现
        self.setWindowTitle("Neko Games")
        self.setGeometry(100, 100, 1000, 600)

        # 初始化托盘图标
        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()


        # 设置主窗口样式
        qss_path = resource_path("resources/styles/main.qss")
        with open(qss_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        # 主布局
        main_layout = QHBoxLayout()
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)

        # 创建详情页面占位
        self.game_details_page = None

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

        # 加载设置并检查无感模式
        self.load_settings()
        if not self.stealth_mode_enabled:
            self.show()  # 仅当未启用无感模式时显示窗口


        # 设置主窗口布局
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 监听主页的游戏选择信号
        self.home_page.game_selected.connect(self.show_game_details)

        # 默认显示主页
        self.pages.setCurrentIndex(0)
        self.home_button.setChecked(True)

        # 设置对话框信号
        self.dialog = GameDialog()
        self.dialog.game_saved.connect(self.add_game_to_tracker)

        # 初始化页面切换动画
        self.setup_animation()

        # 启动主页动画
        self.start_home_animation()


    def setup_animation(self):
        """设置页面切换的浮现动画"""
        # 设置透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self.pages)
        self.pages.setGraphicsEffect(self.opacity_effect)

        # 设置动画，控制透明度从 0 到 1
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)  # 动画持续时间，单位为毫秒
        self.animation.setStartValue(0)  # 动画开始值
        self.animation.setEndValue(1)    # 动画结束值
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)  # 动画曲线

    def start_home_animation(self):
        """应用启动时启动主页的淡入动画"""
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def show_home_page(self):
        """切换回主页页面"""
        self.pages.setCurrentWidget(self.home_page)

    def show_game_details(self, game_id, game_name, game_icon, poster_horizontal):
        """切换到游戏详情页面并显示游戏信息"""
        if self.game_details_page:
            self.pages.removeWidget(self.game_details_page)
            self.game_details_page.deleteLater()

        self.game_details_page = GameDetails(game_id, game_name, game_icon, poster_horizontal)
        self.game_details_page.go_back_signal.connect(self.show_home_page)  # 连接返回主页信号
        self.pages.addWidget(self.game_details_page)
        self.pages.setCurrentWidget(self.game_details_page)

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

        # 启动淡入动画
        self.animation.start()

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
        """保存所有设置到配置文件"""
        settings = {
            "stealth_mode": self.settings_page.stealth_mode_checkbox.isChecked(),
            "auto_start": self.settings_page.auto_start_checkbox.isChecked(),
            "minimize_to_tray": self.settings_page.minimize_to_tray_checkbox.isChecked()
        }
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        """加载设置并初始化复选框状态"""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as f:
                settings = json.load(f)
                self.stealth_mode_enabled = settings.get("stealth_mode", False)
                self.settings_page.stealth_mode_checkbox.setChecked(self.stealth_mode_enabled)
                self.settings_page.auto_start_checkbox.setChecked(settings.get("auto_start", False))
                self.settings_page.minimize_to_tray_checkbox.setChecked(settings.get("minimize_to_tray", False))
        else:
            self.stealth_mode_enabled = False  # 默认关闭无感模式

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

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置托盘图标
        self.setIcon(QIcon("resources/icons/app_icon.png"))
        self.setToolTip("My Game Manager")

        # 创建菜单
        tray_menu = QMenu(parent)

        # 退出菜单项
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(QApplication.quit)  # 确保完全退出应用
        tray_menu.addAction(exit_action)

        # 将菜单添加到托盘图标
        self.setContextMenu(tray_menu)

        # 托盘图标点击事件
        self.activated.connect(self.on_tray_icon_clicked)

    def on_tray_icon_clicked(self, reason):
        # 单击恢复窗口
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.parent().isHidden():
                self.parent().show()  # 显示主窗口
            else:
                self.parent().hide()  # 隐藏主窗口

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction

class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon("resources/icons/app_icon.png"))
        self.setToolTip("My Game Manager")
        tray_menu = QMenu(parent)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(exit_action)
        self.setContextMenu(tray_menu)
        self.activated.connect(self.on_tray_icon_clicked)

    def on_tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.parent().isHidden():
                self.parent().show()
            else:
                self.parent().hide()

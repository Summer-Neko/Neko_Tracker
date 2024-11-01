from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QGuiApplication
from PyQt6.QtWidgets import QApplication, QMessageBox

from database import init_db
from ui.main_window import MainWindow
import sys

from utils.utils import resource_path, is_already_running

# 检测单实例
if is_already_running():
    app = QApplication(sys.argv)
    QMessageBox.warning(None, "提示", "应用已在运行。")
    sys.exit(0)


def main():

    init_db()  # 初始化数据库
    app = QApplication([])

    # 启用高 DPI 支持
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app.setWindowIcon(QIcon(resource_path("resources/icons/app_icon.png")))
    main_window = MainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

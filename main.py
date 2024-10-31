from PyQt6.QtGui import QIcon
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
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("resources/icons/app_icon.png")))
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

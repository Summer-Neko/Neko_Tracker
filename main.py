from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from database import init_db
from ui.main_window import MainWindow
import sys

from utils.utils import resource_path


def main():

    init_db()  # 初始化数据库
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("resources/icons/app_icon.png")))
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

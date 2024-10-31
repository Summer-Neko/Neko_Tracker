# ui/pages/home.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("主页内容")  # 添加内容到主页
        layout.addWidget(label)
        self.setLayout(layout)

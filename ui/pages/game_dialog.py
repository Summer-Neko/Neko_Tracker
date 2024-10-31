import os

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QSizePolicy, QMessageBox
from database import add_game, update_game, get_game, check_duplicate_exe
from utils.utils import resource_path


class GameDialog(QDialog):

    # 添加信号用于刷新主页内容
    game_saved = pyqtSignal()
    def __init__(self, game_id=None):
        super().__init__()

        # 加载样式文件
        with open(resource_path("resources/styles/game_manager.qss"), "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        self.setWindowTitle("添加游戏" if game_id is None else "编辑游戏")
        self.setFixedSize(500, 450)

        self.game_id = game_id
        self.icon_path = None
        self.poster_vertical_path = None
        self.poster_horizontal_path = None
        self.exe_filename = None

        # 主布局
        layout = QVBoxLayout()

        # 游戏名称
        layout.addWidget(QLabel("游戏名称"))
        self.name_input = QLineEdit()
        self.name_input.setFixedHeight(30)
        layout.addWidget(self.name_input)

        # 选择游戏图标
        layout.addWidget(QLabel("游戏图标路径"))
        self.icon_button = QPushButton("选择图标")
        self.icon_button.clicked.connect(self.choose_icon)
        layout.addWidget(self.icon_button)
        self.icon_path_label = QLabel("未选择文件")
        self.icon_path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.icon_path_label)

        # 选择竖向海报
        layout.addWidget(QLabel("竖向海报路径"))
        self.vertical_button = QPushButton("选择竖向海报")
        self.vertical_button.clicked.connect(self.choose_vertical_poster)
        layout.addWidget(self.vertical_button)
        self.vertical_path_label = QLabel("未选择文件")
        self.vertical_path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.vertical_path_label)

        # 选择横向海报
        layout.addWidget(QLabel("横向海报路径"))
        self.horizontal_button = QPushButton("选择横向海报")
        self.horizontal_button.clicked.connect(self.choose_horizontal_poster)
        layout.addWidget(self.horizontal_button)
        self.horizontal_path_label = QLabel("未选择文件")
        self.horizontal_path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.horizontal_path_label)

        # 应用程序文件路径
        layout.addWidget(QLabel("可执行文件路径"))
        self.exe_button = QPushButton("选择exe文件")
        self.exe_button.clicked.connect(self.choose_exe)
        layout.addWidget(self.exe_button)
        self.exe_path_label = QLabel("未选择文件")
        self.exe_path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.exe_path_label)

        # 总时长（只读）
        self.total_duration_label = QLabel("总时长: 0 秒")
        layout.addWidget(self.total_duration_label)

        # 保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_game)
        save_button.setFixedHeight(35)
        layout.addWidget(save_button)

        # 如果是编辑模式，加载现有数据
        if self.game_id:
            self.load_game_data()

        self.setLayout(layout)

    def choose_icon(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择图标", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.icon_path = path
            self.icon_path_label.setText(path)

    def choose_vertical_poster(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择竖向海报", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.poster_vertical_path = path
            self.vertical_path_label.setText(path)

    def choose_horizontal_poster(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择横向海报", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.poster_horizontal_path = path
            self.horizontal_path_label.setText(path)

    def choose_exe(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择exe文件", "", "Executable Files (*.exe)")
        if path:
            # 仅保存文件名，而非完整路径
            self.exe_filename = os.path.basename(path)
            self.exe_path_label.setText(self.exe_filename)

    def load_game_data(self):
        game = get_game(self.game_id)
        self.name_input.setText(game[1])  # 游戏名称
        self.icon_path = game[2] if game[2] else ""
        self.exe_filename = game[3] if game[3] else ""
        self.poster_vertical_path = game[4] if game[4] else ""
        self.poster_horizontal_path = game[5] if game[5] else ""

        # 显示总时长
        self.total_duration_label.setText(f"总时长: {game[6]} 秒")

        # 更新路径显示
        self.icon_path_label.setText(self.icon_path if self.icon_path else "未选择文件")
        self.exe_path_label.setText(self.exe_filename if self.exe_filename else "未选择文件")
        self.vertical_path_label.setText(self.poster_vertical_path if self.poster_vertical_path else "未选择文件")
        self.horizontal_path_label.setText(self.poster_horizontal_path if self.poster_horizontal_path else "未选择文件")

    def save_game(self):
        try:
            name = self.name_input.text()
            icon_path = self.icon_path if self.icon_path else ""
            exe_filename = self.exe_filename if self.exe_filename else ""
            poster_vertical = self.poster_vertical_path if self.poster_vertical_path else ""
            poster_horizontal = self.poster_horizontal_path if self.poster_horizontal_path else ""

            # 检查重复的 exe_filename
            if check_duplicate_exe(exe_filename) and not self.game_id:
                QMessageBox.warning(self, "重复的文件", "已存在相同的可执行文件名，无法添加重复的游戏。")
                return  # 阻止添加

            # 更新或添加游戏信息
            if self.game_id:
                update_game(self.game_id, name, icon_path, exe_filename, poster_vertical, poster_horizontal)
            else:
                add_game(name, icon_path, exe_filename, poster_vertical, poster_horizontal)

            self.accept()
            self.game_saved.emit()  # 触发信号通知主页刷新
        except Exception as e:
            print(f"Error saving game: {e}")

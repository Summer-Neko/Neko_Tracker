from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QGridLayout, QDialog, \
    QMenu
from PyQt6.QtGui import QPixmap, QAction, QImage
from PyQt6.QtCore import Qt, QPoint
from database import add_game, get_games, get_game, delete_game
from ui.pages.game_dialog import GameDialog
from utils.utils import resource_path


class GameManagerPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("GameManagerPage")

        # 加载专属样式文件
        with open(resource_path("resources/styles/game_manager.qss"), "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())


        # 主布局
        main_layout = QVBoxLayout()

        # 顶部布局，包含“添加游戏”按钮
        top_layout = QHBoxLayout()
        top_layout.addStretch()  # 占位使按钮居右
        self.add_game_button = QPushButton("添加游戏")
        self.add_game_button.setObjectName("add_game_button")  # 匹配 QSS 样式
        self.add_game_button.clicked.connect(self.open_add_game_dialog)
        top_layout.addWidget(self.add_game_button)
        main_layout.addLayout(top_layout)

        # 游戏卡片区域布局
        self.grid_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout)
        self.setLayout(main_layout)

        # 加载游戏列表
        self.load_games()

    def load_games(self):
        # 清除现有游戏卡片
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        games = get_games()

        if games:
            for index, game in enumerate(games):
                card = self.create_game_card(game)
                row = index // 4  # 每行显示4个卡片
                col = index % 4
                self.grid_layout.addWidget(card, row, col)
        else:
            no_games_label = QLabel("目前没有游戏")
            no_games_label.setObjectName("no_games_label")
            self.grid_layout.addWidget(no_games_label, 0, 0, 1, 4)

    def create_game_card(self, game):
        card_widget = QWidget()
        card_widget.setFixedSize(150, 250)
        card_widget.setObjectName("game_card")
        card_layout = QVBoxLayout()

        # 使用高质量缩放模式显示图片
        poster_label = QLabel()
        poster_label.setObjectName("poster_label")
        image = QImage(game[4]) if game[4] else QImage(resource_path("resources/images/default_vertical.png"))
        scaled_image = image.scaled(150, 200, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        poster_label.setPixmap(QPixmap.fromImage(scaled_image))

        # 卡片布局
        name_menu_layout = QHBoxLayout()
        name_label = QLabel(game[1])
        name_label.setObjectName("game_name_label")
        name_menu_layout.addWidget(name_label)

        menu_button = QPushButton("...")
        menu_button.setObjectName("menu_button")
        menu_button.setFixedSize(24, 24)
        menu_button.clicked.connect(lambda _, game_id=game[0]: self.show_menu(menu_button, game_id, game[1]))
        name_menu_layout.addWidget(menu_button, alignment=Qt.AlignmentFlag.AlignRight)

        # 组合布局
        card_layout.addWidget(poster_label)
        card_layout.addLayout(name_menu_layout)
        card_widget.setLayout(card_layout)

        return card_widget

    def show_menu(self, button, game_id, game_name):
        # 创建下拉菜单
        menu = QMenu()
        edit_action = QAction("编辑游戏信息", self)
        edit_action.triggered.connect(lambda: self.open_edit_game_dialog(game_id))
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.delete_game(game_id))
        menu.addAction(edit_action)
        menu.addAction(delete_action)
        menu.exec(button.mapToGlobal(QPoint(0, button.height())))

    def open_add_game_dialog(self):
        dialog = GameDialog()
        dialog.exec()
        self.load_games()  # 更新列表

    def open_edit_game_dialog(self, game_id):
        dialog = GameDialog(game_id)
        dialog.exec()
        self.load_games()  # 更新列表

    def delete_game(self, game_id):
        delete_game(game_id)
        self.load_games()

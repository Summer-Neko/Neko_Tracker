from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from database import get_games, get_game_duration_today, get_game_duration_last_2_weeks
from utils.process_utils import is_game_running
from utils.utils import resource_path


class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        # 主布局
        layout = QVBoxLayout()
        self.game_list = QListWidget()
        layout.addWidget(self.game_list)
        self.setLayout(layout)

        with open(resource_path("resources/styles/home.qss"), "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        # 监听保存游戏信号
        self.load_games()

    def load_games(self):
        games = get_games()
        self.game_list.clear()

        # 计算所有游戏中近两周的最大时长，默认值设为 0
        max_recent_duration = max((get_game_duration_last_2_weeks(game[0]) for game in games), default=0)

        for game in games:
            item_widget = self.create_game_card(game, max_recent_duration)
            item = QListWidgetItem(self.game_list)
            item.setSizeHint(item_widget.sizeHint())
            self.game_list.addItem(item)
            self.game_list.setItemWidget(item, item_widget)

    def create_game_card(self, game, max_recent_duration):
        card_widget = QWidget()
        card_layout = QHBoxLayout()

        # 游戏海报
        poster_label = QLabel()
        poster_pixmap = QPixmap(game[5]) if game[5] else QPixmap(resource_path("resources/images/default_horizontal.png"))
        poster_label.setPixmap(poster_pixmap.scaled(150, 90, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                    Qt.TransformationMode.SmoothTransformation))
        card_layout.addWidget(poster_label)

        # 游戏信息区域
        info_layout = QVBoxLayout()

        # 游戏名称
        name_label = QLabel(game[1])
        name_label.setObjectName("game_name_label")
        info_layout.addWidget(name_label)

        # 总时长和近两周时长
        total_duration = get_game_duration_today(game[0])
        recent_duration = get_game_duration_last_2_weeks(game[0])

        total_time_label = QLabel(f"总时长: {total_duration} h")
        recent_time_label = QLabel(f"近两周: {recent_duration} h")
        info_layout.addWidget(total_time_label)
        info_layout.addWidget(recent_time_label)

        # 进度条显示近两周时长占最大时长的比例
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(1000)  # 设为 1000 表示 100%

        # 计算进度百分比并按比例设置进度条
        percent = int((recent_duration / max_recent_duration) * 1000) if max_recent_duration > 0 else 0
        progress_bar.setValue(percent)

        # 显示百分比
        info_layout.addWidget(progress_bar)

        # 游戏运行状态标记
        running = is_game_running(game[3])
        if running:
            running_label = QLabel("运行中")
            running_label.setObjectName("running_label")
            info_layout.addWidget(running_label)

        card_layout.addLayout(info_layout)
        card_widget.setLayout(card_layout)

        return card_widget

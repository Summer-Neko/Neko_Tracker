from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal
from database import get_games, get_game_duration_today, get_game_duration_last_2_weeks
from utils.process_utils import is_game_running
from utils.utils import resource_path

class HomePage(QWidget):
    game_selected = pyqtSignal(int, str, str, str)  # 信号传递游戏ID、名称、图标、横向海报

    def __init__(self):
        super().__init__()

        # 主布局
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(15)
        self.setLayout(self.layout)

        # 加载样式
        with open(resource_path("resources/styles/home.qss"), "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        # 加载游戏列表
        self.load_games()

    def load_games(self):
        games = get_games()
        self.clear_layout()

        # 如果没有游戏，显示提示信息
        if not games:
            no_games_label = QLabel("请先添加游戏")
            no_games_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(no_games_label)
            return

        # 计算所有游戏中近两周的最大时长
        max_recent_duration = max((get_game_duration_last_2_weeks(game[0]) for game in games), default=0)

        # 遍历游戏列表并创建每个游戏的卡片
        for game in games:
            card_widget = self.create_game_card(game, max_recent_duration)
            card_widget.mousePressEvent = lambda event, g=game: self.on_game_card_clicked(g)
            self.layout.addWidget(card_widget)

    def on_game_card_clicked(self, game):
        """游戏卡片点击事件处理，发射信号到主窗口"""
        game_id = game[0]
        game_name = game[1]
        game_icon = game[2]
        poster_horizontal = game[5]
        self.game_selected.emit(game_id, game_name, game_icon, poster_horizontal)

    def create_game_card(self, game, max_recent_duration):
        card_widget = QWidget()
        card_layout = QHBoxLayout()
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(10)

        # 游戏海报
        poster_label = QLabel()
        poster_pixmap = QPixmap(game[5]) if game[5] else QPixmap(resource_path("resources/images/default_horizontal.png"))
        poster_label.setPixmap(poster_pixmap.scaled(150, 90, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                    Qt.TransformationMode.SmoothTransformation))
        card_layout.addWidget(poster_label)

        # 游戏信息区域
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)

        # 游戏名称
        name_label = QLabel(game[1])
        name_label.setObjectName("game_name_label")
        info_layout.addWidget(name_label)

        # 总时长和近两周时长
        total_duration = get_game_duration_today(game[0])
        recent_duration = get_game_duration_last_2_weeks(game[0])

        total_time_label = QLabel(f"总时长: {total_duration} h")
        recent_time_label = QLabel(f"近两周: {recent_duration} h")
        recent_time_label.setObjectName("recent_time_label")
        total_time_label.setObjectName("total_time_label")
        info_layout.addWidget(total_time_label)
        info_layout.addWidget(recent_time_label)

        # 进度条显示近两周时长占最大时长的比例
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(1000)
        percent = int((recent_duration / max_recent_duration) * 1000) if max_recent_duration > 0 else 0
        progress_bar.setValue(percent)
        info_layout.addWidget(progress_bar)

        card_layout.addLayout(info_layout)

        # 添加“运行中”标签到卡片的最右侧
        running = is_game_running(game[3])
        if running:
            running_label = QLabel("运行中")
            running_label.setObjectName("running_label")
            running_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            card_layout.addWidget(running_label)

        card_widget.setLayout(card_layout)
        card_widget.setObjectName("game_card")
        return card_widget

    def clear_layout(self):
        """清除布局中的所有小部件"""
        while self.layout.count():
            widget = self.layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()

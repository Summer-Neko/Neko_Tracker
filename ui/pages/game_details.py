import numpy as np
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout, QPushButton, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from database import get_game_sessions, get_game_duration_last_2_weeks, get_last_play_time, get_game_duration_today
from utils.utils import resource_path
from utils.process_utils import is_game_running

class GameDetails(QWidget):
    go_back_signal = pyqtSignal()  # 定义返回主页的信号

    def __init__(self, game_id, game_name, game_icon, poster_horizontal):
        super().__init__()
        self.game_id = game_id
        self.game_name = game_name

        # 主布局
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        # 顶部信息区域
        self.setup_top_section(game_name, game_icon, poster_horizontal)

        # 趋势分析图表区域
        self.setup_trend_section()

        # 添加回主页按钮
        self.add_back_button()

    def setup_top_section(self, game_name, game_icon, poster_horizontal):
        """设置页面上部的基本信息区域"""

        top_layout = QVBoxLayout()

        # 游戏横向海报
        poster_label = QLabel()
        poster_pixmap = QPixmap(poster_horizontal if poster_horizontal else resource_path("resources/images/default_horizontal.png"))
        poster_label.setPixmap(poster_pixmap.scaled(500, 150, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        top_layout.addWidget(poster_label)

        # 游戏信息布局
        info_layout = QHBoxLayout()

        # 游戏图标
        icon_label = QLabel()
        icon_pixmap = QPixmap(game_icon if game_icon else resource_path("resources/images/default_icon.png"))
        icon_label.setPixmap(icon_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        info_layout.addWidget(icon_label)

        # 名称与时长信息
        details_layout = QVBoxLayout()
        name_label = QLabel(f"{game_name}")
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        name_label.setObjectName("game_name_label")
        details_layout.addWidget(name_label)

        # 游戏状态与时长显示
        total_duration_label = QLabel(f"两周内总时长: {get_game_duration_last_2_weeks(self.game_id)} h")
        today_duration_label = QLabel(f"今日时长: {get_game_duration_today(self.game_id)} h")
        last_play_label = QLabel(f"最后运行时间: {get_last_play_time(self.game_id)}")
        details_layout.addWidget(total_duration_label)
        details_layout.addWidget(today_duration_label)
        details_layout.addWidget(last_play_label)

        # 添加成就进度条（可选功能）
        progress_bar = QProgressBar()
        progress_bar.setValue(80)  # 示例成就进度
        details_layout.addWidget(progress_bar)

        # 运行状态显示
        running = is_game_running(self.game_name)
        running_label = QLabel("运行中" if running else "未运行")
        running_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        details_layout.addWidget(running_label)

        info_layout.addLayout(details_layout)
        top_layout.addLayout(info_layout)
        self.layout.addLayout(top_layout)

    def setup_trend_section(self):
        """设置页面的下部图表展示区域"""

        trend_layout = QVBoxLayout()

        # 下拉选择查看具体天数
        day_selector = QComboBox()
        day_selector.addItems(["Last 7 Days", "Last 14 Days", "Last 30 Days"])  # 使用英文替换汉字
        day_selector.currentIndexChanged.connect(self.plot_trend)  # 选择项更改后重新绘制图表
        trend_layout.addWidget(day_selector)

        # 添加条形图展示
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        trend_layout.addWidget(self.canvas)
        self.plot_trend()  # 绘制条形图

        self.layout.addLayout(trend_layout)

    import numpy as np

    def plot_trend(self):
        """绘制趋势图（条形图）"""
        # 获取近两周的游戏时长数据
        data = get_game_sessions(self.game_id)
        dates = [d["date"] for d in data]
        durations = [d["duration"] for d in data]

        # 绘图
        ax = self.canvas.figure.subplots()
        ax.clear()
        ax.bar(dates, durations, color="#87CEFA")
        ax.set_title("Daily Playtime Trend (Last 2 Weeks)")  # 使用英文标题
        ax.set_xlabel("Date")
        ax.set_ylabel("Hours")

        # 自适应纵坐标上限和刻度
        max_duration = max(durations) if durations else 1  # 确保最大值至少为1，避免空数据时除以0
        ax.set_ylim(0, max_duration + max_duration / 4)  # 将纵坐标上限设置为最大值的1.25倍

        # 设置动态刻度，以最大数据的四分之一为间隔
        tick_interval = max(1, max_duration / 4)  # 确保间隔至少为1
        ax.yaxis.set_ticks(np.arange(0, max_duration + tick_interval, tick_interval))

        # 绘制图表
        self.canvas.draw()

    def add_back_button(self):
        """添加返回主页按钮"""
        back_button = QPushButton("返回主页")
        back_button.clicked.connect(self.go_back)  # 连接点击事件
        self.layout.addWidget(back_button)

    def go_back(self):
        """发射返回主页的信号"""
        self.go_back_signal.emit()

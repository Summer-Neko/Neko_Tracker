from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class GameDetailPage(QWidget):
    def __init__(self, game_id):
        super().__init__()
        self.game_id = game_id
        layout = QVBoxLayout()

        # 总时长统计
        total_time_label = QLabel(f"总游戏时长: {self.calculate_total_play_time()}")

        # 每天游戏时长条形图
        self.plot_daily_play_time()

        layout.addWidget(total_time_label)
        self.setLayout(layout)

    def plot_daily_play_time(self):
        """绘制每天游戏时长条形图"""
        # 使用 matplotlib 绘制条形图
        # 获取 session_logs 数据并生成图表...

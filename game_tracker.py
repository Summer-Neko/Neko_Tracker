from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from datetime import datetime, timedelta
from database import add_game_session, update_game_session, update_game_duration, get_latest_session, get_games
from utils.process_utils import is_game_running

class GameTracker(QObject):
    game_status_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.tracked_games = {}  # 存储正在追踪的游戏信息
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_games_status)
        self.timer.start(6000)  # 每60秒更新一次

    def initialize_tracking(self):
        games = get_games()
        for game in games:
            self.tracked_games[game[0]] = {
                "exe_filename": game[3],
                "is_running": False,
                "start_time": None
            }

    def check_games_status(self):
        current_time = datetime.now()
        for game_id, game_info in self.tracked_games.items():
            exe_filename = game_info["exe_filename"]
            is_running = is_game_running(exe_filename)

            if is_running and not game_info["is_running"]:
                # 游戏刚开始运行，记录开始时间
                game_info["start_time"] = current_time
                add_game_session(game_id, current_time)
                game_info["is_running"] = True

            elif is_running and game_info["is_running"]:
                # 游戏持续运行，每次更新时长和结束时间
                start_time = game_info["start_time"]
                if start_time:
                    elapsed = (current_time - start_time).total_seconds()
                    update_game_duration(game_id, elapsed)

                    # 更新会话的结束时间
                    session = get_latest_session(game_id)
                    if session and session["end_time"] is None:
                        update_game_session(session["id"], current_time)

            elif not is_running and game_info["is_running"]:
                # 游戏结束，记录结束时间并更新时长
                session = get_latest_session(game_id)
                if session and session["end_time"] is None:
                    end_time = current_time
                    update_game_session(session["id"], end_time)
                    elapsed = (end_time - datetime.fromisoformat(session["start_time"])).total_seconds()
                    update_game_duration(game_id, elapsed)
                game_info["is_running"] = False

        # 更新界面
        self.game_status_updated.emit()

    def add_game_to_tracking(self, game_id, exe_filename):
        self.tracked_games[game_id] = {
            "exe_filename": exe_filename,
            "is_running": False,
            "start_time": None
        }

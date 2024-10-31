import sqlite3
import os
from datetime import datetime, timedelta

from utils.utils import app_root_path

DB_PATH = app_root_path("games.db")


def init_db():
    """Initialize the SQLite database and create tables if not exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icon TEXT,
            exe_filename TEXT UNIQUE,
            poster_vertical TEXT,
            poster_horizontal TEXT,
            total_duration INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
    ''')
    conn.commit()
    conn.close()


def add_game_session(game_id, start_time):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO game_sessions (game_id, start_time)
        VALUES (?, ?)
    ''', (game_id, start_time.isoformat()))
    conn.commit()
    conn.close()

def update_game_duration(game_id, additional_duration):
    """增加游戏的总时长"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE games
        SET total_duration = total_duration + ?
        WHERE id = ?
    ''', (int(additional_duration), game_id))
    conn.commit()
    conn.close()


def update_game_duration(game_id, duration):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE games
        SET total_duration = total_duration + ?
        WHERE id = ?
    ''', (int(duration), game_id))
    conn.commit()
    conn.close()


def get_game_duration_today(game_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = datetime.now().date()
    cursor.execute('''
        SELECT SUM(
            CASE 
                WHEN end_time IS NOT NULL THEN (julianday(end_time) - julianday(start_time)) * 24 * 60
                ELSE (julianday(?) - julianday(start_time)) * 24 * 60
            END
        ) AS duration
        FROM game_sessions
        WHERE game_id = ? AND date(start_time) = ?
    ''', (datetime.now().isoformat(), game_id, today.isoformat()))
    duration = cursor.fetchone()[0]
    conn.close()
    return round((duration or 0) / 60, 1)  # 返回小时数


def get_game_duration_last_2_weeks(game_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    two_weeks_ago = datetime.now() - timedelta(days=14)
    cursor.execute('''
        SELECT SUM(
            CASE 
                WHEN end_time IS NOT NULL THEN (julianday(end_time) - julianday(start_time)) * 24 * 60
                ELSE (julianday(?) - julianday(start_time)) * 24 * 60
            END
        ) AS duration
        FROM game_sessions
        WHERE game_id = ? AND date(start_time) >= ?
    ''', (datetime.now().isoformat(), game_id, two_weeks_ago.date().isoformat()))
    duration = cursor.fetchone()[0]
    conn.close()
    return round((duration or 0) / 60, 1)  # 返回小时数


def delete_game(game_id):
    """删除游戏和相关的游戏时长记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 删除关联的游戏会话记录
    cursor.execute('DELETE FROM game_sessions WHERE game_id = ?', (game_id,))
    # 删除游戏记录
    cursor.execute('DELETE FROM games WHERE id = ?', (game_id,))
    conn.commit()
    conn.close()



def get_games():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games')
    games = cursor.fetchall()
    conn.close()
    return games

def get_game(game_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games WHERE id = ?', (game_id,))
    game = cursor.fetchone()
    conn.close()
    return game


def add_game(name, icon, exe_filename, poster_vertical, poster_horizontal):
    """添加游戏信息，初始化总时长为0"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO games (name, icon, exe_filename, poster_vertical, poster_horizontal, total_duration)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, icon, exe_filename, poster_vertical, poster_horizontal, 0))
    conn.commit()
    conn.close()

def update_game(game_id, name, icon, exe_filename, poster_vertical, poster_horizontal):
    """更新游戏信息，但保持总时长不变"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 获取当前游戏的总时长
    cursor.execute('SELECT total_duration FROM games WHERE id = ?', (game_id,))
    total_duration = cursor.fetchone()[0]

    # 更新游戏信息，保留总时长字段
    cursor.execute('''
        UPDATE games
        SET name = ?, icon = ?, exe_filename = ?, poster_vertical = ?, poster_horizontal = ?, total_duration = ?
        WHERE id = ?
    ''', (name, icon, exe_filename, poster_vertical, poster_horizontal, total_duration, game_id))
    conn.commit()
    conn.close()


def check_duplicate_exe(exe_filename):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM games WHERE exe_filename = ?', (exe_filename,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def get_latest_session(game_id):
    """获取指定游戏的最近会话记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, start_time, end_time
        FROM game_sessions
        WHERE game_id = ?
        ORDER BY start_time DESC
        LIMIT 1
    ''', (game_id,))
    session = cursor.fetchone()
    conn.close()

    if session:
        return {"id": session[0], "start_time": session[1], "end_time": session[2]}
    return None

def get_latest_game():
    """获取最近添加的游戏信息"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT *
        FROM games
        ORDER BY id DESC
        LIMIT 1
    ''')
    latest_game = cursor.fetchone()
    conn.close()
    return latest_game

def update_game_session(session_id, end_time):
    """更新指定会话的结束时间"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE game_sessions
        SET end_time = ?
        WHERE id = ?
    ''', (end_time.isoformat(), session_id))
    conn.commit()
    conn.close()

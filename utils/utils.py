import os
import sys

import win32com
import win32event
import win32api
import winerror
import win32com.client


def resource_path(relative_path):
    """获取打包后资源文件的路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def app_root_path(filename):
    """获取根目录下的文件路径，用于保存配置文件和数据库"""
    if hasattr(sys, '_MEIPASS'):
        # 在打包运行环境下，将配置文件放在可执行文件的同级目录
        return os.path.join(os.path.dirname(sys.executable), filename)
    # 开发环境下
    return os.path.join(os.path.abspath("."), filename)


mutex_name = "ThisIsUniqueGameNEKO"  # 设置互斥锁名称，确保唯一

def is_already_running():
    """检查是否已有实例在运行"""
    global mutex
    mutex = win32event.CreateMutex(None, False, mutex_name)
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        # 检测到已经有实例运行，返回 True
        return True
    return False


def get_startup_folder():
    """获取当前用户的启动文件夹路径"""
    return os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")

def create_shortcut(app_name="NekoGame", exe_path=None):
    """在启动文件夹中创建应用的快捷方式"""
    if exe_path is None:
        exe_path = sys.executable  # 获取当前应用的可执行文件路径

    # 启动文件夹路径
    shortcut_path = os.path.join(get_startup_folder(), f"{app_name}.lnk")

    try:
        # 创建快捷方式
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.IconLocation = exe_path  # 可选：将应用图标用于快捷方式
        shortcut.save()
    except Exception as e:
        return f"创建快捷方式失败: {e}"


def remove_shortcut(app_name="MyApp"):
    """从启动文件夹中删除应用的快捷方式"""
    startup_folder = get_startup_folder()
    shortcut_path = os.path.join(startup_folder, f"{app_name}.lnk")
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
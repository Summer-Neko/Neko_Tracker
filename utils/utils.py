import os
import sys

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
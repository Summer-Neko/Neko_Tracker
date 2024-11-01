import os


def get_startup_folder():
    """获取当前用户的启动文件夹路径"""
    return os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")

print(get_startup_folder())
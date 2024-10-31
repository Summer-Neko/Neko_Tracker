import psutil

def is_game_running(exe_filename):
    """Check if a game is currently running based on its exe filename."""
    for process in psutil.process_iter(['name']):
        if process.info['name'] == exe_filename:
            return True
    return False

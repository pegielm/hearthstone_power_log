import psutil
import subprocess
import time
import os
import glob

import bg_log_parser

def is_hearthstone_running():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'Hearthstone.exe':
            return True
    return False

def get_latest_folder(directory):
    folders = [f for f in glob.glob(directory + "/*/") if os.path.isdir(f)]
    if not folders:
        return None
    latest_folder = max(folders, key=os.path.getmtime)
    return latest_folder

def find_hearthstone_directory():
    try:
        result = subprocess.run(['where', 'Hearthstone.exe'], capture_output=True, text=True, check=True)
        paths = result.stdout.strip().split('\n')
        if paths:
            # Extract the directory from the full path
            return os.path.dirname(paths[0])
    except subprocess.CalledProcessError:
        print("Hearthstone.exe not found in system PATH. Checking common installation directories.")
    common_dirs = [
        r'C:\Program Files (x86)\Hearthstone',
        r'C:\Program Files\Hearthstone',
        r'C:\Program Files (x86)\Blizzard\Hearthstone',
        r'C:\Program Files\Blizzard\Hearthstone',
        os.path.expandvars(r'%LOCALAPPDATA%\Blizzard\Hearthstone')
    ]
    
    for dir in common_dirs:
        hearthstone_path = os.path.join(dir, 'Hearthstone.exe')
        if os.path.exists(hearthstone_path):
            return dir
    return None


def check_if_game_started(path):
    while True:
        if os.path.exists(path):
            print(f"Game started")
            break
        else:
            print(f"waiting for game to start")
            time.sleep(0.5)

def watch_log_file(path):
    parser = bg_log_parser.parser()

    with open(path, 'r') as file:
        # Move to the end of the file
        file.seek(0, os.SEEK_END)
        current_position = file.tell()
        partial_line = ''
        while True:
            # Seek to the last known position
            file.seek(current_position)
            line = file.readline()
            if not line:
                time.sleep(0.1)  # Wait a bit for new content to be written
                continue
            # Check if the line is complete (ends in a newline character)
            if not line.endswith('\n'):
                partial_line += line  # Store partial line to prepend on the next read
                continue
            # Prepend any stored partial line
            line = partial_line + line
            partial_line = ''  # Reset partial line storage
            current_position = file.tell()  # Update the current position
            parser.parse_line(line)

if __name__ == "__main__":
    while True:
        if is_hearthstone_running():
            print("HEARTHSTONE IS RUNNING")
            path = find_hearthstone_directory()
            if path:
                print(f"path: {path}")
            else:
                print("bad hs dir")
            break
        else:
            print("hearhtstone is not running")
        time.sleep(0.5)  # Wait for 0.5 seconds before checking again
    path = get_latest_folder(path + "\\Logs")
    path = path + "Power.log"
    check_if_game_started(path)
    watch_log_file(path)

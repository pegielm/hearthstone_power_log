import os
import glob
import time
import tkinter as tk
import threading


def watch_log_file(file_path, text_widget):
    with open(file_path, 'r') as file:
        file.seek(0, os.SEEK_END)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
                continue
            text_widget.insert(tk.END, line)
            text_widget.see(tk.END)
            
def get_latest_folder(directory):
    folders = [f for f in glob.glob(directory + "/*/") if os.path.isdir(f)]
    
    if not folders:
        return None
    
    latest_folder = max(folders, key=os.path.getmtime)
    return latest_folder

def start_watching(file_path, text_widget):
    thread = threading.Thread(target=watch_log_file, args=(file_path, text_widget))
    thread.daemon = True
    thread.start()

def create_window(file_path):
    root = tk.Tk()
    root.title("Log Watcher")
    root.geometry("600x400")
    root.attributes('-topmost', True)

    text_widget = tk.Text(root)
    text_widget.pack(expand=True, fill='both')

    start_watching(file_path, text_widget)

    root.mainloop()

if __name__ == "__main__":
    path = 'C:\\Program Files (x86)\\Hearthstone\\Logs'
    path = get_latest_folder(path)
    path = path + "\\Power.log"
    create_window(path)

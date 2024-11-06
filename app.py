from flask import Flask, render_template, jsonify
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time
import os
import json
import pyperclip
from pathlib import Path
import threading

app = Flask(__name__)
with open("config.json") as f:
    config = json.load(f)

watch_folder = Path(config["folder_to_monitor"])
output_folder = Path(config["target_folder_base"])
base_url = config["base_url"]

# 存储转换记录
converted_files = []

def convert_to_avif(input_path, output_path):
    cmd = [
        'ffmpeg', '-i', str(input_path), 
        '-c:v', 'libaom-av1', '-y', str(output_path)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix.lower() in config["valid_extensions"]:
            today_folder = output_folder / time.strftime('%Y-%m-%d')
            today_folder.mkdir(parents=True, exist_ok=True)
            output_file = today_folder / f"{int(time.time())}.avif"

            # 转换图片
            convert_to_avif(file_path, output_file)
            md_link = f"![{output_file.name}]({base_url}/{today_folder.name}/{output_file.name})"
            pyperclip.copy(md_link)
            converted_files.append({
                "filename": output_file.name,
                "md_link": md_link,
                "url": f"{base_url}/{today_folder.name}/{output_file.name}"
            })
            os.remove(file_path)

observer = Observer()

@app.route('/')
def index():
    return render_template("index.html", converted_files=converted_files)

@app.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    event_handler = ImageHandler()
    observer.schedule(event_handler, str(watch_folder), recursive=False)
    observer.start()
    return jsonify({"status": "Monitoring started"})

@app.route('/stop_monitoring', methods=['POST'])
def stop_monitoring():
    observer.stop()
    observer.join()
    return jsonify({"status": "Monitoring stopped"})

if __name__ == "__main__":
    app.run(debug=True)

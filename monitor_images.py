import os
import shutil
import time
import logging
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 加载配置文件
def load_config(config_file='config.json'):
    """加载配置文件"""
    if not os.path.exists(config_file):
        logging.warning(f"配置文件 {config_file} 不存在，使用默认配置。")
        return {}  # 若配置文件不存在，返回空字典，后面会用默认值
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# 获取配置项，若未配置则使用默认值
config = load_config()

# 配置默认值
folder_to_monitor = config.get("folder_to_monitor", r"E:\360MoveData\Users\WIN\Desktop\my-github\my-img\img\Upload")
target_folder_base = config.get("target_folder_base", r"E:\360MoveData\Users\WIN\Desktop\my-github\my-img\img")
valid_extensions = config.get("valid_extensions", [".jpg", ".jpeg", ".png", ".gif", ".avif"])
max_retry_count = config.get("max_retry_count", 3)
domain = config.get("domain", "https://h.xbrooke.cn")
folder_name_format = config.get("folder_name_format", "%Y-%m-%d")
file_name_format = config.get("file_name_format", "%Y%m%d_%H%M%S")

# 配置日志 - 只输出核心信息
logging.basicConfig(level=logging.INFO, format='%(message)s')

# 确保监控文件夹和目标文件夹存在
if not os.path.exists(folder_to_monitor):
    logging.error(f"监控文件夹 {folder_to_monitor} 不存在!")
    exit()

if not os.path.exists(target_folder_base):
    logging.error(f"目标文件夹 {target_folder_base} 不存在!")
    exit()

class ImageHandler(FileSystemEventHandler):
    """处理文件系统事件（新建文件）"""
    def __init__(self, max_retry_count, domain, valid_extensions):
        self.retry_count = max_retry_count
        self.domain = domain
        self.valid_extensions = valid_extensions
    
    def on_created(self, event):
        """当新文件被创建时调用"""
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            _, ext = os.path.splitext(file_name)

            if ext.lower() in self.valid_extensions:
                self.process_file(event.src_path, ext)

    def process_file(self, src_path, ext):
        """处理文件：移动、重命名和生成Markdown链接"""
        # 生成今天的文件夹和新文件名
        today_folder, today = self.get_today_folder()
        timestamp = datetime.now().strftime(file_name_format)
        new_file_name = f"{timestamp}{ext}"
        new_file_path = os.path.join(today_folder, new_file_name)

        # 重试机制
        if not self.retry_file_move(src_path, new_file_path):
            return

        # 生成 Markdown 链接
        markdown_link = f"![{new_file_name}]({self.domain}/img/{today}/{new_file_name})"
        logging.info(f"生成的 Markdown 链接: {markdown_link}")

        # 复制链接到剪贴板
        self.copy_to_clipboard(markdown_link)

    def retry_file_move(self, src_path, new_file_path):
        """尝试移动文件，重试最大次数"""
        for attempt in range(self.retry_count):
            try:
                shutil.move(src_path, new_file_path)
                logging.info(f"文件已移动并重命名为: {new_file_path}")
                return True
            except Exception as e:
                logging.error(f"移动文件时出错: {e} (尝试 {attempt + 1} / {self.retry_count})")
                time.sleep(2)
        logging.error(f"文件移动失败: {new_file_path}, 超过最大重试次数。")
        return False

    def get_today_folder(self):
        """获取今天的文件夹路径，若不存在则创建"""
        today = datetime.now().strftime(folder_name_format)
        today_folder = os.path.join(target_folder_base, today)
        os.makedirs(today_folder, exist_ok=True)
        return today_folder, today

    def copy_to_clipboard(self, text):
        """将文本复制到剪贴板"""
        try:
            import pyperclip
            pyperclip.copy(text)
            logging.info("Markdown链接已复制到剪贴板")
        except Exception as e:
            logging.error(f"复制到剪贴板时出错: {e}")

# 监控文件夹
def start_monitoring():
    logging.info(f"开始监控文件夹: {folder_to_monitor}")

    event_handler = ImageHandler(max_retry_count, domain, valid_extensions)
    observer = Observer(timeout=1)
    observer.schedule(event_handler, folder_to_monitor, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)  # 防止高 CPU 占用
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_monitoring()

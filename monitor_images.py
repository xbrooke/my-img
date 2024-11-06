import os
import shutil
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 设置监控文件夹和目标文件夹
folder_to_monitor = os.path.normpath(r"E:\360MoveData\Users\WIN\Desktop\my-github\my-img\img\Upload")
target_folder_base = os.path.normpath(r"E:\360MoveData\Users\WIN\Desktop\my-github\my-img")

# 确保文件夹存在
if not os.path.exists(folder_to_monitor):
    print(f"监控文件夹 {folder_to_monitor} 不存在!")
    exit()

if not os.path.exists(target_folder_base):
    print(f"目标文件夹 {target_folder_base} 不存在!")
    exit()

# 支持的图片格式
valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.avif'}

class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        # 当新文件被创建时调用
        if not event.is_directory:  # 确保不是文件夹
            file_name = os.path.basename(event.src_path)
            _, ext = os.path.splitext(file_name)

            if ext.lower() in valid_extensions:
                today_folder, today = self.get_today_folder()
                new_file_name = f"{self.get_next_file_number(today_folder)}{ext}"
                new_file_path = os.path.join(today_folder, new_file_name)

                # 移动文件并重命名
                shutil.move(event.src_path, new_file_path)
                print(f"移动文件到: {new_file_path}")

                # 生成 Markdown 链接
                markdown_link = f"![{new_file_name}](https://h.xbrooke.cn/img/{today}/{new_file_name})"
                print(f"Markdown链接: {markdown_link}")

                # 复制链接到剪贴板（可选）
                try:
                    import pyperclip
                except ImportError:
                    os.system('pip install pyperclip')
                    import pyperclip
                
                try:
                    pyperclip.copy(markdown_link)
                    print("Markdown链接已复制到剪贴板")
                except Exception as e:
                    print(f"复制到剪贴板时出错: {e}")

            else:
                print(f"跳过无效图像格式: {file_name}")

    def get_today_folder(self):
        today = datetime.now().strftime("%Y-%m-%d")
        today_folder = os.path.join(target_folder_base, today)
        os.makedirs(today_folder, exist_ok=True)
        return today_folder, today

    def get_next_file_number(self, folder):
        # 获取下一个文件编号
        existing_files = os.listdir(folder)
        existing_numbers = [int(os.path.splitext(f)[0]) for f in existing_files if f.split('.')[0].isdigit()]
        return max(existing_numbers, default=0) + 1  # 返回下一个文件编号

if __name__ == "__main__":
    # 打印监控和目标文件夹路径
    print(f"监控文件夹: {folder_to_monitor}")
    print(f"目标文件夹基础路径: {target_folder_base}")

    event_handler = ImageHandler()
    observer = Observer(timeout=1)  # 添加超时设置
    observer.schedule(event_handler, folder_to_monitor, recursive=False)
    observer.start()
    print(f"开始监控文件夹: {folder_to_monitor}")

    try:
        while True:
            time.sleep(1)  # 防止高 CPU 占用
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

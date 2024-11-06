import os
import shutil
import time
import logging
from pathlib import Path
import pyperclip
import subprocess

# 设置日志级别
logging.basicConfig(level=logging.INFO, format="%(message)s")

# 监控文件夹路径
watch_folder = r'E:\360MoveData\Users\WIN\Desktop\my-github\my-img\img\Upload'
output_folder = r'E:\360MoveData\Users\WIN\Desktop\my-github\my-img\img'  # 确保日期文件夹在这个目录下

# 图片转换函数
def convert_to_avif(input_path: Path, output_path: Path):
    cmd = [
        'ffmpeg', '-i', str(input_path), 
        '-c:v', 'libaom-av1', '-v', '0', '-y', 
        str(output_path)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 获取当天日期文件夹，并确保该文件夹存在
def get_today_folder():
    today = time.strftime('%Y-%m-%d')
    today_folder = Path(output_folder) / today
    today_folder.mkdir(parents=True, exist_ok=True)  # 确保文件夹存在
    return today_folder

# 获取下一个序号
def get_next_file_number(folder: Path):
    existing_files = list(folder.glob('*.avif'))
    existing_numbers = [int(f.stem) for f in existing_files if f.stem.isdigit()]
    return max(existing_numbers, default=0) + 1

# 监控文件夹
def monitor_folder():
    while True:
        for file in Path(watch_folder).glob('*'):
            if file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                logging.info(f"转换中: {file}")
                
                # 获取当前日期文件夹
                today_folder = get_today_folder()  # 获取今天的文件夹
                output_file_number = get_next_file_number(today_folder)  # 获取新的序号
                output_file = today_folder / f"{output_file_number}.avif"  # 新文件的路径
                
                # 执行转换
                convert_to_avif(file, output_file)
                logging.info(f"转换完成: {output_file}")

                # 生成Markdown链接
                md_link = f"![{output_file.name}](https://h.xbrooke.cn/img/{today_folder.name}/{output_file.name})"
                pyperclip.copy(md_link)
                logging.info(f"Markdown链接已复制到剪贴板")

                # 删除原文件
                os.remove(file)
                logging.info(f"原文件已删除: {file}")

        time.sleep(5)

# 启动监控
if __name__ == "__main__":
    logging.info(f"开始监控文件夹: {watch_folder}")
    monitor_folder()

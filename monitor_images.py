import os
import subprocess
import time
import logging
from pathlib import Path
import pyperclip
import json

# 设置日志级别
logging.basicConfig(level=logging.INFO, format="%(message)s")

# 加载配置文件
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()

# 配置参数
watch_folder = config["folder_to_monitor"]
output_folder = config["target_folder_base"]
valid_extensions = config["valid_extensions"]
base_url = config["base_url"]
max_retry_count = config["max_retry_count"]

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

# 自动提交到 GitHub
def git_commit_and_push():
    subprocess.run(['git', 'add', '.'], check=True)  # 添加文件到 Git
    subprocess.run(['git', 'commit', '-m', '自动上传图片并更新Markdown'], check=True)  # 提交
    subprocess.run(['git', 'push', 'origin', 'main'], check=True)  # 推送到远程仓库

# 监控文件夹
def monitor_folder():
    retry_count = 0
    while retry_count < max_retry_count:
        try:
            for file in Path(watch_folder).glob('*'):
                if file.suffix.lower() in valid_extensions:
                    logging.info(f"转换中: {file}")

                    # 获取当前日期文件夹
                    today_folder = get_today_folder()  # 获取今天的文件夹
                    output_file_number = get_next_file_number(today_folder)  # 获取新的序号
                    output_file = today_folder / f"{output_file_number}.avif"  # 新文件的路径

                    # 执行转换
                    convert_to_avif(file, output_file)
                    logging.info(f"转换完成: {output_file}")

                    # 生成Markdown链接
                    md_link = f"![{output_file.name}](https://{base_url}/img/{today_folder.name}/{output_file.name})"
                    pyperclip.copy(md_link)
                    logging.info(f"Markdown链接已复制到剪贴板")

                    # 删除原文件
                    os.remove(file)
                    logging.info(f"原文件已删除: {file}")

                    # 提交更改到 GitHub 并触发 Netlify 部署
                    git_commit_and_push()
                    logging.info("Git 提交并推送成功，Netlify 自动部署触发。")

            retry_count = 0  # 成功后重置重试计数
        except Exception as e:
            logging.error(f"发生错误: {e}")
            retry_count += 1
            logging.info(f"重试 {retry_count}/{max_retry_count}...")

        time.sleep(5)

# 启动监控
if __name__ == "__main__":
    logging.info(f"开始监控文件夹: {watch_folder}")
    monitor_folder()

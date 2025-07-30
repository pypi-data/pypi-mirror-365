import datetime
import os

import psutil


def get_uptime():
    """获取服务器的总运行时间"""
    boot_time_timestamp = psutil.boot_time()
    boot_time = datetime.datetime.fromtimestamp(boot_time_timestamp)
    current_time = datetime.datetime.now()
    uptime = current_time - boot_time
    days = uptime.days
    seconds = uptime.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    if days > 0:
        return f"{days}天{hours}小时{minutes}分钟{seconds}秒"
    else:
        return f"{hours}小时{minutes}分钟{seconds}秒"


def get_service_start_time():
    """获取服务的启动时间"""
    try:
        process = psutil.Process(os.getpid())
        start_time_seconds = process.create_time()  # 返回自纪元以来的秒数
        start_time = datetime.datetime.fromtimestamp(start_time_seconds).isoformat()
        return start_time
    except Exception as e:
        return f"无法获取服务启动时间: {str(e)}"

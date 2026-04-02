"""
工具函数模块
"""

import datetime
import json
from pathlib import Path

def get_current_time():
    """获取当前时间字符串"""
    return datetime.datetime.now().strftime("%H:%M")

def get_datetime_string():
    """获取日期时间字符串"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def get_display_time():
    """获取显示用时间"""
    return datetime.datetime.now().strftime("%m-%d %H:%M")

def clean_think_tags(text):
    """清理think标签"""
    return text.replace("<think>", "").replace("</think>", "")

def save_json_file(path, data):
    """保存JSON文件"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json_file(path):
    """加载JSON文件"""
    if not path.exists():
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def ensure_dir(path):
    """确保目录存在"""
    Path(path).mkdir(exist_ok=True)
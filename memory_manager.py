"""
记忆管理模块
"""

import json
from pathlib import Path
from utils import load_json_file, save_json_file, get_datetime_string

class MemoryManager:
    """记忆管理器"""
    
    def __init__(self, memory_dir):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
    def get_memory_path(self, chat_id):
        """获取记忆文件路径"""
        return self.memory_dir / f"{chat_id}_memory.json"
    
    def init_memory(self, chat_id):
        """初始化记忆文件"""
        path = self.get_memory_path(chat_id)
        if not path.exists():
            save_json_file(path, {"chat": chat_id, "list": []})
    
    def load_memory(self, chat_id):
        """加载记忆"""
        path = self.get_memory_path(chat_id)
        data = load_json_file(path)
        if not data:
            return ""
        
        memory_text = ""
        for item in data.get("list", [])[-6:]:
            memory_text += f"用户：{item['user']}\nAI：{item['ai']}\n---\n"
        return memory_text if memory_text else "无对话记忆"
    
    def update_memory(self, chat_id, user_input, ai_response):
        """更新记忆"""
        path = self.get_memory_path(chat_id)
        data = load_json_file(path) or {"chat": chat_id, "list": []}
        
        data.setdefault("list", []).append({
            "time": get_datetime_string(),
            "user": user_input,
            "ai": ai_response
        })
        
        # 限制记忆数量
        data["list"] = data["list"][-100:]
        save_json_file(path, data)
    
    def clear_memory(self, chat_id):
        """清空记忆"""
        path = self.get_memory_path(chat_id)
        save_json_file(path, {"chat": chat_id, "list": []})
    
    def get_memory_data(self, chat_id):
        """获取完整记忆数据"""
        path = self.get_memory_path(chat_id)
        return load_json_file(path) or {"chat": chat_id, "list": []}
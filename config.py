"""
配置文件
"""

import os
from pathlib import Path

# Ollama配置
OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "deepseek-r1:8b"
TEMPERATURE = 0.7

# 应用配置
APP_TITLE = "AI Chat Assistant"
APP_WIDTH = 1200
APP_HEIGHT = 750
APP_MIN_WIDTH = 900
APP_MIN_HEIGHT = 600

# 界面样式
BG_COLOR = '#f2f2f7'
SIDEBAR_BG = '#ffffff'
CHAT_BG = '#ffffff'
USER_BG = '#007aff'
AI_BG = '#f2f2f7'
TEXT_COLOR = '#1d1d1f'
SECONDARY_COLOR = '#86868b'

# 字体配置
FONT_FAMILY = "SF Pro Display"
FONT_SIZE_NORMAL = 12
FONT_SIZE_SMALL = 10
FONT_SIZE_LARGE = 18

# 对话配置
MAX_HISTORY = 8
MAX_MEMORY_ITEMS = 100

# 路径配置
MEMORY_DIR = Path("chat_memories")
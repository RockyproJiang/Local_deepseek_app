"""
UI组件模块
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import config

class ChatDisplay:
    """聊天显示组件"""
    
    def __init__(self, parent):
        self.parent = parent
        self.text_widget = None
        self.setup_display()
        
    def setup_display(self):
        """设置显示区域"""
        container = tk.Frame(self.parent, bg=config.CHAT_BG)
        container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(container, bg=config.CHAT_BG)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_widget = tk.Text(
            container, wrap=tk.WORD,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
            bg=config.CHAT_BG, bd=0, relief=tk.FLAT,
            yscrollcommand=scrollbar.set,
            highlightthickness=0, spacing3=6
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_widget.yview)
        
        # 配置标签样式
        self.text_widget.tag_config('user', foreground='white', background=config.USER_BG,
                                    font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
                                    lmargin1=100, lmargin2=100, rmargin=20,
                                    spacing1=8, spacing3=8)
        self.text_widget.tag_config('ai', foreground=config.TEXT_COLOR, background=config.AI_BG,
                                    font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
                                    lmargin1=20, lmargin2=20, rmargin=100,
                                    spacing1=8, spacing3=8)
        self.text_widget.tag_config('system', foreground=config.SECONDARY_COLOR,
                                    font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL, 'italic'),
                                    justify='center', spacing1=10, spacing3=10)
        self.text_widget.tag_config('name', foreground=config.SECONDARY_COLOR,
                                    font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL))
        
        self.text_widget.config(state=tk.DISABLED)
    
    def render_message(self, role, content, time):
        """渲染消息"""
        self.text_widget.config(state=tk.NORMAL)
        
        if role == "user":
            self.text_widget.insert(tk.END, f"你 • {time}\n", "name")
            self.text_widget.insert(tk.END, f" {content} \n", "user")
        elif role == "ai":
            self.text_widget.insert(tk.END, f"AI • {time}\n", "name")
            self.text_widget.insert(tk.END, f" {content} \n", "ai")
        else:
            self.text_widget.insert(tk.END, f"{content}\n", "system")
        
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)
    
    def clear(self):
        """清空显示"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)
    
    def get_index(self):
        """获取当前光标位置"""
        return self.text_widget.index(tk.END)

class InputArea:
    """输入区域组件"""
    
    def __init__(self, parent, on_send):
        self.parent = parent
        self.on_send = on_send
        self.text_widget = None
        self.setup_input()
        
    def setup_input(self):
        """设置输入区域"""
        input_frame = tk.Frame(self.parent, bg=config.CHAT_BG, height=130)
        input_frame.pack(fill=tk.X, padx=24, pady=(8, 20))
        input_frame.pack_propagate(False)
        
        input_box = tk.Frame(input_frame, bg=config.AI_BG, bd=0,
                            highlightthickness=1, highlightcolor='#d1d1d6',
                            highlightbackground='#d1d1d6')
        input_box.pack(fill=tk.BOTH, expand=True)
        
        self.text_widget = tk.Text(input_box,
                                  font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
                                  height=3, bg=config.AI_BG, bd=0,
                                  relief=tk.FLAT, padx=12, pady=10)
        self.text_widget.pack(fill=tk.BOTH, expand=True)
    
    def get_text(self):
        """获取输入文本"""
        return self.text_widget.get(1.0, tk.END).strip()
    
    def clear(self):
        """清空输入框"""
        self.text_widget.delete(1.0, tk.END)
"""
主应用类
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import json
import requests
from pathlib import Path

import config
from memory_manager import MemoryManager
from utils import get_current_time, get_display_time, clean_think_tags
from ui_components import ChatDisplay, InputArea

class ChatApplication:
    """聊天应用主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(config.APP_TITLE)
        self.root.geometry(f"{config.APP_WIDTH}x{config.APP_HEIGHT}")
        self.root.configure(bg=config.BG_COLOR)
        self.root.minsize(config.APP_MIN_WIDTH, config.APP_MIN_HEIGHT)
        
        # 初始化记忆管理器
        self.memory_manager = MemoryManager(config.MEMORY_DIR)
        
        # 会话管理
        self.conversations = {}
        self.current_chat_id = None
        self.conversation_history = []
        self.is_generating = False
        self.stop_generation = False
        self.current_response_thread = None
        
        # 流式输出专用变量
        self.ai_response_buffer = ""
        self.ai_message_start_index = None
        self.memory_windows = []
        
        # 创建界面
        self.create_ui()
        self.new_conversation()
    
    def create_ui(self):
        """创建用户界面"""
        main_container = tk.Frame(self.root, bg=config.BG_COLOR)
        main_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # 左侧面板
        self.create_sidebar(main_container)
        
        # 右侧主区域
        self.create_main_area(main_container)
    
    def create_sidebar(self, parent):
        """创建侧边栏"""
        left_frame = tk.Frame(parent, bg=config.SIDEBAR_BG, width=280, bd=0, relief='flat')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 4))
        left_frame.pack_propagate(False)
        
        # 标题区域
        title_frame = tk.Frame(left_frame, bg=config.SIDEBAR_BG, height=75)
        title_frame.pack(fill=tk.X, padx=18, pady=15)
        
        title_label = tk.Label(title_frame, text="对话列表",
                              font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold"),
                              bg=config.SIDEBAR_BG, fg=config.TEXT_COLOR)
        title_label.pack(side=tk.LEFT)
        
        new_btn = tk.Button(title_frame, text="+ 新建对话",
                           font=(config.FONT_FAMILY, 11, "bold"),
                           bg='#007aff', fg='white',
                           activebackground='#0062cc',
                           command=self.new_conversation,
                           relief=tk.FLAT, cursor='hand2',
                           padx=14, pady=6, bd=0)
        new_btn.pack(side=tk.RIGHT)
        
        # 对话列表
        list_frame = tk.Frame(left_frame, bg='#f7f7f7')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 12))
        
        scrollbar = tk.Scrollbar(list_frame, bg='#f7f7f7')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chat_listbox = tk.Listbox(list_frame, bg='#f7f7f7', fg=config.TEXT_COLOR,
                                       font=(config.FONT_FAMILY, 11),
                                       selectbackground='#007aff',
                                       selectforeground='white',
                                       relief=tk.FLAT, bd=0,
                                       yscrollcommand=scrollbar.set,
                                       highlightthickness=0, activestyle='none')
        self.chat_listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        scrollbar.config(command=self.chat_listbox.yview)
        self.chat_listbox.bind('<<ListboxSelect>>', self.switch_conversation)
    
    def create_main_area(self, parent):
        """创建主区域"""
        right_frame = tk.Frame(parent, bg=config.CHAT_BG)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 头部
        self.create_header(right_frame)
        
        # 聊天显示区域
        self.chat_display = ChatDisplay(right_frame)
        
        # 输入区域
        self.create_input_area(right_frame)
    
    def create_header(self, parent):
        """创建头部"""
        header_frame = tk.Frame(parent, bg=config.CHAT_BG, height=75)
        header_frame.pack(fill=tk.X, padx=24, pady=15)
        
        self.chat_title = tk.Label(header_frame, text="新对话",
                                  font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold"),
                                  bg=config.CHAT_BG, fg=config.TEXT_COLOR)
        self.chat_title.pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(header_frame, bg=config.CHAT_BG)
        btn_frame.pack(side=tk.RIGHT)
        
        memory_btn = tk.Button(btn_frame, text="📝 查看记忆",
                              font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                              bg=config.AI_BG, fg='#007aff',
                              activebackground='#e1e1e1',
                              command=self.show_memory,
                              relief=tk.FLAT, cursor='hand2',
                              padx=12, pady=5, bd=0)
        memory_btn.pack(side=tk.LEFT, padx=6)
        
        clear_btn = tk.Button(btn_frame, text="🗑️ 清空记忆",
                             font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                             bg=config.AI_BG, fg='#ff3b30',
                             activebackground='#e1e1e1',
                             command=self.clear_memory,
                             relief=tk.FLAT, cursor='hand2',
                             padx=12, pady=5, bd=0)
        clear_btn.pack(side=tk.LEFT, padx=6)
    
    def create_input_area(self, parent):
        """创建输入区域"""
        input_frame = tk.Frame(parent, bg=config.CHAT_BG)
        input_frame.pack(fill=tk.X, padx=24, pady=(8, 20))
        
        # 输入框容器
        input_container = tk.Frame(input_frame, bg=config.AI_BG, bd=0,
                                  highlightthickness=1, highlightcolor='#d1d1d6',
                                  highlightbackground='#d1d1d6')
        input_container.pack(fill=tk.BOTH, expand=True)
        
        self.input_text = tk.Text(input_container,
                                 font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL),
                                 height=3, bg=config.AI_BG, bd=0,
                                 relief=tk.FLAT, padx=12, pady=10)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # 底部按钮
        ctrl_frame = tk.Frame(input_frame, bg=config.CHAT_BG)
        ctrl_frame.pack(fill=tk.X, pady=8)
        
        self.stop_btn = tk.Button(ctrl_frame, text="⏸ 停止生成",
                                 font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL, "bold"),
                                 bg='#ff3b30', fg='white',
                                 activebackground='#e63946',
                                 command=self.stop_ai_generation,
                                 relief=tk.FLAT, cursor='hand2',
                                 padx=16, pady=6, bd=0, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=4)
        
        self.status_label = tk.Label(ctrl_frame, text="✅ 就绪",
                                    font=(config.FONT_FAMILY, 9),
                                    bg=config.CHAT_BG, fg=config.SECONDARY_COLOR)
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.send_btn = tk.Button(ctrl_frame, text="发送消息 ↩",
                                 font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL, "bold"),
                                 bg='#007aff', fg='white',
                                 activebackground='#0062cc',
                                 command=self.send_message,
                                 relief=tk.FLAT, cursor='hand2',
                                 padx=20, pady=6, bd=0)
        self.send_btn.pack(side=tk.RIGHT)
        
        # 快捷键
        self.input_text.bind('<Return>', self.on_enter)
        self.input_text.bind('<Shift-Return>', self.on_shift_enter)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_shift_enter(self, event):
        """Shift+Enter换行"""
        self.input_text.insert(tk.INSERT, "\n")
        return "break"
    
    def on_enter(self, event):
        """Enter发送消息"""
        if not self.is_generating:
            self.send_message()
        return "break"
    
    def new_conversation(self):
        """新建对话"""
        if self.current_chat_id:
            self.save_current_conversation()
        
        from utils import get_datetime_string, get_display_time
        chat_id = get_datetime_string()
        self.current_chat_id = chat_id
        self.conversation_history = []
        self.ai_response_buffer = ""
        self.ai_message_start_index = None
        
        self.chat_display.clear()
        self.input_text.delete(1.0, tk.END)
        
        name = f"对话 {get_display_time()}"
        self.chat_title.config(text=name)
        self.chat_listbox.insert(0, name)
        self.chat_listbox.selection_clear(0, tk.END)
        self.chat_listbox.selection_set(0)
        
        self.conversations[chat_id] = {
            "name": name, "history": [], "memory": self.memory_manager.get_memory_path(chat_id)
        }
        self.memory_manager.init_memory(chat_id)
        self.add_system_msg("✨ 新对话已创建，请问需要什么帮助？")
    
    def save_current_conversation(self):
        """保存当前对话"""
        if self.current_chat_id:
            self.conversations[self.current_chat_id]["history"] = self.conversation_history.copy()
    
    def switch_conversation(self, event):
        """切换对话"""
        sel = self.chat_listbox.curselection()
        if not sel:
            return
        
        self.save_current_conversation()
        target_name = self.chat_listbox.get(sel[0])
        
        for cid, data in self.conversations.items():
            if data["name"] == target_name:
                self.current_chat_id = cid
                self.conversation_history = data["history"].copy()
                self.chat_title.config(text=target_name)
                
                self.chat_display.clear()
                for msg in self.conversation_history:
                    self.chat_display.render_message(msg["role"], msg["content"], msg["time"])
                break
    
    def add_system_msg(self, text):
        """添加系统消息"""
        t = get_current_time()
        self.chat_display.render_message("system", text, t)
        self.conversation_history.append({"role": "system", "content": text, "time": t})
    
    def add_user_msg(self, text):
        """添加用户消息"""
        t = get_current_time()
        self.chat_display.render_message("user", text, t)
        self.conversation_history.append({"role": "user", "content": text, "time": t})
    
    def start_ai_msg(self):
        """开始AI消息"""
        t = get_current_time()
        self.ai_response_buffer = ""
        self.chat_display.text_widget.config(state=tk.NORMAL)
        self.chat_display.text_widget.insert(tk.END, "\n")
        self.chat_display.text_widget.insert(tk.END, f"AI • {t}\n", "name")
        self.ai_message_start_index = self.chat_display.text_widget.index(tk.END)
        self.chat_display.text_widget.insert(self.ai_message_start_index, " ", "ai")
        self.chat_display.text_widget.see(tk.END)
        self.chat_display.text_widget.config(state=tk.DISABLED)
    
    def stream_ai_msg(self, text):
        """流式输出AI消息"""
        clean_text = clean_think_tags(text)
        self.ai_response_buffer += clean_text
        self.chat_display.text_widget.config(state=tk.NORMAL)
        self.chat_display.text_widget.delete(self.ai_message_start_index, tk.END)
        self.chat_display.text_widget.insert(self.ai_message_start_index, f" {self.ai_response_buffer} \n", "ai")
        self.chat_display.text_widget.see(tk.END)
        self.chat_display.text_widget.config(state=tk.DISABLED)
    
    def finish_ai_msg(self):
        """完成AI消息"""
        t = get_current_time()
        self.conversation_history.append({"role": "ai", "content": self.ai_response_buffer, "time": t})
        self.ai_message_start_index = None
    
    def send_message(self):
        """发送消息"""
        txt = self.input_text.get(1.0, tk.END).strip()
        if not txt or self.is_generating:
            return
        
        self.input_text.delete(1.0, tk.END)
        self.add_user_msg(txt)
        
        self.is_generating = True
        self.stop_generation = False
        self.status_label.config(text="⌛ AI生成中...", fg='#007aff')
        self.send_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.start_ai_msg()
        self.current_response_thread = threading.Thread(target=self.get_ai_response, args=(txt,), daemon=True)
        self.current_response_thread.start()
    
    def stop_ai_generation(self):
        """停止AI生成"""
        self.stop_generation = True
        self.status_label.config(text="⏹ 已停止", fg='#ff3b30')
    
    def get_ai_response(self, user_input):
        """获取AI响应"""
        try:
            memory = self.memory_manager.load_memory(self.current_chat_id)
            messages = [{"role": "system", "content": f"你是智能助手，对话记忆：{memory}"}]
            
            # 获取最近的历史记录
            history = self.conversation_history[-config.MAX_HISTORY:]
            for m in history:
                if m["role"] == "user":
                    messages.append({"role": "user", "content": m["content"]})
                elif m["role"] == "ai":
                    messages.append({"role": "assistant", "content": m["content"]})
            
            payload = {
                "model": config.MODEL_NAME,
                "messages": messages,
                "stream": True,
                "options": {"temperature": config.TEMPERATURE}
            }
            
            url = f"{config.OLLAMA_URL}/api/chat"
            with requests.post(url, json=payload, stream=True, timeout=60) as resp:
                if resp.status_code != 200:
                    self.root.after(0, lambda: self.add_system_msg(f"❌ 请求失败：{resp.status_code}"))
                    return
                
                for line in resp.iter_lines():
                    if self.stop_generation:
                        break
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            c = data["message"]["content"]
                            self.root.after(0, self.stream_ai_msg, c)
                    except:
                        continue
        
        except requests.exceptions.ConnectionError:
            self.root.after(0, lambda: self.add_system_msg("❌ 无法连接Ollama，请启动服务"))
        except Exception as e:
            self.root.after(0, lambda: self.add_system_msg(f"❌ 错误：{str(e)}"))
        finally:
            if not self.stop_generation and self.ai_response_buffer:
                self.memory_manager.update_memory(self.current_chat_id, user_input, self.ai_response_buffer)
            self.root.after(0, self.finish_ai_msg)
            self.root.after(0, self.reset_ui)
    
    def reset_ui(self):
        """重置UI状态"""
        self.is_generating = False
        self.status_label.config(text="✅ 就绪", fg='#007aff')
        self.send_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def show_memory(self):
        """显示记忆"""
        for w in self.memory_windows:
            try:
                w.destroy()
            except:
                pass
        self.memory_windows.clear()
        
        data = self.memory_manager.get_memory_data(self.current_chat_id)
        if not data.get("list"):
            messagebox.showinfo("提示", "暂无记忆")
            return
        
        win = tk.Toplevel(self.root)
        win.title("对话记忆")
        win.geometry("720x650")
        win.configure(bg=config.BG_COLOR)
        self.memory_windows.append(win)
        
        f = tk.Frame(win, bg=config.SIDEBAR_BG)
        f.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(f, text="🧠 完整记忆", 
                font=(config.FONT_FAMILY, 16, "bold"),
                bg=config.SIDEBAR_BG, fg=config.TEXT_COLOR).pack(pady=10)
        
        st = scrolledtext.ScrolledText(f, font=(config.FONT_FAMILY, 11),
                                      bg=config.AI_BG, relief=tk.FLAT)
        st.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        content = f"📁 对话：{self.chat_title['text']}\n\n"
        for i, item in enumerate(data.get("list", []), 1):
            content += f"【{i}】\n👤 {item['user']}\n🤖 {item['ai']}\n{'='*40}\n\n"
        
        st.insert(1.0, content)
        st.config(state=tk.DISABLED)
        
        tk.Button(f, text="关闭", command=win.destroy,
                 bg='#007aff', fg='white',
                 font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
                 padx=20, pady=6).pack(pady=10)
    
    def clear_memory(self):
        """清空记忆"""
        if not messagebox.askyesno("确认", "确定清空当前对话所有记忆？"):
            return
        self.memory_manager.clear_memory(self.current_chat_id)
        self.add_system_msg("✅ 记忆已清空")
    
    def on_closing(self):
        """关闭应用"""
        self.save_current_conversation()
        for w in self.memory_windows:
            try:
                w.destroy()
            except:
                pass
        self.root.destroy()
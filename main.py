import tkinter as tk
from chat_app import ChatApplication

def main():
    """程序主入口"""
    root = tk.Tk()
    app = ChatApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()
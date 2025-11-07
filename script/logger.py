import tkinter as tk

class LogText(tk.Text):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        #固定黑底白字，不跟随主题变化
        self.configure(
            wrap="word",
            background="black",
            foreground="white",
            insertbackground="white",      #光标颜色
            selectbackground="blue",       #选中背景色
            selectforeground="white",      #选中字体颜色
            font=("Consolas", 10)
        )

        #定义日志类型颜色
        self.tag_configure("info", foreground="green")
        self.tag_configure("warn", foreground="yellow")
        self.tag_configure("error", foreground="red")
        self.tag_configure("default", foreground="white", background="black")

        #禁止用户输入，但允许选中复制
        self.bind("<Key>", lambda e: "break")

    def write(self, msg: str):
        """带类型的日志写入"""
        if msg.startswith("[INFO]"):
            tag = "info"
        elif msg.startswith("[WARN]"):
            tag = "warn"
        elif msg.startswith("[ERROR]"):
            tag = "error"
        else:
            tag = "default"

        self.insert("end", msg + "\n", tag)
        self.see("end")

    def write_raw(self, msg: str):
        """原始输出"""
        self.insert("end", msg + "\n", "default")
        self.see("end")

    def clear(self):
        """清空日志"""
        self.delete("1.0", "end")

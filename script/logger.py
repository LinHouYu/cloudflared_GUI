import tkinter as tk

class LogText(tk.Text):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(state="disabled", wrap="word")
        self.current_theme = "light"
        self.set_theme(self.current_theme)

        #定义日志类型颜色
        self.tag_configure("info", foreground="green")
        self.tag_configure("warn", foreground="orange")
        self.tag_configure("error", foreground="red")
        self.tag_configure("cloudflare_dark", foreground="gray80", background="black")
        self.tag_configure("cloudflare_light", foreground="gray20", background="white")

    def set_theme(self, theme: str):
        """根据主题调整背景和默认字体颜色"""
        self.current_theme = theme
        if theme == "dark":
            self.configure(background="black", foreground="white", insertbackground="white")
        else:
            self.configure(background="white", foreground="black", insertbackground="black")

    def write(self, msg: str):
        """带类型的日志写入"""
        self.configure(state="normal")

        if msg.startswith("[INFO]"):
            tag = "info"
        elif msg.startswith("[WARN]"):
            tag = "warn"
        elif msg.startswith("[ERROR]"):
            tag = "error"
        else:
            tag = f"cloudflare_{self.current_theme}"

        self.insert("end", msg + "\n", tag)
        self.see("end")
        self.configure(state="disabled")

    def write_raw(self, msg: str):
        """原始 cloudflared 输出"""
        self.configure(state="normal")
        tag = f"cloudflare_{self.current_theme}"
        self.insert("end", msg + "\n", tag)
        self.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")

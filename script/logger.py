import tkinter as tk

class LogText(tk.Text):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.tag_config("info", foreground="green")
        self.tag_config("error", foreground="red")
        self.tag_config("warn", foreground="yellow")
        self.tag_config("default", foreground="white")

    def _pick_tag(self, text: str) -> str:
        t = text.lower()
        if "[error]" in t or " level=error " in t:
            return "error"
        if "[warn]" in t or " level=warn " in t or " level=warning " in t:
            return "warn"
        if "[info]" in t or " level=info " in t or "success" in t:
            return "info"
        return "default"

    def write(self, message: str):
        tag = self._pick_tag(message)
        self.insert(tk.END, message + "\n", tag)
        self.see(tk.END)

    def write_raw(self, message: str):
        self.write(message)

    def clear(self):
        self.delete("1.0", tk.END)

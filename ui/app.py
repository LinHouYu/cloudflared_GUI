import tkinter as tk
from tkinter import ttk
import sv_ttk
import threading
import pystray
from PIL import Image
from ui.server_tab import ServerTab
from ui.client_tab import ClientTab
from ui.misc_tab import MiscTab
from script.storage import Storage
from utils import resource_path

class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.storage = Storage()
        self.parent = parent
        self.icon = None  #托盘图标对象

        #初始化主题
        theme = self.storage.load_settings().get("theme", "light")
        sv_ttk.set_theme(theme)

        parent.title("Cloudflare Tunnel GUI - By Linhouyu")
        parent.geometry("900x600")
        parent.iconbitmap(resource_path("cloudflared.ico"))

        parent.columnconfigure(0, weight=1)

        ttk.Label(
            parent,
            text="Cloudflare Tunnel GUI版",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        ttk.Button(parent, text="黑/白", command=self.toggle_theme).grid(
            row=0, column=1, sticky="ne", padx=10, pady=10
        )

        #Notebook
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        parent.rowconfigure(1, weight=1)

        #Tabs
        self.server_tab = ServerTab(self.notebook)
        self.client_tab = ClientTab(self.notebook)
        self.misc_tab = MiscTab(self.notebook)

        self.notebook.add(self.server_tab, text="服务端")
        self.notebook.add(self.client_tab, text="客户端")
        self.notebook.add(self.misc_tab, text="杂项")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        #恢复上次打开的标签页
        last = self.storage.load_last("tab")
        if last:
            if last.get("tunnel") == "server":
                self.notebook.select(self.server_tab)
            elif last.get("tunnel") == "client":
                self.notebook.select(self.client_tab)

        #初始化日志框主题
        if hasattr(self.server_tab, "log"):
            self.server_tab.log.set_theme(theme)
        if hasattr(self.client_tab, "log"):
            self.client_tab.log.set_theme(theme)
        if hasattr(self.misc_tab, "log"):
            self.misc_tab.log.set_theme(theme)

        #拦截关闭事件 → 隐藏到托盘
        parent.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def toggle_theme(self):
        """切换黑白主题，并同步更新日志框"""
        sv_ttk.toggle_theme()
        current = sv_ttk.get_theme()
        self.storage.save_settings({"theme": current})

        #同步日志框主题
        if hasattr(self.server_tab, "log"):
            self.server_tab.log.set_theme(current)
        if hasattr(self.client_tab, "log"):
            self.client_tab.log.set_theme(current)
        if hasattr(self.misc_tab, "log"):
            self.misc_tab.log.set_theme(current)

    def on_tab_changed(self, event):
        """保存最后一次打开的标签页"""
        tab = event.widget.select()
        tab_text = event.widget.tab(tab, "text")
        if tab_text == "服务端":
            self.storage.save_last("tab", "server", "")
        elif tab_text == "客户端":
            self.storage.save_last("tab", "client", "")

    #托盘功能
    def hide_to_tray(self):
        """隐藏窗口并显示托盘图标"""
        self.parent.withdraw()

        if self.icon is None:
            #托盘图标
            image = Image.open(resource_path("cloudflared.ico"))

            self.icon = pystray.Icon(
                "cloudflared_gui",
                image,
                "Cloudflared GUI",
                menu=pystray.Menu(
                    pystray.MenuItem("显示窗口", self.show_window),
                    pystray.MenuItem("退出程序", self.quit_app)
                )
            )

            #托盘必须在单独线程运行
            threading.Thread(target=self.icon.run, daemon=True).start()

    def show_window(self, icon=None, item=None):
        """从托盘恢复窗口"""
        self.parent.deiconify()
        if self.icon:
            self.icon.stop()
            self.icon = None

    def quit_app(self, icon=None, item=None):
        """退出程序"""
        if self.icon:
            self.icon.stop()
        self.parent.destroy()

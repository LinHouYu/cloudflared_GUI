import tkinter as tk
from tkinter import ttk
import sv_ttk
from ui.server_tab import ServerTab
from ui.client_tab import ClientTab
from script.storage import Storage
from ui.misc_tab import MiscTab
from utils import resource_path 

class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.storage = Storage()
        theme = self.storage.load_settings().get("theme", "light")
        sv_ttk.set_theme(theme)
        parent.title("Cloudflare Tunnel GUI - By Linhouyu")
        parent.geometry("900x600")
        parent.iconbitmap(resource_path("cloudflared.ico"))

        parent.columnconfigure(0, weight=1)
        ttk.Label(parent, text="Cloudflare Tunnel GUI版", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, sticky="nw", padx=10, pady=10
        )
        ttk.Button(parent, text="黑/白", command=self.toggle_theme).grid(
            row=0, column=1, sticky="ne", padx=10, pady=10
        )
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        parent.rowconfigure(1, weight=1)
        self.server_tab = ServerTab(self.notebook)
        self.client_tab = ClientTab(self.notebook)
        self.notebook.add(self.server_tab, text="服务端")
        self.notebook.add(self.client_tab, text="客户端")
        self.misc_tab = MiscTab(self.notebook)
        self.notebook.add(self.misc_tab, text="杂项")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        last = self.storage.load_last("tab")
        if last:
            if last.get("tunnel") == "server":
                self.notebook.select(self.server_tab)
            elif last.get("tunnel") == "client":
                self.notebook.select(self.client_tab)

    def toggle_theme(self):
        sv_ttk.toggle_theme()
        current = sv_ttk.get_theme()
        self.storage.save_settings({"theme": current})

    def on_tab_changed(self, event):
        tab = event.widget.select()
        tab_text = event.widget.tab(tab, "text")
        if tab_text == "服务端":
            self.storage.save_last("tab", "server", "")
        elif tab_text == "客户端":
            self.storage.save_last("tab", "client", "")

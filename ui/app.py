import tkinter as tk
from tkinter import ttk
import sv_ttk
from ui.server_tab import ServerTab
from ui.client_tab import ClientTab
from ui.misc_tab import MiscTab
from script.storage import Storage
from ui.lenguaje import LANG_DATA, LANG_ORDER, load_all_languages
from ui import tray
from utils import resource_path


class App(ttk.Frame):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.storage = Storage()
        self.parent = parent
        self.icon = None

        #加载语言文件
        load_all_languages()

        #加载主题和语言设置
        settings = self.storage.load_settings()
        theme = settings.get("theme", "light")
        sv_ttk.set_theme(theme)

        saved_lang = settings.get("lang")
        self.current_lang = saved_lang if saved_lang in LANG_ORDER else LANG_ORDER[0]
        pack = LANG_DATA[self.current_lang]

        #窗口设置
        self.parent.title(pack.get("title", "Cloudflare Tunnel GUI"))
        self.parent.geometry("900x600")
        try:
            self.parent.iconbitmap(resource_path("cloudflared.ico"))
        except:
            pass
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=1)

        #标题
        self.header_label = ttk.Label(
            self.parent,
            text=pack.get("header", pack.get("title", "Cloudflare Tunnel GUI")),
            font=("Segoe UI", 12, "bold")
        )
        self.header_label.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        #右上角按钮区
        button_frame = ttk.Frame(self.parent)
        button_frame.grid(row=0, column=1, sticky="ne", padx=10, pady=10)

        #语言选择下拉框
        self.lang_var = tk.StringVar()
        self.lang_map = {}
        choices = []
        for lang in LANG_ORDER:
            label = LANG_DATA[lang].get("lang_button", lang)
            display = f"{label} ({lang})"
            self.lang_map[display] = lang
            choices.append(display)
        current_label = LANG_DATA[self.current_lang].get("lang_button", self.current_lang)
        current_display = f"{current_label} ({self.current_lang})"
        self.lang_var.set(current_display)
        self.lang_combo = ttk.Combobox(button_frame, textvariable=self.lang_var,
                                       values=choices, state="readonly", width=12)
        self.lang_combo.pack(side="left", padx=(0, 5))
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_lang_selected)

        #主题切换按钮
        icon = "☀" if theme == "light" else "🌙"
        self.theme_button = ttk.Button(button_frame, text=icon, width=3, command=self.toggle_theme)
        self.theme_button.pack(side="left")

        #Notebook标签页
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.server_tab = ServerTab(self.notebook)
        self.client_tab = ClientTab(self.notebook)
        self.misc_tab = MiscTab(self.notebook)

        self.notebook.add(self.server_tab, text="")
        self.notebook.add(self.client_tab, text="")
        self.notebook.add(self.misc_tab, text="")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        #恢复上次打开的标签
        last = self.storage.load_last("tab")
        if isinstance(last, dict):
            if last.get("tunnel") == "server":
                self.notebook.select(self.server_tab)
            elif last.get("tunnel") == "client":
                self.notebook.select(self.client_tab)

        #同步日志主题
        for tab in (self.server_tab, self.client_tab, self.misc_tab):
            if hasattr(tab, "log"):
                try:
                    tab.log.set_theme(theme)
                except:
                    pass

        #应用语言
        self.apply_language()

        #关闭窗口时隐藏到托盘
        self.parent.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    #切换主题
    def toggle_theme(self):
        sv_ttk.toggle_theme()
        current = sv_ttk.get_theme()
        self.storage.save_settings({"theme": current, "lang": self.current_lang})
        for tab in (self.server_tab, self.client_tab, self.misc_tab):
            if hasattr(tab, "log"):
                try:
                    tab.log.set_theme(current)
                except:
                    pass
        self.theme_button.config(text="☀" if current == "light" else "🌙")

    #下拉框选择语言
    def on_lang_selected(self, event):
        selected_display = self.lang_var.get()
        if selected_display in self.lang_map:
            lang_key = self.lang_map[selected_display]
            self.set_language(lang_key)

    #设置语言
    def set_language(self, lang_key: str):
        if lang_key in LANG_ORDER:
            self.current_lang = lang_key
            self.storage.save_settings({"theme": sv_ttk.get_theme(), "lang": self.current_lang})
            self.apply_language()

    #应用语言
    def apply_language(self):
        pack = LANG_DATA[self.current_lang]
        self.parent.title(pack.get("title", "Cloudflare Tunnel GUI"))
        self.header_label.config(text=pack.get("header", pack.get("title", "Cloudflare Tunnel GUI")))
        current_display = f"{pack.get('lang_button', self.current_lang)} ({self.current_lang})"
        self.lang_var.set(current_display)

        tabs = pack.get("tabs", {})
        self.notebook.tab(self.server_tab, text=tabs.get("server", "Server"))
        self.notebook.tab(self.client_tab, text=tabs.get("client", "Client"))
        self.notebook.tab(self.misc_tab, text=tabs.get("misc", "Misc"))

        self.update_tab_texts(self.server_tab, pack.get("server_tab", {}))
        self.update_tab_texts(self.client_tab, pack.get("client_tab", {}))
        self.update_tab_texts(self.misc_tab, pack.get("misc_tab", {}))

        if self.icon:
            try:
                self.icon.stop()
            except:
                pass
            self.icon = None
            self.hide_to_tray()

    #更新标签页文字
    def update_tab_texts(self, tab, lang_map: dict):
        labels_map = lang_map.get("labels", {})
        buttons_map = lang_map.get("buttons", {})
        headers_map = lang_map.get("headers", {})

        for child in tab.winfo_children():
            if isinstance(child, (ttk.Label, ttk.LabelFrame)):
                if not hasattr(child, "_lang_key"):
                    child._lang_key = child.cget("text")
                key = child._lang_key
                if key in labels_map:
                    child.config(text=labels_map[key])
            elif isinstance(child, ttk.Button):
                if not hasattr(child, "_lang_key"):
                    child._lang_key = child.cget("text")
                key = child._lang_key
                if key in buttons_map:
                    child.config(text=buttons_map[key])
            elif isinstance(child, ttk.Frame):
                self.update_tab_texts(child, lang_map)

        if hasattr(tab, "tree") and isinstance(tab.tree, ttk.Treeview) and headers_map:
            for col in tab.tree["columns"]:
                current_header = tab.tree.heading(col, option="text")
                if current_header in headers_map:
                    tab.tree.heading(col, text=headers_map[current_header])

    #切换标签时保存
    def on_tab_changed(self, event):
        tab_id = event.widget.select()
        tab_text = event.widget.tab(tab_id, "text")
        current_pack = LANG_DATA.get(self.current_lang, {})
        tabs_map = current_pack.get("tabs", {})
        if tab_text in {tabs_map.get("server", "Server"), "服务端", "Server"}:
            self.storage.save_last("tab", "server", "")
        elif tab_text in {tabs_map.get("client", "Client"), "客户端", "Client"}:
            self.storage.save_last("tab", "client", "")

    #隐藏到托盘
    def hide_to_tray(self):
        self.parent.withdraw()
        if self.icon is None:
            pack = LANG_DATA[self.current_lang]
            self.icon = tray.create_tray_icon(self, pack)

    #显示窗口
    def show_window(self, icon=None, item=None):
        try:
            self.parent.deiconify()
        except:
            pass
        if self.icon:
            try:
                self.icon.stop()
            except:
                pass
            self.icon = None

    #退出程序
    def quit_app(self, icon=None, item=None):
        if self.icon:
            try:
                self.icon.stop()
            except:
                pass
        try:
            self.parent.destroy()
        except:
            pass


#入口
def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()

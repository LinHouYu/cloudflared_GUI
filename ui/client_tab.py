import tkinter as tk
from tkinter import ttk
from script.logger import LogText
from script.storage import Storage
from script.runner import CloudflareRunner

class ClientTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.storage = Storage()
        self.runner = CloudflareRunner(lambda msg: self.log.write_raw(msg))

        ttk.Label(self, text="隧道域名:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.tunnel_entry = ttk.Entry(self)
        self.tunnel_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=6)

        ttk.Label(self, text="本地监听端口:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.port_entry = ttk.Entry(self)
        self.port_entry.grid(row=1, column=1, sticky="ew", padx=6, pady=6)

        #恢复上次输入
        last = self.storage.load_last("client")
        if last:
            self.tunnel_entry.insert(0, last.get("tunnel", ""))
            self.port_entry.insert(0, last.get("port", ""))

        ttk.Button(self, text="连接", command=self.connect_client).grid(row=2, column=0, columnspan=2, pady=10)

        self.log = LogText(self, height=12)
        self.log.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

    def connect_client(self):
        hostname = self.tunnel_entry.get().strip()
        port = self.port_entry.get().strip()
        if not hostname or not port.isdigit():
            self.log.write("[ERROR] 输入错误，请检查隧道域名和端口")
            return
        self.log.write(f"[INFO] 连接隧道: {hostname} → 本地端口 {port}")
        self.runner.run_command([
            "cloudflared", "access", "tcp",
            "--hostname", hostname,
            "--listener", f"127.0.0.1:{port}"
        ])
        #保存本次输入
        self.storage.save_last("client", hostname, port)

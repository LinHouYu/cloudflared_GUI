import tkinter as tk
from tkinter import ttk
from script.logger import LogText
from script.storage import Storage
from script.runner import CloudflareRunner
import re
import subprocess

class ClientTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.storage = Storage()
        self.runner = CloudflareRunner(lambda msg: self.log.write_raw(msg))

        ttk.Label(self, text="隧道域名:").grid(row=0, column=0, sticky="w", padx=6, pady=6)

        def validate_hostname(P):
            #允许字母、数字、点号，且不能以点开头或结尾
            if P == "" or re.fullmatch(r"[A-Za-z0-9]+(\.[A-Za-z0-9]+)*", P):
                self.tunnel_entry.state(["!invalid"])
                return True
            else:
                self.tunnel_entry.state(["invalid"])
                return True

        vcmd_host = (self.register(validate_hostname), "%P")
        self.tunnel_entry = ttk.Entry(self, validate="key", validatecommand=vcmd_host)
        self.tunnel_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=6)

        ttk.Label(self, text="本地监听端口:").grid(row=1, column=0, sticky="w", padx=6, pady=6)

        def validate_port(P):
            if P.isdigit() or P == "":
                self.port_entry.state(["!invalid"])
                return True
            else:
                self.port_entry.state(["invalid"])
                return True

        vcmd_port = (self.register(validate_port), "%P")
        self.port_entry = ttk.Entry(self, validate="key", validatecommand=vcmd_port)
        self.port_entry.grid(row=1, column=1, sticky="ew", padx=6, pady=6)

        #恢复上次输入
        last = self.storage.load_last("client")
        if last:
            self.tunnel_entry.insert(0, last.get("tunnel", ""))
            self.port_entry.insert(0, last.get("port", ""))

        #按钮区：连接 + 暂停
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="连接", command=self.connect_client).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="暂停连接", command=self.stop_client).pack(side="left", padx=5)

        #日志框
        self.log = LogText(self, height=12)
        self.log.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

    def connect_client(self):
        hostname = self.tunnel_entry.get().strip()
        port = self.port_entry.get().strip()
        #再次严格检查
        if not re.fullmatch(r"[A-Za-z0-9]+(\.[A-Za-z0-9]+)*", hostname) or not port.isdigit():
            self.log.write("[ERROR] 输入错误，请检查隧道域名和端口")
            return
        self.log.write(f"[INFO] 连接隧道: {hostname} → 本地端口 {port}")
        self.runner.run_command(
            [
                "cloudflared", "access", "tcp",
                "--hostname", hostname,
                "--listener", f"127.0.0.1:{port}"
            ],
            return_process=True
        )
        self.storage.save_last("client", hostname, port)

    def stop_client(self):
        """停止当前连接"""
        self.runner.stop()
        self.log.write("[INFO] 已暂停连接")

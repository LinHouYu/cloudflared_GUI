import tkinter as tk
from tkinter import ttk, messagebox
from script.logger import LogText
from script.storage import Storage
from script.runner import CloudflareRunner
import subprocess

class ServerTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.storage = Storage()
        self.runner = CloudflareRunner(lambda msg: self.log.write_raw(msg))

        ttk.Label(self, text="隧道名字:").grid(row=0, column=0, sticky="w", padx=6, pady=6)

        def validate_tunnel(P):
            if P.isalpha() or P == "":
                self.tunnel_entry.state(["!invalid"])
                return True
            else:
                self.tunnel_entry.state(["invalid"])
                return True

        vcmd_tunnel = (self.register(validate_tunnel), "%P")
        self.tunnel_entry = ttk.Entry(self, validate="key", validatecommand=vcmd_tunnel)
        self.tunnel_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=6)

        ttk.Label(self, text="端口号:").grid(row=1, column=0, sticky="w", padx=6, pady=6)

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

        last = self.storage.load_last("server")
        if last:
            self.tunnel_entry.insert(0, last.get("tunnel", ""))
            self.port_entry.insert(0, last.get("port", ""))

        #按钮区：放在一个居中的 Frame 里
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=8)  # 占据三列，居中

        ttk.Button(btn_frame, text="创建隧道", command=self.create_tunnel).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="启动隧道", command=self.start_tunnel).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="停止隧道", command=self.stop_tunnel).pack(side="left", padx=10)

        #隧道列表
        columns = ("id", "name", "created", "connections")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="NAME")
        self.tree.heading("created", text="CREATED")
        self.tree.heading("connections", text="CONNECTIONS")
        self.tree.column("id", width=240, anchor="w")
        self.tree.column("name", width=160, anchor="w")
        self.tree.column("created", width=170, anchor="w")
        self.tree.column("connections", width=260, anchor="w")
        self.tree.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=6, pady=6)

        #双击选择隧道
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        #工具栏：放在一个居中的 Frame 里
        bar = ttk.Frame(self)
        bar.grid(row=4, column=0, columnspan=3, pady=6)  # 占据三列，居中

        ttk.Button(bar, text="刷新隧道列表", command=self.refresh_tunnels).pack(side="left", padx=10)
        ttk.Button(bar, text="删除隧道", command=self.delete_tunnel).pack(side="left", padx=10)
        ttk.Button(bar, text="清空日志", command=self.clear_log).pack(side="left", padx=10)


        #日志
        self.log = LogText(self, height=10)
        self.log.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=6, pady=6)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, weight=1)

        self.after(200, self.refresh_tunnels)

    def clear_log(self):
        self.log.clear()

    def create_tunnel(self):
        name = self.tunnel_entry.get().strip()
        if not name or not name.isalpha():
            self.log.write("[ERROR] 隧道名不能为空且只能包含字母")
            return
        self.runner.run_command(["cloudflared", "tunnel", "create", name])
        self.log.write(f"[INFO] 已创建隧道 {name}")
        self.storage.save_last("server", name, self.port_entry.get().strip())

    def start_tunnel(self):
        name = self.tunnel_entry.get().strip()
        port = self.port_entry.get().strip()
        if not name.isalpha() or not port.isdigit():
            self.log.write("[ERROR] 隧道名或端口错误")
            return
        self.runner.run_command(
            ["cloudflared", "tunnel", "--name", name, "--url", f"tcp://127.0.0.1:{port}"],
            return_process=True
        )
        self.log.write(f"[INFO] 已启动隧道 {name} 端口 {port}")
        self.storage.save_last("server", name, port)

    def stop_tunnel(self):
        self.runner.stop()

    def refresh_tunnels(self):
        self.tree.delete(*self.tree.get_children())
        try:
            result = subprocess.run(
                ["cloudflared", "tunnel", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            lines = result.stdout.splitlines()
            count = 0
            for line in lines:
                line = line.strip()
                if not line or line.startswith("You can obtain") or line.startswith("ID "):
                    continue
                parts = line.split(maxsplit=3)
                if len(parts) == 4:
                    cid, name, created, connections = parts
                elif len(parts) == 3:
                    cid, name, created = parts
                    connections = ""
                else:
                    continue
                self.tree.insert("", "end", values=(cid, name, created, connections))
                count += 1
            self.log.write(f"[INFO] 已刷新隧道列表，共 {count} 条")
        except FileNotFoundError:
            self.log.write("[ERROR] 未找到 cloudflared 可执行文件，请检查安装与 PATH")
        except Exception as e:
            self.log.write(f"[ERROR] 刷新隧道列表失败: {e}")

    def delete_tunnel(self):
        selected = self.tree.selection()
        if not selected:
            self.log.write("[WARN] 请先选择要删除的隧道")
            return
        values = self.tree.item(selected[0], "values")
        if len(values) < 2:
            self.log.write("[ERROR] 无法获取隧道名")
            return
        tunnel_name = values[1]
        confirm = messagebox.askyesno("确认删除", f"确定要删除隧道 '{tunnel_name}' 吗？")
        if not confirm:
            self.log.write(f"[INFO] 已取消删除隧道 {tunnel_name}")
            return
        self.log.write(f"[INFO] 正在删除隧道 {tunnel_name} ...")
        try:
            result = subprocess.run(
                ["cloudflared", "tunnel", "delete", tunnel_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                self.log.write(f"[INFO] 隧道 {tunnel_name} 已删除")
            else:
                self.log.write(f"[ERROR] 删除失败: {result.stdout.strip()}")
        except FileNotFoundError:
            self.log.write("[ERROR] 未找到 cloudflared 可执行文件，请检查安装与 PATH")
        except Exception as e:
            self.log.write(f"[ERROR] 删除隧道时出错: {e}")
        self.refresh_tunnels()

    def on_tree_double_click(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        if len(values) >= 2:
            name = values[1]
            self.tunnel_entry.delete(0, tk.END)
            self.tunnel_entry.insert(0, name)
            self.log.write(f"[INFO] 已选择隧道 {name}")

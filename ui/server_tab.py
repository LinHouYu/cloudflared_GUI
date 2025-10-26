import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from script.logger import LogText
from script.storage import Storage
from script.runner import CloudflareRunner

class ServerTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.storage = Storage()
        self.runner = CloudflareRunner(lambda msg: self.log.write_raw(msg))

        # 输入区
        ttk.Label(self, text="隧道名字:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.tunnel_entry = ttk.Entry(self)
        self.tunnel_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=6)

        ttk.Label(self, text="端口号:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.port_entry = ttk.Entry(self)
        self.port_entry.grid(row=1, column=1, sticky="ew", padx=6, pady=6)

        # 恢复上次输入
        last = self.storage.load_last("server")
        if last:
            self.tunnel_entry.insert(0, last.get("tunnel", ""))
            self.port_entry.insert(0, last.get("port", ""))

        # 按钮：创建 + 启动
        ttk.Button(self, text="创建隧道", command=self.create_tunnel).grid(row=2, column=0, padx=6, pady=8)
        ttk.Button(self, text="启动隧道", command=self.start_tunnel).grid(row=2, column=1, padx=6, pady=8, sticky="w")

        # 隧道列表 Treeview
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
        self.tree.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

        # 双击填充 NAME 到输入框
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # 工具栏
        bar = ttk.Frame(self)
        bar.grid(row=4, column=0, columnspan=2, sticky="ew", padx=6, pady=2)
        ttk.Button(bar, text="刷新隧道列表", command=self.refresh_tunnels).pack(side="left", padx=2)
        ttk.Button(bar, text="删除隧道", command=self.delete_tunnel).pack(side="left", padx=2)   # ✅ 新增
        ttk.Button(bar, text="清空日志", command=self.clear_log).pack(side="left", padx=2)

        # 日志
        self.log = LogText(self, height=10)
        self.log.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

        # 布局权重
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, weight=1)

        # 启动时自动刷新
        self.after(200, self.refresh_tunnels)

    def clear_log(self):
        self.log.clear()

    def create_tunnel(self):
        name = self.tunnel_entry.get().strip()
        if not name:
            self.log.write("[ERROR] 隧道名不能为空")
            return
        self.runner.run_command(["cloudflared", "tunnel", "create", name])
        self.log.write(f"[INFO] 已创建隧道 {name}")
        self.storage.save_last("server", name, self.port_entry.get().strip())

    def start_tunnel(self):
        name = self.tunnel_entry.get().strip()
        port = self.port_entry.get().strip()
        if not name or not port.isdigit():
            self.log.write("[ERROR] 隧道名或端口错误")
            return
        self.runner.run_command(["cloudflared", "tunnel", "--name", name, "--url", f"tcp://127.0.0.1:{port}"])
        self.log.write(f"[INFO] 已启动隧道 {name} 端口 {port}")
        self.storage.save_last("server", name, port)

    def refresh_tunnels(self):
        """刷新并显示所有隧道到 Treeview"""
        self.tree.delete(*self.tree.get_children())
        try:
            result = subprocess.run(
                ["cloudflared", "tunnel", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
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
        """删除选中的隧道（带确认对话框）"""
        selected = self.tree.selection()
        if not selected:
            self.log.write("[WARN] 请先选择要删除的隧道")
            return
        values = self.tree.item(selected[0], "values")
        if len(values) < 2:
            self.log.write("[ERROR] 无法获取隧道名")
            return
        tunnel_name = values[1]

        # ✅ 弹出确认对话框
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
                text=True
            )
            if result.returncode == 0:
                self.log.write(f"[INFO] 隧道 {tunnel_name} 已删除")
            else:
                self.log.write(f"[ERROR] 删除失败: {result.stdout.strip()}")
        except FileNotFoundError:
            self.log.write("[ERROR] 未找到 cloudflared 可执行文件，请检查安装与 PATH")
        except Exception as e:
            self.log.write(f"[ERROR] 删除隧道时出错: {e}")

        # 删除后刷新
        self.refresh_tunnels()

    def on_tree_double_click(self, event):
        """双击行将 NAME 写入输入框"""
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        if len(values) >= 2:
            name = values[1]
            self.tunnel_entry.delete(0, tk.END)
            self.tunnel_entry.insert(0, name)
            self.log.write(f"[INFO] 已选择隧道 {name}")

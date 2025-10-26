import tkinter as tk
from tkinter import ttk
import subprocess, webbrowser, threading
from script.logger import LogText
from PIL import Image, ImageTk 
from utils import resource_path

class MiscTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # 按钮区
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Cloudflared 授权登录", command=self.login_cloudflared).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="检查 cloudflared 版本", command=self.check_version).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="更新 cloudflared", command=self.update_cloudflared).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="下载 cloudflared", command=self.download_cloudflared).pack(side="left", padx=5)

        # 日志框
        self.log = LogText(self, height=3)
        self.log.pack(fill="x", padx=10, pady=10)

        # 打赏区（微信 + USDT 并排）
        donate_frame = ttk.LabelFrame(self, text="打赏")
        donate_frame.pack(pady=10)

        # 微信二维码
        try:
            img = Image.open(resource_path("ui/wechat.png"))
            img = img.resize((200, 200))
            self.qr_img = ImageTk.PhotoImage(img)
            wx_frame = ttk.Frame(donate_frame)
            wx_frame.pack(side="left", padx=20)
            tk.Label(wx_frame, image=self.qr_img).pack()
            ttk.Label(wx_frame, text="微信打赏").pack(pady=5)
        except Exception:
            ttk.Label(donate_frame, text="未找到微信二维码图片").pack(side="left", padx=20)

        # USDT 二维码 + 地址
        try:
            cimg = Image.open(resource_path("ui/usdt.png"))
            cimg = cimg.resize((200, 200))
            self.usdt_img = ImageTk.PhotoImage(cimg)
            usdt_frame = ttk.Frame(donate_frame)
            usdt_frame.pack(side="left", padx=20)
            tk.Label(usdt_frame, image=self.usdt_img).pack()
            ttk.Label(usdt_frame, text="USDT 打赏 (TRC20)").pack(pady=5)

            # 可点击复制的地址
            self.usdt_address = "TQhtmLB9A7xjjPzXJZv95g7XzRo5QhXFVq"
            addr_label = ttk.Label(usdt_frame, text=f"地址: {self.usdt_address}", foreground="blue", cursor="hand2")
            addr_label.pack()
            addr_label.bind("<Button-1>", self.copy_usdt_address)

        except Exception:
            ttk.Label(donate_frame, text="未找到 USDT 收款二维码").pack(side="left", padx=20)

        # GitHub & Bilibili
        link_frame = ttk.LabelFrame(self, text="关于我")
        link_frame.pack(pady=10, fill="x")

        github = ttk.Label(link_frame, text="GitHub: https://github.com/LinHouYu", foreground="blue", cursor="hand2")
        github.pack(anchor="w", padx=10, pady=2)
        github.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/LinHouYu"))

        bili = ttk.Label(link_frame, text="Bilibili: https://space.bilibili.com/1563740453", foreground="blue", cursor="hand2")
        bili.pack(anchor="w", padx=10, pady=2)
        bili.bind("<Button-1>", lambda e: webbrowser.open("https://space.bilibili.com/1563740453"))

    # ===== 功能函数 =====
    def check_version(self):
        try:
            result = subprocess.run(["cloudflared", "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.log.write(result.stdout.strip())
        except FileNotFoundError:
            self.log.write("[ERROR] 未找到 cloudflared，请检查安装")
        except Exception as e:
            self.log.write(f"[ERROR] 检查版本失败: {e}")

    def update_cloudflared(self):
        try:
            result = subprocess.run(["cloudflared", "update"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.log.write(result.stdout.strip())
        except FileNotFoundError:
            self.log.write("[ERROR] 未找到 cloudflared，请检查安装")
        except Exception as e:
            self.log.write(f"[ERROR] 更新失败: {e}")

    def login_cloudflared(self):
        """执行 cloudflared tunnel login，自动跳转浏览器授权，并在日志中打印认证链接"""
        try:
            process = subprocess.Popen(
                ["cloudflared", "tunnel", "login"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            self.log.write("[INFO] 已启动 Cloudflared 授权，请在浏览器完成登录")

            def reader():
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        self.log.after(0, lambda l=line: self.log.write(l))
                        if "https://" in line:
                            self.log.after(0, lambda l=line: self.log.write(f"[INFO] 请手动打开以下链接完成授权: {l}"))
                            # 自动复制到剪贴板
                            self.clipboard_clear()
                            self.clipboard_append(line)
                            self.log.after(0, lambda: self.log.write("[INFO] 已复制授权链接到剪贴板"))

            threading.Thread(target=reader, daemon=True).start()

        except FileNotFoundError:
            self.log.write("[ERROR] 未找到 cloudflared，请检查安装")
        except Exception as e:
            self.log.write(f"[ERROR] 授权登录失败: {e}")

    def download_cloudflared(self):
        """跳转到 cloudflared 官方下载页面"""
        url = "https://github.com/cloudflare/cloudflared/releases/latest"
        webbrowser.open(url)
        self.log.write("[INFO] 已打开浏览器下载 cloudflared")

    def copy_usdt_address(self, event=None):
        """点击复制 USDT 地址到剪贴板"""
        self.clipboard_clear()
        self.clipboard_append(self.usdt_address)
        self.log.write("[INFO] 已复制 USDT 地址到剪贴板")

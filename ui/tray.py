import threading
import pystray
from PIL import Image
from utils import resource_path
import psutil
import subprocess
import tkinter.messagebox as msg
import platform

# 跨平台安全关闭隧道
def safe_kill_tunnel(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            try:
                child.terminate()
            except Exception:
                child.kill()
        parent.terminate()
        parent.wait(timeout=5)
    except Exception:
        system = platform.system().lower()
        try:
            if system == "windows":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], check=False)
            elif system in ("linux", "darwin"):
                subprocess.run(["pkill", "-TERM", "-P", str(pid)], check=False)
                subprocess.run(["kill", "-TERM", str(pid)], check=False)
            else:
                psutil.Process(pid).kill()
        except Exception:
            pass

# 检测隧道是否在运行
def is_tunnel_running(app):
    pid = None
    try:
        pid = app.storage.load_last("tunnel_pid")
    except Exception:
        pid = None
    if pid:
        try:
            p = psutil.Process(pid)
            if p.is_running():
                return True, pid
        except Exception:
            pass
    for proc in psutil.process_iter(attrs=["name", "cmdline"]):
        try:
            if "cloudflared" in (proc.info["name"] or "").lower() or \
               any("cloudflared" in (arg or "") for arg in (proc.info["cmdline"] or [])):
                return True, proc.pid
        except Exception:
            continue
    return False, None

# 创建托盘图标
def create_tray_icon(app, pack):
    tooltip = pack.get("tray", {}).get("tooltip", "Cloudflared GUI")
    show_text = pack.get("tray", {}).get("show", "Show Window")
    quit_text = pack.get("tray", {}).get("quit", "Quit")
    confirm_title = pack.get("tray", {}).get("confirm_title", "提示")
    confirm_close = pack.get("tray", {}).get("confirm_close", "喵~ 你有一个隧道在运行，确定要关闭吗？")

    try:
        image = Image.open(resource_path("cloudflared.ico"))
    except:
        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))

    def on_quit(icon, item):
        running, pid = is_tunnel_running(app)
        if running and pid:
            if msg.askyesno(confirm_title, confirm_close):
                safe_kill_tunnel(pid)
                for proc in psutil.process_iter(attrs=["name"]):
                    if "cloudflared" in (proc.info["name"] or "").lower():
                        try:
                            proc.kill()
                        except Exception:
                            pass
                app.quit_app()
            else:
                return
        else:
            app.quit_app()

    menu = pystray.Menu(
        pystray.MenuItem(show_text, app.show_window, default=True),
        pystray.MenuItem(quit_text, on_quit)
    )

    icon = pystray.Icon("cloudflared_gui", image, tooltip, menu=menu)
    threading.Thread(target=icon.run, daemon=True).start()
    return icon

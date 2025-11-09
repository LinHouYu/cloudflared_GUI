import PyInstaller.__main__
import os, sys

if __name__ == "__main__":
    sep = ";" if sys.platform.startswith("win") else ":"
    PyInstaller.__main__.run([
        "main.py",
        "--onefile",
        "--noconsole",
        f"--icon={os.path.abspath('cloudflared.ico')}",
        f"--add-data={os.path.abspath('cloudflared.ico')}{sep}.",
        f"--add-data={os.path.abspath('ui')}{sep}ui",
        f"--add-data={os.path.abspath('data')}{sep}data",
        f"--add-data={os.path.abspath('lenguaje')}{sep}lenguaje",
        f"--add-data={os.path.abspath('ui/wechat.png')}{sep}ui",
        f"--add-data={os.path.abspath('ui/usdt.png')}{sep}ui",
        "--clean",
        "--name=CloudflaredGUI"
    ])

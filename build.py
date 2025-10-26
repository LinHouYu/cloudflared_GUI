import PyInstaller.__main__
import os

if __name__ == "__main__":
    PyInstaller.__main__.run([
        "main.py",                                
        "--onefile",                              
        "--noconsole",                            
        f"--icon={os.path.abspath('cloudflared.ico')}",      
        f"--add-data={os.path.abspath('cloudflared.ico')};.",
        f"--add-data={os.path.abspath('ui')};ui",            
        f"--add-data={os.path.abspath('data')};data",        
        f"--add-data={os.path.abspath('ui/wechat.png')};ui", 
        f"--add-data={os.path.abspath('ui/usdt.png')};ui",   
        "--clean",                                
        "--name=CloudflaredGUI"                   
    ])

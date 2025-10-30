import sys, os

def resource_path(relative_path: str) -> str:
    """
    获取资源文件路径，兼容 PyInstaller 打包。
    - 开发环境：返回当前目录下的路径
    - 打包环境：返回 _MEIPASS 临时目录下的路径
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

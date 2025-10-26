# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\zhish\\Desktop\\cloudflared_GUI\\cloudflared.ico', '.'), ('C:\\Users\\zhish\\Desktop\\cloudflared_GUI\\ui', 'ui'), ('C:\\Users\\zhish\\Desktop\\cloudflared_GUI\\data', 'data'), ('C:\\Users\\zhish\\Desktop\\cloudflared_GUI\\ui\\wechat.png', 'ui'), ('C:\\Users\\zhish\\Desktop\\cloudflared_GUI\\ui\\usdt.png', 'ui')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CloudflaredGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\zhish\\Desktop\\cloudflared_GUI\\cloudflared.ico'],
)

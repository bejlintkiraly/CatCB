# -*- mode: python ; coding: utf-8 -*-
# CatCB v1.10.2: native pywebview host with Outlook COM + local UI
from PyInstaller.utils.hooks import collect_submodules, collect_all

datas = []
binaries = []
hiddenimports = [
    "pythoncom", "pywintypes", "win32timezone", "win32com", "win32com.client",
    "webview.platforms.edgechromium", "webview.platforms.winforms", "clr", "System",
]
for package in ["win32com", "webview", "pythonnet", "clr_loader"]:
    d, b, h = collect_all(package)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ["CatCB_Desktop_Launcher_v14.py"],
    pathex=[],
    binaries=binaries,
    datas=datas + [
        ("index.html", "."),
        ("CatCB_Space_v14.jpg", "."),
        ("CatCB_Mascot_v14.png", "."),
        ("CatCB_Mascot_v14.ico", "."),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PyQt5", "PyQt6", "PySide2", "PySide6", "cefpython3", "gi"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="CatCB",
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
    icon=["CatCB_Mascot_v14.ico"],
)

# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("customtkinter")

excluded_modules = [
    "debugpy",
    "IPython",
    "ipykernel",
    "jedi",
    "jupyter_client",
    "jupyter_core",
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "setuptools",
    "zmq",
]

a = Analysis(
    ['../apps/liverig/main.py'],
    pathex=['../apps/liverig'],
    binaries=[],
    datas=[
        ('../apps/liverig/assets', 'assets'),
        ('../apps/visual-studio/teleprompt', 'visual-studio/teleprompt'),
        ('../apps/visual-studio/video', 'visual-studio/video'),
        ('../apps/liverig/pano_de_fundo.jpg', '.'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LiveRig',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LiveRig',
)

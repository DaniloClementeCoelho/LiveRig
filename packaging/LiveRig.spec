# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import sys

from PyInstaller.utils.hooks import collect_submodules

ROOT = Path.cwd()
PYTHON_HOME = Path(sys.base_prefix)
sys.path.insert(0, str(ROOT / "apps" / "liverig"))

from version import APP_VERSION

hiddenimports = (
    collect_submodules("customtkinter")
    + collect_submodules("network")
    + collect_submodules("playback")
    + collect_submodules("visual_sync")
    + [
    "_tkinter",
    "tkinter",
    "tkinter.constants",
    "tkinter.filedialog",
    "tkinter.font",
    "tkinter.ttk",
    ]
)

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
    binaries=[
        (str(PYTHON_HOME / 'DLLs' / '_tkinter.pyd'), '.'),
        (str(PYTHON_HOME / 'DLLs' / 'tcl86t.dll'), '.'),
        (str(PYTHON_HOME / 'DLLs' / 'tk86t.dll'), '.'),
    ],
    datas=[
        (str(PYTHON_HOME / 'Lib' / 'tkinter'), 'tkinter'),
        (str(PYTHON_HOME / 'tcl' / 'tcl8.6'), '_tcl_data'),
        (str(PYTHON_HOME / 'tcl' / 'tk8.6'), '_tk_data'),
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
    name=f'LiveRig-v{APP_VERSION}',
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

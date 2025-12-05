# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Silhouette Card Maker
This creates a standalone executable with all dependencies bundled.
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Get the project root directory
root_dir = Path('.').absolute()

# Collect all submodules for critical packages
requests_imports = collect_all('requests')
urllib3_imports = collect_all('urllib3')

# Data files to include
datas = [
    ('assets', 'assets'),
    ('calibration', 'calibration'),
    ('cutting_templates', 'cutting_templates'),
    ('plugins', 'plugins'),
    ('gui/utils', 'gui/utils'),
]

# Add collected data files
datas += requests_imports[0]
datas += urllib3_imports[0]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'requests',
    'pypdfium2',
    'json',
    'queue',
    'threading',
    'pathlib',
    'tempfile',
    'shutil',
    'io',
    'base64',
    'click',
    'natsort',
    'numpy',
    'pydantic',
    'split_image',
    'filetype',
    # Plugin imports
    'plugins.plugin_manager',
    'plugins.mtg.deck_formats',
    'plugins.mtg.scryfall',
    'plugins.mtg.download_manager',
    # GUI utilities
    'gui.utils.settings_manager',
    'gui.utils.styles',
]

# Add collected hidden imports
hiddenimports += requests_imports[1]
hiddenimports += urllib3_imports[1]

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    module_collection_mode={
        'requests': 'py',  # Collect all requests modules
        'urllib3': 'py',   # Requests dependency
        'PIL': 'py',       # Pillow
        'pypdfium2': 'py', # PDF library
    }
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SilhouetteCardMaker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you create one: icon='assets/icon.ico'
)

# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT, BUNDLE

# Definir diretório base
block_cipher = None
base_path = os.path.abspath(os.path.dirname(__file__))

# Adicionar caminhos de dados e arquivos necessários
data_files = [
    # Pasta static completa
    ('static', 'static'),
    # Pasta templates completa
    ('templates', 'templates'),
    # Pasta blueprints completa
    ('blueprints', 'blueprints'),
    # Pasta uploads
    ('uploads', 'uploads'),
    # Pasta utils
    ('utils', 'utils'),
    # Pasta instance (para banco de dados SQLite se for usado)
    ('instance', 'instance'),
]

# Incluir arquivos importantes
added_files = []
for src, dst in data_files:
    added_files.append((src, dst))

a = Analysis(
    ['zelopack_app.py'],
    pathex=[base_path],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'flask',
        'flask_login',
        'flask_sqlalchemy',
        'sqlalchemy',
        'werkzeug',
        'jinja2',
        'email_validator',
        'flask_wtf',
        'wtforms',
        'matplotlib',
        'numpy',
        'pandas',
        'openpyxl',
        'pillow',
        'reportlab',
        'pypdf2',
        'python-docx',
        'sendgrid',
        'twilio',
        'gunicorn',
        'psycopg2-binary',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ZELOPACK',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False para esconder o console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/img/favicon.ico' if os.path.exists('static/img/favicon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ZELOPACK',
)

# Configurações específicas para diferentes plataformas
if sys.platform == 'darwin':  # macOS
    app = BUNDLE(
        coll,
        name='ZELOPACK.app',
        icon='static/img/favicon.ico' if os.path.exists('static/img/favicon.ico') else None,
        bundle_identifier='com.zelopack.laudos',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'CFBundleDisplayName': 'ZELOPACK',
            'CFBundleName': 'ZELOPACK',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHumanReadableCopyright': '© 2025 ZELOPACK. Todos os direitos reservados.',
        },
    )
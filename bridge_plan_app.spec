# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/bridge_plan_web_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('config', 'config'),
        ('data', 'data'),
        ('src/bridge_plan_generator', 'bridge_plan_generator'),
    ],
    hiddenimports=[
        'flask',
        'pandas',
        'openpyxl',
        'numpy',
        'bridge_config',
        'bridge_models',
        'bridge_plan_generator.data_loader',
        'bridge_plan_generator.sourcing_processor',
        'bridge_plan_generator.target_processor',
        'bridge_plan_generator.suppression_processor',
        'bridge_plan_generator.hierarchy_processor',
        'bridge_plan_generator.promotion_ops_calculator',
        'bridge_plan_generator.sourcing_plan_generator',
        'bridge_plan_generator.suppression_plan_generator',
        'bridge_plan_generator.bridge_plan_orchestrator',
        'bridge_plan_generator.report_generator',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BridgePlanGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pipeline.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['video_pipeline.audio_sync', 'video_pipeline.ocr_cleaning', 'video_pipeline.auto_analyse', 'video_pipeline.translation', 'video_pipeline.video_editing', 'video_pipeline.quality_control', 'video_pipeline.fallback_tools'],
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
    name='pipeline',
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

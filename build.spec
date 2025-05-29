# -*- mode: python ; coding: utf-8 -*-
import sys
import platform

# 获取当前操作系统
is_mac = platform.system() == 'Darwin'

# 基础配置
base_config = {
    'pathex': [],
    'binaries': [],
    'datas': [('config.yaml', '.'), ('app', 'app')],
    'hiddenimports': [
        'engineio.async_drivers.threading',
        'eventlet',
        'eventlet.hubs.epolls',
        'eventlet.hubs.kqueue',
        'eventlet.hubs.selects',
        'eventlet.hubs.poll',
        'eventlet.hubs.py3k',
        'eventlet.hubs.zeromq'
    ],
    'hookspath': [],
    'hooksconfig': {},
    'runtime_hooks': [],
    'excludes': [],
    'noarchive': False,
    'optimize': 0,
}

# 创建分析对象
a = Analysis(
    ['run.py'],
    **base_config
)

pyz = PYZ(a.pure)

# 根据操作系统设置不同的配置
if is_mac:
    exe_config = {
        'name': 'drea-sense-client',
        'debug': False,
        'bootloader_ignore_signals': False,
        'strip': False,
        'upx': True,
        'upx_exclude': [],
        'runtime_tmpdir': None,
        'console': True,
        'disable_windowed_traceback': False,
        'argv_emulation': True,  # 启用macOS参数模拟
        'target_arch': None,
        'codesign_identity': None,
        'entitlements_file': None,
        'icon': None,  # 如果需要图标，可以在这里指定
    }
else:
    exe_config = {
        'name': 'drea-sense-client',
        'debug': False,
        'bootloader_ignore_signals': False,
        'strip': False,
        'upx': True,
        'upx_exclude': [],
        'runtime_tmpdir': None,
        'console': True,
        'disable_windowed_traceback': False,
        'argv_emulation': False,
        'target_arch': None,
        'codesign_identity': None,
        'entitlements_file': None,
    }

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    **exe_config
)

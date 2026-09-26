# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all


PROJECT_ROOT = Path(SPECPATH)
cyipopt_datas, cyipopt_binaries, cyipopt_hiddenimports = collect_all("cyipopt")

# Conda installs IPOPT beside Python instead of inside the cyipopt package.
# PyInstaller follows most DLL dependencies; these patterns cover the rest.
conda_dlls = []
conda_bin = Path(sys.prefix) / "Library" / "bin"
for pattern in (
    "*ipopt*.dll",
    "*mumps*.dll",
    "*openblas*.dll",
    "*gfortran*.dll",
    "*quadmath*.dll",
    "*gcc_s*.dll",
):
    if conda_bin.exists():
        conda_dlls.extend((str(path), ".") for path in conda_bin.glob(pattern))

a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=cyipopt_binaries + conda_dlls,
    datas=[
        (str(PROJECT_ROOT / "app" / "files"), "app/files"),
        (str(PROJECT_ROOT / "app" / "imgs"), "app/imgs"),
        (str(PROJECT_ROOT / "thermodynamic_data.xlsx"), "."),
        (str(PROJECT_ROOT / "ico.ico"), "."),
    ] + cyipopt_datas,
    hiddenimports=cyipopt_hiddenimports,
    runtime_hooks=[str(PROJECT_ROOT / "packaging" / "runtime_hook.py")],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TeS Studio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    icon=str(PROJECT_ROOT / "ico.ico"),
)

collect = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="TeS Studio",
)

"""Prepare the PyInstaller directory for native IPOPT libraries on Windows."""

from __future__ import annotations

import os
import sys


_TES_DLL_DIRECTORIES = []

if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        for candidate in (bundle_root, os.path.join(bundle_root, "runtime")):
            if os.path.isdir(candidate):
                _TES_DLL_DIRECTORIES.append(os.add_dll_directory(candidate))

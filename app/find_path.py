"""Resource lookup that works in source checkouts and PyInstaller bundles."""

from __future__ import annotations

import sys
from pathlib import Path


def application_root() -> Path:
    """Return the read-only root containing bundled application resources."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root)
    return Path(__file__).resolve().parent.parent


def resource_path(relative_path: str) -> str:
    """Resolve a project-relative resource path as an absolute string path."""
    return str(application_root() / Path(relative_path))

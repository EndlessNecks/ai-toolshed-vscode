#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
paths.py — canonical paths for AI ToolShed runtime.

All indexing + RAG operations target ONLY:
    <INSTALL_ROOT>/workspace_files
"""

from __future__ import annotations

import json
import os
from pathlib import Path


# ------------------------------------------------------------
# Load venv_info.json
# ------------------------------------------------------------
def _load_info():
    here = Path(__file__).resolve()
    configs = here.parent
    info = configs / "venv_info.json"

    if info.exists():
        return json.loads(info.read_text())

    # Development fallback: use repo root if the installer has not run yet
    default_root = os.environ.get("AI_TOOLSHED_INSTALL_ROOT")
    if not default_root:
        default_root = here.parents[2]  # AI_ToolShed_VScode root

    return {"install_root": str(Path(default_root).resolve())}


_INFO = _load_info()


# ------------------------------------------------------------
# Install root (C:\Program Files\AI_ToolShed_VScode)
# ------------------------------------------------------------
def get_install_root() -> Path:
    return Path(_INFO["install_root"]).resolve()


# ------------------------------------------------------------
# Workspace-files ONLY root
# ------------------------------------------------------------
def get_index_root() -> Path:
    return get_install_root() / "workspace_files"


# ------------------------------------------------------------
# Qdrant storage path
# ------------------------------------------------------------
def get_qdrant_path() -> Path:
    return get_install_root() / "qdrant"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
paths.py — canonical paths for AI ToolShed runtime.

All indexing + RAG operations target ONLY:
    <INSTALL_ROOT>/workspace_files
"""

from __future__ import annotations

import json
from pathlib import Path


# ------------------------------------------------------------
# Load venv_info.json
# ------------------------------------------------------------
def _load_info():
    here = Path(__file__).resolve()
    configs = here.parent
    root = configs.parent
    info = configs / "venv_info.json"
    if not info.exists():
        raise RuntimeError("venv_info.json missing. Run setup.ps1.")
    return json.loads(info.read_text())


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

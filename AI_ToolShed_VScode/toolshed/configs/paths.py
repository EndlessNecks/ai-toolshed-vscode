"""
paths.py — Universal path resolver for AI ToolShed.

This file makes AI ToolShed fully portable:

- Installation root is determined automatically from this file’s location.
- Workspace root is determined dynamically from environment variables.
- All state (vector_db / logs / rag_state) lives INSIDE the install folder.
"""

from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Dict, Any

# -------------------------------------------------------------------
# INSTALL ROOT — NEVER HARDCODED
# -------------------------------------------------------------------
# Example resolved path:
#   C:\Program Files\AI_ToolShed_VScode\configs\paths.py
#
# install_root = C:\Program Files\AI_ToolShed_VScode
# -------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent
_INSTALL_ROOT = _THIS_DIR.parent   # C:\Program Files\AI_ToolShed_VScode\


# -------------------------------------------------------------------
# Load static defaults from paths.json
# -------------------------------------------------------------------

_PATHS_JSON = _THIS_DIR / "paths.json"
if not _PATHS_JSON.exists():
    raise FileNotFoundError(f"Missing paths.json at {_PATHS_JSON}")

with open(_PATHS_JSON, "r", encoding="utf-8") as f:
    _RAW: Dict[str, Any] = json.load(f)


# -------------------------------------------------------------------
# WORKSPACE ROOT (dynamic, user project)
# -------------------------------------------------------------------
def get_workspace_root() -> Path:
    """
    Workspace resolution rules:
    1. TOOLS_HED_WORKSPACE (set by VS Code extension)
    2. paths.json.workspace_root
    3. Default: installation root (fallback safe mode)
    """
    env = os.environ.get("TOOLS_HED_WORKSPACE", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if p.exists():
            return p

    cfg = _RAW.get("workspace_root", "").strip()
    if cfg:
        p = Path(cfg).expanduser().resolve()
        if p.exists():
            return p

    # Fallback — safe but not ideal
    return _INSTALL_ROOT


# -------------------------------------------------------------------
# PERSISTENT DATA ROOTS (system-level)
# These live INSIDE the installation directory so ToolShed is portable.
# -------------------------------------------------------------------

def _ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_db_path() -> Path:
    sub = _RAW.get("db_root", "vector_db")
    return _ensure(_INSTALL_ROOT / sub)

def get_logs_path() -> Path:
    sub = _RAW.get("logs_root", "logs")
    return _ensure(_INSTALL_ROOT / sub)

def get_rag_state_path() -> Path:
    sub = _RAW.get("rag_state_root", "rag_state")
    return _ensure(_INSTALL_ROOT / sub)


# -------------------------------------------------------------------
# Export installation root
# -------------------------------------------------------------------
def get_install_root() -> Path:
    return _INSTALL_ROOT


# -------------------------------------------------------------------
# Directory bootstrap
# -------------------------------------------------------------------
def ensure_all_dirs_exist():
    get_db_path()
    get_logs_path()
    get_rag_state_path()


# Debug output
if __name__ == "__main__":
    print("Install Root   :", get_install_root())
    print("Workspace Root :", get_workspace_root())
    print("DB Path        :", get_db_path())
    print("Logs Path      :", get_logs_path())
    print("RAG State Path :", get_rag_state_path())

"""
paths.py — Centralized path resolver for AI ToolShed RAG system.
Python 3.14 compatible, zero external dependencies except stdlib.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

# -------------------------------------------------------------
# Load raw paths.json
# -------------------------------------------------------------
_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent  # AI_ToolShed_VScode/

_PATHS_JSON = _THIS_DIR / "paths.json"

if not _PATHS_JSON.exists():
    raise FileNotFoundError(f"paths.json missing: {_PATHS_JSON}")

with open(_PATHS_JSON, "r", encoding="utf-8") as f:
    _RAW_CONFIG: Dict[str, Any] = json.load(f)


# -------------------------------------------------------------
# Environment override for workspace root (set by extension.js)
# -------------------------------------------------------------
def get_workspace_root() -> Path:
    """
    Resolves workspace root using:
    1) TOOLS_HED_WORKSPACE env var (set by VS Code extension)
    2) paths.json's workspace_root
    3) fallback: project root
    """
    env_override = os.environ.get("TOOLS_HED_WORKSPACE", "").strip()
    if env_override:
        root = Path(env_override).expanduser().resolve()
        if root.exists():
            return root

    cfg_root = _RAW_CONFIG.get("workspace_root", "").strip()
    if cfg_root:
        root_path = Path(cfg_root).expanduser().resolve()
        if root_path.exists():
            return root_path

    return _PROJECT_ROOT


# -------------------------------------------------------------
# Other system paths
# -------------------------------------------------------------
def get_db_path() -> Path:
    db_root = _RAW_CONFIG.get("db_root", "./vector_db")
    p = (get_workspace_root() / db_root).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_logs_path() -> Path:
    logs_root = _RAW_CONFIG.get("logs_root", "./logs")
    p = (get_workspace_root() / logs_root).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_rag_state_path() -> Path:
    state_root = _RAW_CONFIG.get("rag_state_root", "./rag_state")
    p = (get_workspace_root() / state_root).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


# -------------------------------------------------------------
# Generic ensure-all-directories helper
# -------------------------------------------------------------
def ensure_all_dirs_exist() -> None:
    """
    Creates all required base directories for RAG system.
    Called on startup of indexer, retriever, watcher, orchestrator.
    """
    get_db_path()
    get_logs_path()
    get_rag_state_path()


# -------------------------------------------------------------
# Expose project root for convenience
# -------------------------------------------------------------
def get_project_root() -> Path:
    return _PROJECT_ROOT


if __name__ == "__main__":
    print("PROJECT ROOT:", get_project_root())
    print("WORKSPACE ROOT:", get_workspace_root())
    print("DB PATH:", get_db_path())
    print("LOG PATH:", get_logs_path())
    print("RAG STATE:", get_rag_state_path())

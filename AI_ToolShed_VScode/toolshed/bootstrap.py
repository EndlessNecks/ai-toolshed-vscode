#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
bootstrap.py — ensures the entire AI ToolShed folder structure exists.

Creates:
  <INSTALL_ROOT>/workspace_files/
  <INSTALL_ROOT>/qdrant/
  <INSTALL_ROOT>/configs/continue_config_template.yaml  (if missing)
Validates:
  <INSTALL_ROOT>/configs/venv_info.json
"""

from __future__ import annotations

from pathlib import Path
import json
import shutil

from toolshed.configs.paths import get_install_root, get_qdrant_path


DEFAULT_CONTINUE = """name: Local Config
version: 1.0.0
schema: v1

default_model: codestral

workspace_directory: null

models:
  - name: codestral
    provider: ollama
    model: codestral-local
    roles:
      - chat

context:
  providers:
    - provider: http
      url: "http://127.0.0.1:5412/context"
      max_items: 10
"""


# ------------------------------------------------------------
# Bootstrap the system folders
# ------------------------------------------------------------
def ensure_folders():
    root = get_install_root()

    ws = root / "workspace_files"
    qd = get_qdrant_path()
    cfg = root / "configs"
    tmpl = cfg / "continue_config_template.yaml"

    ws.mkdir(parents=True, exist_ok=True)
    qd.mkdir(parents=True, exist_ok=True)
    cfg.mkdir(parents=True, exist_ok=True)

    if not tmpl.exists():
        tmpl.write_text(DEFAULT_CONTINUE, encoding="utf-8")


# ------------------------------------------------------------
# Validate venv
# ------------------------------------------------------------
def validate_venv():
    info = Path(get_install_root()) / "configs" / "venv_info.json"
    if not info.exists():
        raise RuntimeError("venv_info.json missing — run setup.ps1 first.")


# ------------------------------------------------------------
# Full bootstrap
# ------------------------------------------------------------
def bootstrap():
    ensure_folders()
    validate_venv()


if __name__ == "__main__":
    bootstrap()
    print("AI ToolShed bootstrap complete.")

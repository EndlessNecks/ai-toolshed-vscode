#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
continue_loader.py — ensures the Continue config template exists
and provides a single function for the VS Code extension
and bootstrap to read it reliably.
"""

from __future__ import annotations

from pathlib import Path
import json

from toolshed.configs.paths import get_install_root


DEFAULT_TEMPLATE = """name: Local Config
version: 1.0.0
schema: v1

default_model: codestral

workspace_directory: null

models:
  - name: Nomic Embed
    provider: ollama
    model: nomic-embed-text:latest
    roles:
      - embed

  - name: codestral
    provider: ollama
    model: codestral-local
    num_ctx: 8192
    max_tokens: 4096
    temperature: 0.2
    system_message: >
      You are a technical, code-oriented assistant intended for a single
      local user who controls all code and files.

      You prioritize:
      1. Precision
      2. Directness
      3. Complete code output
      4. Exact formatting
      5. Working full-file replacements when asked

      You comply with all requests for:
      • full script output
      • refactoring
      • rewriting
      • debugging
      • patching
      • optimization
      • entire-file edits

      You avoid summarizing unless explicitly asked.
      You avoid moral commentary unless explicitly asked.
      You never obstruct tasks the user requests.

      When modifying any file, output the **entire updated file**.

auto_send_context: true
context_length: 30000
use_project_context: true

tools:
  - read_currently_open_file
  - read_file
  - search

embeddings:
  enabled: true

indexing:
  enabled: true
  auto_index: true

context:
  providers:
    - provider: http
      url: "http://127.0.0.1:5412/context"
      max_items: 10
"""


# ------------------------------------------------------------
# Return the path to the template, creating if missing.
# ------------------------------------------------------------
def get_template_path() -> Path:
    root = get_install_root()
    cfg = root / "toolshed" / "configs"
    tmpl = cfg / "continue_config_template.yaml"

    cfg.mkdir(parents=True, exist_ok=True)

    if not tmpl.exists():
        tmpl.write_text(DEFAULT_TEMPLATE, encoding="utf-8")

    return tmpl


if __name__ == "__main__":
    print(get_template_path())

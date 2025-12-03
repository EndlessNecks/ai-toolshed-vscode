#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
chunker.py — Splits project files into small text chunks.
"""

import os
import sys
import re

# ---------------------------------------------
# FIXED: Ensure rag_engine + configs import works
# ---------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLSHED_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if TOOLSHED_ROOT not in sys.path:
    sys.path.insert(0, TOOLSHED_ROOT)

# ---------------------------------------------

TEXT_EXTENSIONS = {".py", ".js", ".ts", ".json", ".md", ".txt", ".html", ".css"}

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None


def split_into_chunks(text, path):
    lines = text.split("\n")
    chunks = []

    i = 0
    while i < len(lines):
        part = lines[i:i + CHUNK_SIZE]
        content = "\n".join(part)

        chunks.append({
            "source_path": path,
            "content": content,
            "start_line": i + 1,
            "end_line": i + len(part),
        })

        i += (CHUNK_SIZE - CHUNK_OVERLAP)

    return chunks


def chunk_directory(root_dir):
    all_chunks = []

    for base, dirs, files in os.walk(root_dir):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext not in TEXT_EXTENSIONS:
                continue

            full = os.path.join(base, f)
            text = read_file(full)
            if not text:
                continue

            chunks = split_into_chunks(text, full)
            all_chunks.extend(chunks)

    return all_chunks


if __name__ == "__main__":
    import json
    from configs.paths import PROJECT_ROOT

    out = chunk_directory(PROJECT_ROOT)
    print(json.dumps(out[:3], indent=2))

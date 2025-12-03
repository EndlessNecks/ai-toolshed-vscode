#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
chunker.py — safe file reader + text chunking
ONLY for:
    <INSTALL_ROOT>/workspace_files
"""

from __future__ import annotations

import chardet
from pathlib import Path
from typing import List

from rag_engine.indexer import get_index_root


# ------------------------------------------------------------
# Read file safely with encoding detection
# ------------------------------------------------------------
def read_file_safely(path: Path) -> str:
    root = get_index_root()

    # Reject files outside workspace_files
    try:
        path.resolve().relative_to(root)
    except ValueError:
        return ""

    try:
        raw = path.read_bytes()
    except Exception:
        return ""

    enc = chardet.detect(raw).get("encoding") or "utf-8"

    try:
        return raw.decode(enc, errors="ignore")
    except Exception:
        return ""


# ------------------------------------------------------------
# Chunk object
# ------------------------------------------------------------
class Chunk:
    def __init__(self, text: str, start: int, end: int):
        self.text = text
        self.start = start
        self.end = end


# ------------------------------------------------------------
# Chunking logic
# ------------------------------------------------------------
def chunk_text(text: str, max_len: int = 512, overlap: int = 64) -> List[Chunk]:
    if not text:
        return []

    out = []
    start = 0
    end = max_len

    while start < len(text):
        segment = text[start:end]
        out.append(Chunk(segment, start, end))
        start = end - overlap
        end = start + max_len

    return out


# ------------------------------------------------------------
# Chunk a file
# ------------------------------------------------------------
def chunk_file(path: Path) -> List[Chunk]:
    content = read_file_safely(path)
    if not content:
        return []

    return chunk_text(content)


if __name__ == "__main__":
    test_path = Path(get_index_root()) / "test.txt"
    print(chunk_file(test_path))

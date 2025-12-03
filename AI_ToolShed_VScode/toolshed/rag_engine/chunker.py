#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chunker.py — File reading + text chunking engine for AI ToolShed RAG.
Python 3.14 compatible.

Responsibilities:
  - Safely read files (chardet)
  - Normalize text (line endings, null stripping)
  - Chunk text into overlapping windows
  - Yield Chunk objects with metadata
  - Iterate project files based on include/exclude globs

No external dependencies except:
  - chardet
  - pathlib
  - typing
  - configs.paths
"""

from __future__ import annotations

import chardet
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Sequence, Any

from configs.paths import get_workspace_root


# ============================================================
# Data Structure
# ============================================================

@dataclass
class Chunk:
    """
    Represents a piece of text with metadata attached.
    The indexer + retriever will reuse this structure.
    """
    text: str
    metadata: Dict[str, Any]


# ============================================================
# File Reading Utilities
# ============================================================

def read_file_safely(path: Path) -> str:
    """
    Safely read file with chardet detection + fallback.
    - Detect encoding on raw bytes
    - Decode with 'replace' for bad bytes
    - Normalize line endings
    - Strip NULL characters
    """
    try:
        raw = path.read_bytes()
    except Exception:
        return ""

    detection = chardet.detect(raw)
    encoding = detection.get("encoding") or "utf-8"

    try:
        text = raw.decode(encoding, errors="replace")
    except Exception:
        text = raw.decode("utf-8", errors="replace")

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove null bytes
    text = text.replace("\x00", "")

    return text


# ============================================================
# Chunking Logic
# ============================================================

def chunk_text(
    text: str,
    *,
    chunk_size: int,
    overlap: int,
) -> List[str]:
    """
    Produce overlapping character-based chunks.

    Example:
      chunk_size=1200, overlap=200
      Window 1: [0:1200]
      Window 2: [1000:2200]
      Window 3: [2000:3200]
      etc.

    Returns list[str].
    """
    if not text:
        return []

    assert chunk_size > 0
    assert overlap >= 0
    assert overlap < chunk_size

    chunks = []
    length = len(text)

    start = 0
    while start < length:
        end = start + chunk_size
        chunk = text[start:end]

        # Clean chunk
        chunk = chunk.strip()
        if chunk:
            chunks.append(chunk)

        # Move window forward
        start += (chunk_size - overlap)

    return chunks


# ============================================================
# File iteration
# ============================================================

def iter_workspace_files(
    include_globs: Sequence[str],
    exclude_globs: Sequence[str],
) -> Iterator[Path]:
    """
    Yield paths to files inside the workspace that match include globs
    and do NOT match exclude globs.
    """
    workspace = get_workspace_root()

    # Resolve all include patterns
    included_files: List[Path] = []
    for pattern in include_globs:
        included_files.extend(workspace.glob(pattern))

    # Convert exclude patterns to concrete paths
    excluded: List[Path] = []
    for pattern in exclude_globs:
        excluded.extend(workspace.glob(pattern))

    excluded_set = {p.resolve() for p in excluded}

    for p in included_files:
        rp = p.resolve()
        # Skip directories
        if rp.is_dir():
            continue
        if rp in excluded_set:
            continue
        yield rp


# ============================================================
# Chunk generation for a single file
# ============================================================

def yield_chunks_for_file(
    path: Path,
    *,
    chunk_size: int,
    overlap: int,
) -> Iterator[Chunk]:
    """
    Yield Chunk objects for a single file.
    Metadata includes:
      - file_path: relative to workspace
      - chunk_index
      - line_start (approx)
      - line_end (approx)
    """
    workspace = get_workspace_root()
    relpath = path.resolve().relative_to(workspace)

    text = read_file_safely(path)
    if not text:
        return

    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)

    # Precompute line boundaries for approximate mapping
    # This does NOT guarantee exact match for overlapping chunks.
    # But it's useful for Continue context descriptions.
    lines = text.split("\n")
    cumulative_chars = 0
    line_starts = []
    for i, line in enumerate(lines):
        line_starts.append(cumulative_chars)
        cumulative_chars += len(line) + 1

    def approx_line_no(char_index: int) -> int:
        # Find nearest line number
        for i in range(len(line_starts) - 1):
            if line_starts[i] <= char_index < line_starts[i + 1]:
                return i + 1
        return len(line_starts)

    # Yield each chunk with metadata
    for idx, chunk in enumerate(chunks):
        # Estimate where this chunk starts in the original text
        start_char = idx * (chunk_size - overlap)
        line_start = approx_line_no(start_char)
        line_end = approx_line_no(start_char + len(chunk))

        yield Chunk(
            text=chunk,
            metadata={
                "file_path": str(relpath),
                "chunk_index": idx,
                "line_start": line_start,
                "line_end": line_end,
            }
        )


# ============================================================
# Manual test support
# ============================================================

if __name__ == "__main__":
    print("[chunker] Self-test:")
    workspace = get_workspace_root()
    print("Workspace:", workspace)

    # Quick test: list .py files
    for p in iter_workspace_files(["**/*.py"], ["**/__pycache__/**"]):
        print("File:", p)
        for ch in yield_chunks_for_file(p, chunk_size=400, overlap=100):
            print(f" - Chunk #{ch.metadata['chunk_index']} ({ch.metadata['line_start']}–{ch.metadata['line_end']})")
        break
    print("OK.")

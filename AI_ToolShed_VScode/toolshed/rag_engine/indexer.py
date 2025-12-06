#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
indexer.py — indexes ONLY the folder:
    <INSTALL_ROOT>/workspace_files

All other directories are ignored.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from qdrant_client.http import models as qmodels

from configs.paths import get_install_root
from rag_engine.embedder import embed_texts
from rag_engine.chunker import chunk_file
from rag_engine.qdrant_init import (
    get_client,
    ensure_collection,
    COLLECTION_NAME,
)


# ------------------------------------------------------------
# Absolute indexing root: INSTALL_ROOT/workspace_files
# ------------------------------------------------------------
def get_index_root() -> Path:
    env_root = os.environ.get("TOOLS_HED_WORKSPACE")
    if env_root:
        return Path(env_root).resolve()

    return Path(get_install_root()) / "workspace_files"


# ------------------------------------------------------------
# Hash file path → stable point IDs
# ------------------------------------------------------------
def _file_hash(path: Path) -> str:
    return hashlib.md5(str(path).encode("utf-8")).hexdigest()


# ------------------------------------------------------------
# Delete existing vectors for file
# ------------------------------------------------------------
def delete_file(path: Path):
    root = get_index_root()
    rel = str(path.resolve().relative_to(root))

    client = get_client()
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=qmodels.FilterSelector(
            filter=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="file_path",
                        match=qmodels.MatchValue(value=rel)
                    )
                ]
            )
        )
    )


# ------------------------------------------------------------
# Index a single file inside workspace_files
# ------------------------------------------------------------
def reindex_single_file(path: Path):
    ensure_collection()
    root = get_index_root()

    # If file removed → clear entries
    if not path.exists():
        delete_file(path)
        return

    # Path must be inside workspace_files
    try:
        rel = str(path.resolve().relative_to(root))
    except ValueError:
        return  # ignore anything outside workspace_files

    # purge old entries
    delete_file(path)

    chunks = chunk_file(path)
    if not chunks:
        return

    texts = [c.text for c in chunks]
    vectors = embed_texts(texts)

    client = get_client()
    base = _file_hash(path)

    point_ids = [f"{base}_{i}" for i in range(len(chunks))]

    points = []
    for pid, vec, ch in zip(point_ids, vectors, chunks):
        points.append(
            qmodels.PointStruct(
                id=pid,
                vector=vec,
                payload={
                    "file_path": rel,
                    "start": ch.start,
                    "end": ch.end,
                    "text": ch.text
                }
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)


# ------------------------------------------------------------
# Full index build — ONLY workspace_files
# ------------------------------------------------------------
def build_full_index():
    ensure_collection()
    root = get_index_root()

    if not root.exists():
        return

    for p in root.rglob("*"):
        if p.is_file():
            try:
                reindex_single_file(p)
            except Exception:
                continue


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI ToolShed index maintenance")
    parser.add_argument(
        "--delete",
        nargs="+",
        help="Paths under the workspace root to delete from the index",
    )

    args = parser.parse_args()

    if args.delete:
        for target in args.delete:
            path = Path(target)
            if path.is_dir():
                for p in path.rglob("*"):
                    if p.is_file():
                        delete_file(p)
            else:
                delete_file(path)

        print("Selected paths removed from the index.")
    else:
        build_full_index()
        print("Full index build complete.")

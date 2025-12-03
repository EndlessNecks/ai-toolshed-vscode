#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
indexer.py — Vector index builder for AI ToolShed RAG.
Python 3.14 compatible.

Responsibilities:
  - Traverse workspace files (via chunker.iter_workspace_files)
  - Chunk files into overlapping windows
  - Generate embeddings for each chunk
  - Store embeddings + metadata into Qdrant
  - Provide full rebuild + incremental update paths

Dependencies:
  - qdrant-client
  - numpy
  - rag_engine.chunker
  - rag_engine.embedder
  - configs.paths
"""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from configs.paths import get_db_path, get_workspace_root, get_logs_path
from rag_engine.chunker import (
    iter_workspace_files,
    yield_chunks_for_file,
    Chunk
)
from rag_engine.embedder import embed_texts


# ============================================================
# Constants
# ============================================================

COLLECTION_NAME = "toolshed_rag"


# ============================================================
# Qdrant Client Helpers
# ============================================================

def get_client() -> QdrantClient:
    """
    Returns a local file-based Qdrant instance rooted inside vector_db/.
    """
    db_path = get_db_path()
    return QdrantClient(path=str(db_path))


def ensure_collection(dimension: int) -> None:
    """
    Ensures the Qdrant collection exists.
    Recreates if schema mismatch occurs.
    """
    client = get_client()

    try:
        info = client.get_collection(COLLECTION_NAME)
        existing_dim = info.config.params.vectors.size  # type: ignore

        if existing_dim != dimension:
            # Schema mismatch → rebuild collection
            client.delete_collection(COLLECTION_NAME)
            raise Exception("Dimension mismatch, forcing recreation.")

        return

    except Exception:
        # Create a new collection
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=qm.VectorParams(
                size=dimension,
                distance=qm.Distance.COSINE
            )
        )


# ============================================================
# Indexer Core
# ============================================================

def index_chunk_batch(
    chunk_batch: List[Chunk],
    embeddings: np.ndarray,
) -> None:
    """
    Insert a batch of chunks + embeddings into Qdrant.
    """
    assert len(chunk_batch) == embeddings.shape[0], "Embedding count mismatch."

    client = get_client()

    points = []
    for chunk, emb in zip(chunk_batch, embeddings):
        points.append(
            qm.PointStruct(
                id=str(uuid.uuid4()),
                vector=emb.tolist(),
                payload=chunk.metadata
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )


def index_file(
    path: Path,
    *,
    chunk_size: int,
    overlap: int,
    batch_size: int = 32,
) -> int:
    """
    Index all chunks of a single file.
    Returns number of chunks processed.
    """
    chunks: List[Chunk] = list(yield_chunks_for_file(
        path,
        chunk_size=chunk_size,
        overlap=overlap
    ))

    if not chunks:
        return 0

    # Prepare texts
    texts = [c.text for c in chunks]

    # Embed in batches
    total_embedded = 0
    ptr = 0
    while ptr < len(texts):
        batch_texts = texts[ptr:ptr+batch_size]
        batch_chunks = chunks[ptr:ptr+batch_size]
        ptr += batch_size

        embeds = embed_texts(batch_texts, batch_size=len(batch_texts))
        index_chunk_batch(batch_chunks, embeds)
        total_embedded += len(batch_texts)

    return total_embedded


def build_full_index(
    include_globs: List[str],
    exclude_globs: List[str],
    *,
    chunk_size: int = 1200,
    overlap: int = 200,
    batch_size: int = 32,
) -> Dict[str, int]:
    """
    Full rebuild of the entire Qdrant collection.
    Returns summary: { "files_processed": X, "chunks": Y, "duration_sec": Z }
    """
    start = time.time()

    # Make a dummy embedding to determine model dimension
    test_emb = embed_texts(["dimension_probe"], batch_size=1)
    dimension = test_emb.shape[1]

    ensure_collection(dimension)

    files = list(iter_workspace_files(include_globs, exclude_globs))

    total_chunks = 0
    files_processed = 0

    for i, path in enumerate(files):
        print(f"[indexer] ({i+1}/{len(files)}) Indexing file: {path}")

        chunks = index_file(
            path,
            chunk_size=chunk_size,
            overlap=overlap,
            batch_size=batch_size
        )

        if chunks > 0:
            files_processed += 1
            total_chunks += chunks

    end = time.time()

    return {
        "files_processed": files_processed,
        "chunks": total_chunks,
        "duration_sec": round(end - start, 3)
    }


# ============================================================
# Incremental update support (optional for watcher integration)
# ============================================================

def reindex_single_file(
    path: Path,
    *,
    chunk_size: int = 1200,
    overlap: int = 200,
    batch_size: int = 32,
) -> int:
    """
    Remove all existing points for this file and re-index.
    Used by the watcher for incremental updates.
    """
    workspace = get_workspace_root()
    relpath = path.resolve().relative_to(workspace)

    client = get_client()

    # Delete all points whose payload.file_path = relpath
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=qm.Filter(
            must=[
                qm.FieldCondition(
                    key="file_path",
                    match=qm.MatchValue(value=str(relpath))
                )
            ]
        )
    )

    # Reindex fresh
    return index_file(
        path,
        chunk_size=chunk_size,
        overlap=overlap,
        batch_size=batch_size
    )


# ============================================================
# CLI Test
# ============================================================

if __name__ == "__main__":
    print("[indexer] Running manual test...")

    summary = build_full_index(
        include_globs=["**/*.py", "**/*.txt", "**/*.md"],
        exclude_globs=["**/__pycache__/**"],
        chunk_size=1200,
        overlap=200
    )

    print("[indexer] Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
retriever.py — Semantic retrieval for AI ToolShed RAG.
Python 3.14 compatible.

Responsibilities:
  - Embed natural-language queries
  - Query Qdrant for nearest chunks
  - Reconstruct Chunk objects with text + metadata
  - Provide a clean API for the orchestrator / Continue integration

Dependencies:
  - qdrant-client
  - numpy
  - rag_engine.embedder
  - rag_engine.chunker (Chunk + read_file_safely)
  - configs.paths
  - rag_engine.indexer (for get_client + COLLECTION_NAME)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from qdrant_client.http import models as qm

from configs.paths import get_workspace_root
from rag_engine.chunker import Chunk, read_file_safely
from rag_engine.embedder import embed_text
from rag_engine.indexer import get_client, COLLECTION_NAME


# ============================================================
# Helpers
# ============================================================

def _approx_snippet_from_file(
    workspace_root: Path,
    file_path: str,
    line_start: Optional[int],
    line_end: Optional[int],
) -> str:
    """
    Fallback snippet reconstruction when chunk text is not stored directly
    in Qdrant payload. Uses line_start/line_end metadata to slice the file.

    This is approximate but good enough for context injection.
    """
    abs_path = workspace_root / file_path
    if not abs_path.exists():
        return ""

    content = read_file_safely(abs_path)
    if not content:
        return ""

    lines = content.split("\n")

    # Default to full file if we have no line hints
    if line_start is None or line_end is None:
        return content

    # Clamp to valid range
    start_idx = max(line_start - 1, 0)
    end_idx = min(line_end, len(lines))

    if start_idx >= end_idx:
        return content

    return "\n".join(lines[start_idx:end_idx])


# ============================================================
# Core Retrieval API
# ============================================================

def retrieve_relevant_chunks(
    query: str,
    workspace_root: Optional[Path] = None,
    top_k: int = 10,
) -> List[Chunk]:
    """
    Retrieve top_k most relevant chunks for a natural-language query.

    - Embeds query using rag_engine.embedder
    - Searches Qdrant collection
    - Returns list[Chunk] with text + metadata (including score)

    :param query: User query / model input text.
    :param workspace_root: Optional override for workspace root, otherwise configs.paths.
    :param top_k: Number of results to return.
    """
    if not query.strip():
        return []

    if workspace_root is None:
        workspace_root = get_workspace_root()
    else:
        workspace_root = workspace_root.resolve()

    client = get_client()

    # Embed query into single vector
    query_vec = embed_text(query)  # shape (dim,)
    query_vec_list = query_vec.tolist()

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec_list,
        limit=top_k,
        with_payload=True,
    )

    chunks: List[Chunk] = []

    for res in results:
        payload: Dict[str, Any] = dict(res.payload or {})
        score = float(res.score)

        file_path = payload.get("file_path")
        line_start = payload.get("line_start")
        line_end = payload.get("line_end")

        # If we decide later to store 'text' directly in payload,
        # we prefer that, otherwise reconstruct from file.
        snippet = payload.get("text")
        if not snippet and file_path:
            snippet = _approx_snippet_from_file(
                workspace_root=workspace_root,
                file_path=file_path,
                line_start=line_start,
                line_end=line_end,
            )

        if not snippet:
            # Skip if we cannot reconstruct anything meaningful
            continue

        meta = dict(payload)
        meta["score"] = score

        chunks.append(
            Chunk(
                text=snippet,
                metadata=meta,
            )
        )

    return chunks


# ============================================================
# CLI Test
# ============================================================

if __name__ == "__main__":
    print("[retriever] Manual test")

    ws = get_workspace_root()
    print(f"[retriever] Workspace root: {ws}")

    q = input("Enter a test query: ").strip()
    if not q:
        print("Empty query, exiting.")
    else:
        hits = retrieve_relevant_chunks(q, top_k=5)
        print(f"[retriever] Retrieved {len(hits)} chunks.")
        for i, ch in enumerate(hits, 1):
            fp = ch.metadata.get("file_path", "?")
            ls = ch.metadata.get("line_start", "?")
            le = ch.metadata.get("line_end", "?")
            sc = ch.metadata.get("score", "?")
            print(f"\n--- Result #{i} ---")
            print(f"File: {fp}  ({ls}–{le})  score={sc}")
            print(ch.text[:400])
            if len(ch.text) > 400:
                print("... [truncated]")

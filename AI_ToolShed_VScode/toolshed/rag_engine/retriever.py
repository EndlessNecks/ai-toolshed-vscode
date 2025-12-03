#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
retriever.py — semantic search over ONLY:
    <INSTALL_ROOT>/workspace_files

Uses Qdrant + embedder.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from qdrant_client.http import models as qmodels

from rag_engine.embedder import embed_texts
from rag_engine.qdrant_init import (
    get_client,
    ensure_collection,
    COLLECTION_NAME,
)
from rag_engine.indexer import get_index_root


# ------------------------------------------------------------
# Chunk wrapper for clean output
# ------------------------------------------------------------
class RetrievedChunk:
    def __init__(self, text, metadata):
        self.text = text
        self.metadata = metadata


# ------------------------------------------------------------
# Retrieve top-K chunks
# ------------------------------------------------------------
def retrieve_relevant_chunks(query: str, top_k: int = 10) -> List[RetrievedChunk]:
    ensure_collection()

    client = get_client()
    vectors = embed_texts([query])
    vec = vectors[0]

    search = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vec,
        limit=top_k,
        with_payload=True
    )

    out = []
    for r in search:
        payload = r.payload or {}
        txt = payload.get("text", "")

        meta = {
            "file_path": payload.get("file_path", ""),
            "score": r.score,
            "start": payload.get("start", None),
            "end": payload.get("end", None)
        }

        out.append(RetrievedChunk(txt, meta))

    return out


if __name__ == "__main__":
    # for quick testing
    results = retrieve_relevant_chunks("test query", top_k=5)
    for r in results:
        print("----")
        print(r.metadata)
        print(r.text)

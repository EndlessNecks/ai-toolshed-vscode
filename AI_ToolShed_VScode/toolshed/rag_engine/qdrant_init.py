#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
qdrant_init.py — ensures the RAG collection exists with the correct schema.
Called automatically by indexer/retriever on first use.
"""

from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from configs.paths import get_qdrant_path


COLLECTION_NAME = "rag_chunks"
EMBED_DIM = 768  # SentenceTransformer / nomic-embed-text dimension


def get_client() -> QdrantClient:
    return QdrantClient(path=str(get_qdrant_path()))


def ensure_collection():
    client = get_client()

    existing = client.get_collections().collections
    names = [c.name for c in existing]

    if COLLECTION_NAME in names:
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=qmodels.VectorParams(
            size=EMBED_DIM,
            distance=qmodels.Distance.COSINE
        ),
        optimizers_config=qmodels.OptimizersConfigDiff(
            indexing_interval=10000
        ),
        hnsw_config=qmodels.HnswConfigDiff(
            m=32,
            ef_construct=200
        )
    )


if __name__ == "__main__":
    ensure_collection()
    print(f"Collection '{COLLECTION_NAME}' ensured.")

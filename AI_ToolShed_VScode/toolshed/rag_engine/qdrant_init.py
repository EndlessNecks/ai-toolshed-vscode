#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
qdrant_init.py — local, file-based Qdrant bootstrapper.

Creates and caches an on-disk Qdrant instance under the install root and
guarantees a single collection schema for workspace embeddings.
"""

from __future__ import annotations

from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from configs.paths import get_qdrant_path


COLLECTION_NAME = "workspace_chunks"

# NOTE: sentence-transformers/all-MiniLM-L6-v2 → 384 dims
_VECTOR_SIZE = 384

_client: QdrantClient | None = None


# ------------------------------------------------------------
# Singleton client pointing at local storage
# ------------------------------------------------------------
def get_client() -> QdrantClient:
    global _client

    if _client is not None:
        return _client

    path = Path(get_qdrant_path())
    path.mkdir(parents=True, exist_ok=True)

    _client = QdrantClient(path=str(path))
    return _client


# ------------------------------------------------------------
# Ensure the collection exists with the expected schema
# ------------------------------------------------------------
def ensure_collection():
    client = get_client()

    try:
        client.get_collection(COLLECTION_NAME)
        return
    except Exception:
        pass

    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=qmodels.VectorParams(
            size=_VECTOR_SIZE,
            distance=qmodels.Distance.COSINE,
        ),
    )

    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="file_path",
        field_schema=qmodels.PayloadSchemaType.KEYWORD,
    )


if __name__ == "__main__":
    ensure_collection()
    print("Qdrant collection ready at", get_qdrant_path())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
indexer.py — rebuilds Qdrant index
"""

import os
import sys
import json
from typing import List, Dict, Any

# ---------------------------------------------
# FIXED: sys.path so configs + rag_engine imports work
# ---------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLSHED_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if TOOLSHED_ROOT not in sys.path:
    sys.path.insert(0, TOOLSHED_ROOT)
# ---------------------------------------------

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

from configs.paths import PROJECT_ROOT, VECTOR_INDEX_PATH
from rag_engine.chunker import chunk_directory
from rag_engine.embedder import Embedder


COLLECTION_NAME = "tool_shed_index"
BATCH_SIZE = 32


def build_index(source_dir: str = PROJECT_ROOT, index_path: str = VECTOR_INDEX_PATH):
    print(f"[indexer] Source directory: {source_dir}")
    print(f"[indexer] Vector DB path: {index_path}")

    os.makedirs(index_path, exist_ok=True)

    client = QdrantClient(path=index_path, prefer_grpc=False)

    # Recreate collection safely using up-to-date API
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=768,
            distance=Distance.COSINE,
        )
    )

    chunks = chunk_directory(source_dir)
    total = len(chunks)
    print(f"[indexer] Total chunks: {total}")

    embedder = Embedder()
    next_id = 0

    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["content"] for c in batch]

        embeddings = embedder.embed_batch(texts)

        payloads = []
        for c in batch:
            payloads.append({
                "source": c["source_path"],
                "start_line": c.get("start_line"),
                "end_line": c.get("end_line"),
                "content": c["content"],
            })

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=next_id + j,
                    vector=embeddings[j],
                    payload=payloads[j],
                )
                for j in range(len(batch))
            ]
        )

        next_id += len(batch)
        print(f"[indexer] Embedded {next_id}/{total} chunks…", end="\r")

    print("\n[indexer] Index build complete!")
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default=PROJECT_ROOT)
    parser.add_argument("--index", default=VECTOR_INDEX_PATH)
    args = parser.parse_args()
    build_index(args.src, args.index)

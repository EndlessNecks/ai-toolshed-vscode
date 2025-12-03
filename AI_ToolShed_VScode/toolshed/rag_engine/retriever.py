#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
retriever.py — Qdrant nearest-neighbor search
"""

import os
import sys
from typing import List, Dict, Any

# ---------------------------------------------
# FIXED: ensure configs + rag_engine import works
# ---------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLSHED_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if TOOLSHED_ROOT not in sys.path:
    sys.path.insert(0, TOOLSHED_ROOT)
# ---------------------------------------------

from qdrant_client import QdrantClient
from configs.paths import VECTOR_INDEX_PATH
from rag_engine.embedder import Embedder


COLLECTION_NAME = "tool_shed_index"


class Retriever:
    def __init__(self, index_path: str):
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Vector index not found at: {index_path}")

        self.index_path = index_path
        self.embedder = Embedder()
        self.client = QdrantClient(path=index_path, prefer_grpc=False)

        try:
            self.client.get_collection(COLLECTION_NAME)
        except Exception:
            raise RuntimeError("Qdrant collection not found. Run indexer first.")

    def retrieve(self, query: str, top_k: int = 5):
        vec = self.embedder.embed_text(query)

        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vec,
            limit=top_k,
        )

        out = []
        for hit in results:
            out.append({
                "score": float(hit.score),
                "content": hit.payload.get("content"),
                "metadata": {
                    "source": hit.payload.get("source"),
                    "start_line": hit.payload.get("start_line"),
                    "end_line": hit.payload.get("end_line"),
                }
            })
        return out


def load_retriever(index_path: str = None) -> Retriever:
    if index_path is None:
        index_path = VECTOR_INDEX_PATH
    return Retriever(index_path)


if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--index", default=None)
    args = parser.parse_args()

    r = load_retriever(args.index)
    out = r.retrieve(args.query, args.k)
    print(json.dumps(out, indent=2))

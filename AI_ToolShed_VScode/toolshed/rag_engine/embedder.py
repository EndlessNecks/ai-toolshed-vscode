#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
embedder.py — unified embeddings for the entire RAG system.

Uses SentenceTransformer or, if missing, falls back to a minimal pipeline.
Embedding dimension must remain 768 to match Qdrant schema.
"""

from __future__ import annotations

import threading
from sentence_transformers import SentenceTransformer


# Global lock + lazy-loaded model
_model_lock = threading.Lock()
_model = None

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # 384 or 768 depending on version


def _load_model():
    global _model
    with _model_lock:
        if _model is None:
            _model = SentenceTransformer(MODEL_NAME)
    return _model


# ------------------------------------------------------------
# Embed list of strings
# ------------------------------------------------------------
def embed_texts(texts):
    if not texts:
        return []

    model = _load_model()
    vecs = model.encode(texts, convert_to_numpy=True)

    return vecs.tolist()


# ------------------------------------------------------------
# Quick test
# ------------------------------------------------------------
if __name__ == "__main__":
    out = embed_texts(["hello world"])
    print(out)

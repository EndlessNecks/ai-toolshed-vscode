#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
embedder.py — Provides embedding (Ollama → HF fallback)
"""

import os
import sys
import requests
import numpy as np

# ---------------------------------------------
# Ensure imports work from inside VSIX venv
# ---------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLSHED_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if TOOLSHED_ROOT not in sys.path:
    sys.path.insert(0, TOOLSHED_ROOT)
# ---------------------------------------------

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


# --------------------------------------------------------------
# OLLAMA GPU EMBEDDINGS (one request per text = correct behavior)
# --------------------------------------------------------------
def embed_with_ollama(texts):
    results = []
    for t in texts:
        try:
            r = requests.post(
                "http://localhost:11434/api/embeddings",
                json={"model": "nomic-embed-text", "input": [t]},  # <— FIXED
                timeout=30,
            )
            r.raise_for_status()

            data = r.json()
            if "embedding" in data and len(data["embedding"]) > 0:
                vec = data["embedding"]
            elif "data" in data and len(data["data"]) > 0:
                vec = data["data"][0]["embedding"]
            else:
                raise ValueError(f"Unexpected Ollama format: {data}")

            results.append(vec)

        except Exception as e:
            print(f"[Embedder] Ollama failed on text '{t[:30]}...': {e}")
            return None

    return results


# --------------------------------------------------------------
# HF FALLBACK — MUST BE 768 DIM (same as nomic-embed-text)
# --------------------------------------------------------------
def embed_with_hf(texts):
    if SentenceTransformer is None:
        return None
    try:
        model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        emb = model.encode(texts, convert_to_numpy=True)
        return emb.tolist()
    except Exception as e:
        print(f"[Embedder] HF failed: {e}")
        return None


# --------------------------------------------------------------
# MAIN UNIFIED EMBEDDER
# --------------------------------------------------------------
def embed_texts(text_list):
    out = embed_with_ollama(text_list)
    if out is None:
        out = embed_with_hf(text_list)
    if out is None:
        raise RuntimeError("No embedding backend available")

    final = []
    for text, vec in zip(text_list, out):
        v = np.array(vec, dtype=np.float32)
        n = np.linalg.norm(v)
        if n > 0:
            v /= n
        final.append({"text": text, "embedding": v.tolist()})
    return final


def embed_single(text):
    return embed_texts([text])[0]


class Embedder:
    def embed_batch(self, texts):
        return [x["embedding"] for x in embed_texts(texts)]

    def embed_text(self, text):
        return embed_single(text)["embedding"]


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(embed_single(" ".join(sys.argv[1:])))
    else:
        print("usage: python embedder.py \"text\"")

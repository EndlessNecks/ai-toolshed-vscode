#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
embedder.py — Embedding layer for AI ToolShed RAG.

- Uses sentence-transformers + torch
- Automatically picks GPU if available (CUDA/ROCm or MPS) else CPU
- Provides simple helpers:
    * get_model()
    * embed_text()
    * embed_texts()

Dependencies (already in requirements.txt):
    - torch
    - sentence-transformers
    - numpy
"""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import List, Sequence

import numpy as np

try:
    import torch
except ImportError as e:  # pragma: no cover - hard failure
    raise RuntimeError(
        "torch is required for embedder.py but is not installed. "
        "Make sure 'torch' is in rag_engine/requirements.txt and rerun setup."
    ) from e

try:
    from sentence_transformers import SentenceTransformer
except ImportError as e:  # pragma: no cover - hard failure
    raise RuntimeError(
        "sentence-transformers is required for embedder.py but is not installed. "
        "Make sure 'sentence-transformers' is in rag_engine/requirements.txt and rerun setup."
    ) from e


# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

# Default model; can be overridden via env without touching code
_DEFAULT_MODEL_NAME = (
    os.environ.get("TOOLS_HED_EMBED_MODEL")
    or "sentence-transformers/all-MiniLM-L6-v2"
)

# Thread-safe singleton
_MODEL_LOCK = threading.Lock()
_MODEL: SentenceTransformer | None = None

# Optional: cache device string
_DEVICE: str | None = None


# -------------------------------------------------------------------
# Device resolution
# -------------------------------------------------------------------
def _resolve_device() -> str:
    """
    Decide which device to run embeddings on.

    Priority:
      1. TOOLS_HED_EMBED_DEVICE env var (e.g. "cuda", "cuda:0", "cpu")
      2. torch.cuda.is_available()  -> "cuda"
      3. torch.backends.mps.is_available() -> "mps"
      4. Fallback "cpu"

    Works with CUDA *and* ROCm builds of PyTorch, since they both report as "cuda".
    """
    env_device = os.environ.get("TOOLS_HED_EMBED_DEVICE", "").strip()
    if env_device:
        return env_device

    if torch.cuda.is_available():
        return "cuda"

    # macOS Metal (not your use case but harmless)
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():  # type: ignore[attr-defined]
        return "mps"

    return "cpu"


# -------------------------------------------------------------------
# Model loading
# -------------------------------------------------------------------
def get_model() -> SentenceTransformer:
    """
    Lazily load and return the global SentenceTransformer model.
    Safe to call from multiple threads.
    """
    global _MODEL, _DEVICE

    if _MODEL is not None:
        return _MODEL

    with _MODEL_LOCK:
        if _MODEL is not None:
            return _MODEL

        model_name = _DEFAULT_MODEL_NAME
        device = _resolve_device()
        _DEVICE = device

        # NOTE: SentenceTransformer will move to device automatically if given.
        # For ROCm builds, 'cuda' is the correct device string.
        print(f"[embedder] Loading model '{model_name}' on device '{device}'...")
        model = SentenceTransformer(model_name, device=device)
        _MODEL = model
        print("[embedder] Model loaded successfully.")

        return _MODEL


# -------------------------------------------------------------------
# Embedding helpers
# -------------------------------------------------------------------
def embed_texts(
    texts: Sequence[str],
    *,
    batch_size: int = 32,
    normalize: bool = True,
    show_progress: bool = False,
) -> np.ndarray:
    """
    Embed a list of texts into a 2D numpy array of shape (n_texts, dim).

    :param texts: Sequence of strings to embed.
    :param batch_size: Batch size for encoding.
    :param normalize: If True, L2-normalize embeddings (recommended for cosine distance).
    :param show_progress: If True, show a progress bar (tqdm) during encoding.
    :return: np.ndarray of shape (len(texts), embedding_dim)
    """
    if not texts:
        return np.zeros((0, 0), dtype=np.float32)

    model = get_model()
    # SentenceTransformers handles batching internally.
    embeddings = model.encode(
        list(texts),
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=normalize,
        show_progress_bar=show_progress,
    )

    # Ensure dtype is float32 for compatibility with most vector DBs
    if embeddings.dtype != np.float32:
        embeddings = embeddings.astype(np.float32)

    return embeddings


def embed_text(
    text: str,
    *,
    normalize: bool = True,
) -> np.ndarray:
    """
    Convenience wrapper to embed a single text.

    :param text: Input string.
    :param normalize: If True, L2-normalize embedding.
    :return: np.ndarray of shape (embedding_dim,)
    """
    if not text:
        # Return a single zero vector if empty; indexer can decide to skip later.
        emb = embed_texts([""], normalize=normalize)
    else:
        emb = embed_texts([text], normalize=normalize)

    # embed_texts() returns (1, dim); we want (dim,)
    return emb[0]


# -------------------------------------------------------------------
# Small self-test
# -------------------------------------------------------------------
def _self_test() -> None:
    """
    Quick sanity check when running this file directly:
      python -m rag_engine.embedder
    """
    print("[embedder] Running self-test...")
    model = get_model()
    print(f"[embedder] Model device: {_DEVICE}")
    print(f"[embedder] Model: {type(model).__name__}")

    sample_texts = [
        "def hello_world(): print('hello')",
        "Qdrant is a vector database used for semantic search.",
    ]
    embs = embed_texts(sample_texts, batch_size=2, show_progress=False)
    print(f"[embedder] Embedded shape: {embs.shape}")
    print("[embedder] Self-test OK.")


if __name__ == "__main__":
    _self_test()

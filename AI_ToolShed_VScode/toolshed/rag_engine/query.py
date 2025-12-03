#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
query.py — CLI interface for querying the local RAG retriever.

Usage:
    python -m rag_engine.query "your question here" 5
"""

from __future__ import annotations
import sys
import json

from rag_engine.retriever import retrieve_relevant_chunks


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python -m rag_engine.query <query> [top_k]"}))
        return

    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    chunks = retrieve_relevant_chunks(query, top_k=top_k)

    out = []
    for ch in chunks:
        out.append({
            "file": ch.metadata.get("file_path"),
            "text": ch.text,
            "score": ch.metadata.get("score", None)
        })

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

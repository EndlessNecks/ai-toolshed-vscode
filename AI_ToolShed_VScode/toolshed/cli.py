#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cli.py — unified command-line interface for AI ToolShed.

Commands:
    ai-toolshed bootstrap
    ai-toolshed rebuild
    ai-toolshed index
    ai-toolshed query "text" [top_k]
    ai-toolshed watch
    ai-toolshed serve
"""

from __future__ import annotations

import sys
from pathlib import Path

from toolshed.bootstrap import bootstrap
from rag_engine.indexer import build_full_index, reindex_single_file, get_index_root
from rag_engine.retriever import retrieve_relevant_chunks
from rag_engine.watcher import start_watcher
from rag_engine.orchestrator import run as run_orchestrator


USAGE = """Usage:
  ai-toolshed bootstrap
  ai-toolshed rebuild
  ai-toolshed index
  ai-toolshed query "text" [top_k]
  ai-toolshed watch
  ai-toolshed serve
"""


def cmd_bootstrap():
    bootstrap()
    print("Bootstrap complete.")


def cmd_rebuild():
    build_full_index()
    print("Full index rebuilt.")


def cmd_index():
    root = get_index_root()
    for p in root.rglob("*"):
        if p.is_file():
            try:
                reindex_single_file(p)
            except Exception:
                pass
    print("Index updated.")


def cmd_query(args):
    if not args:
        print(USAGE)
        return

    query = args[0]
    top_k = int(args[1]) if len(args) > 1 else 5

    chunks = retrieve_relevant_chunks(query, top_k)
    for c in chunks:
        print("-----")
        print(f"FILE: {c.metadata.get('file_path')}")
        print(f"SCORE: {c.metadata.get('score')}")
        print(c.text)


def cmd_watch():
    start_watcher()


def cmd_serve():
    run_orchestrator()


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        return

    cmd = sys.argv[1].lower()

    if cmd == "bootstrap":
        cmd_bootstrap()
    elif cmd == "rebuild":
        cmd_rebuild()
    elif cmd == "index":
        cmd_index()
    elif cmd == "query":
        cmd_query(sys.argv[2:])
    elif cmd == "watch":
        cmd_watch()
    elif cmd == "serve":
        cmd_serve()
    else:
        print(USAGE)


if __name__ == "__main__":
    main()

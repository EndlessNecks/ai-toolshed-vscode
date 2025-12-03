#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
watcher.py — watches the workspace and updates the RAG index.
Minimal, clean, no extra noise.
"""

from __future__ import annotations

import time
from pathlib import Path
from threading import Thread

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent, FileMovedEvent

from configs.paths import get_workspace_root
from rag_engine.indexer import reindex_single_file, get_client, COLLECTION_NAME
from rag_engine.chunker import read_file_safely


# ------------------------------------------------------------
# Delete all points for a removed file
# ------------------------------------------------------------
def delete_file_from_index(path: Path):
    workspace = get_workspace_root()
    rel = path.resolve().relative_to(workspace)

    client = get_client()
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector={
            "filter": {
                "must": [
                    {"key": "file_path", "match": {"value": str(rel)}}
                ]
            }
        }
    )


# ------------------------------------------------------------
# Watcher event handler
# ------------------------------------------------------------
class RAGEventHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.workspace = get_workspace_root()

    def _valid(self, path: Path) -> bool:
        p = path.resolve()
        if p.is_dir():
            return False
        if any(x in p.parts for x in [
            ".git", "__pycache__", "node_modules", ".venv"
        ]):
            return False
        return True

    def on_created(self, event: FileCreatedEvent):
        p = Path(event.src_path)
        if self._valid(p):
            reindex_single_file(p)

    def on_modified(self, event: FileModifiedEvent):
        p = Path(event.src_path)
        if self._valid(p):
            reindex_single_file(p)

    def on_deleted(self, event: FileDeletedEvent):
        p = Path(event.src_path)
        if self._valid(p):
            delete_file_from_index(p)

    def on_moved(self, event: FileMovedEvent):
        old = Path(event.src_path)
        new = Path(event.dest_path)

        if self._valid(old):
            delete_file_from_index(old)
        if self._valid(new):
            reindex_single_file(new)


# ------------------------------------------------------------
# Runner
# ------------------------------------------------------------
def start_watcher():
    workspace = get_workspace_root()
    handler = RAGEventHandler()
    observer = Observer()
    observer.schedule(handler, str(workspace), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    start_watcher()

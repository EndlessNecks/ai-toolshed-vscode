#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
watcher.py — watches ONLY:
    <INSTALL_ROOT>/workspace_files

Triggers incremental reindexing ONLY for that folder.
"""

from __future__ import annotations

import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    FileModifiedEvent,
    FileDeletedEvent,
    FileMovedEvent,
)

from configs.paths import get_install_root
from rag_engine.indexer import reindex_single_file, delete_file, get_index_root


# ------------------------------------------------------------
# Event handler
# ------------------------------------------------------------
class RAGEventHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.root = get_index_root()

    def _valid(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.root)
        except ValueError:
            return False  # outside workspace_files

        if path.is_dir():
            return False

        if any(x in path.parts for x in [".git", "__pycache__", "node_modules"]):
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
            delete_file(p)

    def on_moved(self, event: FileMovedEvent):
        old = Path(event.src_path)
        new = Path(event.dest_path)

        if self._valid(old):
            delete_file(old)
        if self._valid(new):
            reindex_single_file(new)


# ------------------------------------------------------------
# Runner
# ------------------------------------------------------------
def start_watcher():
    root = get_index_root()

    if not root.exists():
        print(f"[watcher] workspace_files missing: {root}")
        return

    print(f"[watcher] Monitoring workspace at: {root}")

    handler = RAGEventHandler()
    observer = Observer()
    observer.schedule(handler, str(root), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    start_watcher()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
watcher.py — Watches a project directory and triggers Chroma RAG re-indexing
when files change.

Uses:
    watchdog

Features:
    • Detects file edits, additions, deletions
    • Ignores DB/output/log folders
    • Cooldown to prevent rapid re-index loops
"""

import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from configs.paths import PROJECT_ROOT, VECTOR_INDEX_PATH, INDEXER_SCRIPT, LOG_DIR
from configs.rag_config import WATCHED_EXTENSIONS, REINDEX_COOLDOWN


# ============================================================
# LOG HELPER
# ============================================================

def log(msg: str):
    ts = time.strftime("[%Y-%m-%d %H:%M:%S]")
    print(ts, msg)

    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, "watcher.log"), "a", encoding="utf-8") as f:
        f.write(ts + " " + msg + "\n")


# ============================================================
# EVENT HANDLER
# ============================================================

class ProjectEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_trigger = 0

    def should_trigger(self, path: str) -> bool:
        """Check cooldown + extension filters."""
        _, ext = os.path.splitext(path)
        if ext.lower() not in WATCHED_EXTENSIONS:
            return False

        now = time.time()
        if now - self.last_trigger < REINDEX_COOLDOWN:
            return False

        self.last_trigger = now
        return True

    # -------------------------
    # Watchdog events
    # -------------------------

    def on_modified(self, event):
        if not event.is_directory and self.should_trigger(event.src_path):
            log(f"Modified: {event.src_path}")
            self.run_indexer()

    def on_created(self, event):
        if not event.is_directory and self.should_trigger(event.src_path):
            log(f"Created: {event.src_path}")
            self.run_indexer()

    def on_deleted(self, event):
        if not event.is_directory and self.should_trigger(event.src_path):
            log(f"Deleted: {event.src_path}")
            self.run_indexer()

    # -------------------------

    def run_indexer(self):
        """Call the new Chroma indexer to rebuild the vector database."""
        log("Re-indexing project...")
        try:
            subprocess.run(
                [
                    "python",
                    INDEXER_SCRIPT,
                    "--src", PROJECT_ROOT,
                    "--index", VECTOR_INDEX_PATH
                ],
                check=True
            )
            log("Re-index complete.")
        except Exception as e:
            log(f"Indexer FAILED: {e}")


# ============================================================
# WATCH LOOP
# ============================================================

def start_watcher():
    """Begin watching the project folder."""
    handler = ProjectEventHandler()
    observer = Observer()
    observer.schedule(handler, PROJECT_ROOT, recursive=True)

    log("Watcher started.")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Watcher stopping...")
        observer.stop()

    observer.join()


# ============================================================
# CLI SUPPORT
# ============================================================

if __name__ == "__main__":
    start_watcher()

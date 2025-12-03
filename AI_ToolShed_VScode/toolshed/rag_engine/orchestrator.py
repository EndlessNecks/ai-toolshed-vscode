#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
orchestrator.py — minimal HTTP server for Continue.ai
Provides:
  - /context  → returns top-K relevant chunks
  - /query    → manual semantic search
Runs locally alongside watcher + RAG engine.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from rag_engine.retriever import retrieve_relevant_chunks
from configs.paths import get_workspace_root


HOST = "127.0.0.1"
PORT = 5412


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _json(data, code=200):
    return code, json.dumps(data).encode("utf-8"), "application/json"


# Convert Chunk → Continue context item
def _chunk_to_context_item(chunk):
    fp = chunk.metadata.get("file_path", "")
    return {
        "name": f"{fp}",
        "content": chunk.text
    }


# ------------------------------------------------------------
# Request handler
# ------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)

        try:
            data = json.loads(raw.decode("utf-8"))
        except:
            code, body, ct = _json({"error": "invalid json"}, 400)
            self.send_response(code)
            self.send_header("Content-Type", ct)
            self.end_headers()
            self.wfile.write(body)
            return

        # -------------------------
        # /context  (Continue hook)
        # -------------------------
        if self.path == "/context":
            query = data.get("query", "") or data.get("fullInput", "")
            top_k = int(data.get("top_k", 10))

            chunks = retrieve_relevant_chunks(query, top_k=top_k)
            items = [_chunk_to_context_item(ch) for ch in chunks]

            code, body, ct = _json(items)
            self.send_response(code)
            self.send_header("Content-Type", ct)
            self.end_headers()
            self.wfile.write(body)
            return

        # -------------------------
        # /query (manual testing)
        # -------------------------
        if self.path == "/query":
            query = data.get("query", "")
            top_k = int(data.get("top_k", 5))

            chunks = retrieve_relevant_chunks(query, top_k=top_k)

            simplified = [{
                "file": ch.metadata.get("file_path"),
                "score": ch.metadata.get("score"),
                "text": ch.text
            } for ch in chunks]

            code, body, ct = _json(simplified)
            self.send_response(code)
            self.send_header("Content-Type", ct)
            self.end_headers()
            self.wfile.write(body)
            return

        # Unknown path
        code, body, ct = _json({"error": "unknown endpoint"}, 404)
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.end_headers()
        self.wfile.write(body)

    # Silence logs
    def log_message(self, *a):
        return


# ------------------------------------------------------------
# Runner
# ------------------------------------------------------------
def run():
    server = HTTPServer((HOST, PORT), Handler)
    print(f"[orchestrator] Running at http://{HOST}:{PORT}")
    print(f"[orchestrator] Workspace: {get_workspace_root()}")
    server.serve_forever()


if __name__ == "__main__":
    run()

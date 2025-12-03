AI ToolShed — workspace_files

This directory is the ONLY source of truth for indexing, watching, and retrieval.

All files you want the RAG system to use must be placed inside this folder.

The watcher monitors only this folder.
The indexer scans only this folder.
The orchestrator retrieves context only from this folder.

Supported file types:
- .py
- .txt
- .md
- .json
- .yaml
- .yml
- .xml
- .html
- .css
- .js
- .ts
- .c / .cpp / .h
- Any plain text file

Unsupported (ignored):
- node_modules
- .git
- __pycache__
- binary formats (images, video, archives)

You may freely create subfolders.

Example layout:

    workspace_files/
        utils/
            helpers.py
        docs/
            design.md
        api/
            routes.py

The next time you restart AI ToolShed or call "Rebuild Index",
all files inside this directory will be indexed automatically.

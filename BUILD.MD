# AI ToolShed VSCode — Build & Development Guide

This document explains how to build, package, and test the AI ToolShed VSCode extension locally.
Follow this if you are developing or modifying the extension.

Everything runs locally. No cloud services required.


============================================================
PREREQUISITES
============================================================

You must have the following installed:

• Python 3.x
• Node.js
• npm
• VS Code
• Continue extension
• Ollama
• Codestral model pulled locally

Pull Codestral:
    ollama pull codestral:latest


============================================================
PROJECT STRUCTURE (IMPORTANT)
============================================================

AI_ToolShed_VScode/
    build_venv.ps1            # Creates Python venv
    package_vsix.ps1          # Builds .vsix
    extension/                # VS Code extension logic
    toolshed/                 # Python RAG system
        rag_engine/           # Chunker, embedder, indexer, retriever, watcher, orchestrator
        configs/              # Continue config templates + path helpers
        glue_continue/        # Integration with Continue extension
        cli.py                # Unified CLI
        bootstrap.py          # Initializes folder layout
        __init__.py
    workspace_files/          # Only files in this folder are indexed by RAG
    README.md
    BUILD.md (this file)


============================================================
STEP 1 — CLONE REPOSITORY
============================================================

git clone https://github.com/EndlessNecks/ai-toolshed-vscode.git
cd AI_ToolShed_VScode


============================================================
STEP 2 — BUILD THE PYTHON VENV
============================================================

Run:

    powershell -ExecutionPolicy Bypass -File .\build_venv.ps1

This creates:

    toolshed/.venv/


============================================================
STEP 3 — PACKAGE THE VSIX
============================================================

Run:

    powershell -ExecutionPolicy Bypass -File .\package_vsix.ps1

This script will:

• Check for Node.js
• Check for npm
• Auto-install VSCE if missing
• Install all Python dependencies into toolshed/.venv
• Package the VSIX file using VSCE

You should see:

    === VSIX packaged successfully ===

The output file will look like:

    ai-toolshed-vscode-x.x.x.vsix


============================================================
STEP 4 — INSTALL THE EXTENSION INTO VS CODE
============================================================

1. Open VS Code
2. Press: Ctrl + Shift + P
3. Run: Extensions: Install from VSIX...
4. Select your generated .vsix file
5. Reload VS Code when prompted


============================================================
STEP 5 — TEST THE EXTENSION
============================================================

1. Open the Continue sidebar in VS Code (Ctrl + Shift + I)
2. Set the active model to: codestral-local
3. Place any files you want indexed into:

       AI_ToolShed_VScode/workspace_files/

4. Ask Codestral questions inside Continue
5. ToolShed orchestrator sends workspace context automatically
6. Codestral answers with RAG-enhanced project awareness
7. Continue applies generated patches directly to files
8. Watcher detects changes and reindexes automatically


============================================================
REBUILDING AFTER SOURCE CHANGES
============================================================

If you modify any Python source files or RAG engine logic:

    powershell -ExecutionPolicy Bypass -File .\package_vsix.ps1

If you modify Python dependencies:

    powershell -ExecutionPolicy Bypass -File .\build_venv.ps1
    powershell -ExecutionPolicy Bypass -File .\package_vsix.ps1

After each build, reinstall the .vsix in VS Code:

    Ctrl + Shift + P
    "Install from VSIX..."


============================================================
COMMAND SUMMARY
============================================================

Build Venv:
    powershell -ExecutionPolicy Bypass -File .\build_venv.ps1

Package VSIX:
    powershell -ExecutionPolicy Bypass -File .\package_vsix.ps1

Install VSIX:
    Ctrl + Shift + P → Install from VSIX...


============================================================
NOTES
============================================================

• Only workspace_files/ is indexed by RAG
• Everything (indexing, search, embedding) is fully local
• ToolShed behaves like Copilot but without cloud processing
• No API keys or network needed


============================================================
LICENSE
============================================================

See LICENSE for licensing details.

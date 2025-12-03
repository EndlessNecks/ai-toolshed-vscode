AI ToolShed VSCode - Developer Guide

This document explains how to set up a development environment, build the Python virtual environment, generate the VSIX extension package, and load the extension into VS Code for testing.

This guide assumes you cloned the repository from GitHub.

Prerequisites

Before building or packaging the extension, developers must have:

• Python 3.x installed
• Node.js installed
• npm installed (usually comes with Node)
• Powershell available (Windows)
• Continue extension installed in VS Code
• Ollama installed if testing Codestral locally

If Node.js or npm is missing, the packaging script will notify you.

Download Node.js:
https://nodejs.org/

Repository Layout

AI_ToolShed_VScode/
build_venv.ps1
package_vsix.ps1
extension/
media/
scripts/
toolshed/
workspace_files/
LICENSE
package.json
README.md
FOR_DEVELOPERS_README.txt (this file)

The important developer scripts are:

• build_venv.ps1
• package_vsix.ps1

These handle environment setup and packaging.

Step 1 — Build the virtual environment

Open PowerShell in the root of the project:

cd path\to\AI_ToolShed_VScode
powershell -ExecutionPolicy Bypass -File .\build_venv.ps1

This will:

• Remove any old venv
• Create toolshed/.venv
• Set up a clean Python environment

Note: This script does NOT install dependencies. That happens during packaging.

Step 2 — Package the VSIX extension

After build_venv.ps1 completes, run:

powershell -ExecutionPolicy Bypass -File .\package_vsix.ps1

This script will:

• Verify Node.js exists
• Verify npm exists
• Install VSCE globally if missing
• Install all Python dependencies into the venv
• Generate a .vsix file inside the extension/ folder

If successful, you will see:

=== VSIX packaged successfully ===

The generated VSIX file will be named something similar to:

ai-toolshed-vscode-x.x.x.vsix

Step 3 — Install the extension into VS Code

Open VS Code.

Press:
Ctrl + Shift + P

Type:
"Extensions: Install from VSIX..."

Select the .vsix file generated previously.

VS Code will install the extension immediately.

Step 4 — Test locally

Once the extension is installed:

Open ANY folder in VS Code

Continue extension will load

Open the Continue sidebar (Ctrl + Shift + I)

Select the local Codestral model (codestral-local)

The AI ToolShed extension starts:
• Orchestrator server
• File watcher
• Continue config override

Place files you want the RAG engine to index in:

AI_ToolShed_VScode/workspace_files/

Ask Codestral questions inside Continue

Codestral receives project context

Codestral provides suggestions or generates patches

Continue applies patches back into your project

Rebuilding after changes

If you make changes to Python source files or extension logic:

Run build_venv again only if dependencies change:

powershell -ExecutionPolicy Bypass -File .\build_venv.ps1

Run packaging again for every new test build:

powershell -ExecutionPolicy Bypass -File .\package_vsix.ps1

Reinstall the updated VSIX by repeating:

Ctrl + Shift + P
"Extensions: Install from VSIX..."

Summary of required commands

cd AI_ToolShed_VScode

Initial setup:
powershell -ExecutionPolicy Bypass -File .\build_venv.ps1

Package extension:
powershell -ExecutionPolicy Bypass -File .\package_vsix.ps1

Install VSIX in VS Code:
Ctrl+Shift+P → "Install from VSIX…"

Notes

• workspace_files is the ONLY folder indexed by the RAG engine
• Developers can edit any files in the repo and rebuild locally
• No external API keys are required
• Everything runs locally: Qdrant, watcher, orchestrator, Continue, Codestral

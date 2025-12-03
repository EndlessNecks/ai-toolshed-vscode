AI ToolShed VSCode

AI ToolShed adds a two-way automatic project-wide context injection layer for Codestral through the Continue extension. It provides a fully local RAG (Retrieval-Augmented Generation) system that indexes your project files and feeds relevant context to Codestral. It also supports automatic file patching through Continue, similar to GitHub Copilot but entirely local.

Status: Work in Progress (WIP)

FEATURES

• Local RAG system powered by Qdrant and sentence-transformers
• Automatic context injection into Codestral inside Continue
• Watches a dedicated workspace_files directory for updates
• Automatic chunking and re-indexing on file change
• Orchestrator process exposed to Continue as an HTTP context provider
• Rebuild Index and Restart commands integrated into VS Code
• Offline operation, no cloud services required

FOLDER STRUCTURE

AI_ToolShed_VScode/
extension/
media/
scripts/
toolshed/
configs/
glue_continue/
logs/
rag_engine/
init.py
bootstrap.py
cli.py
workspace_files/
LICENSE
package.json
README.md

workspace_files holds all project files to index. Only files placed inside workspace_files are used for context.

REQUIREMENTS

• VS Code
• Continue extension
• Ollama installed
• Codestral model pulled into Ollama
• Python 3.x installed

INSTALLATION

Install Continue in VS Code.

Pull Codestral in Ollama:
ollama pull codestral:latest

Install AI ToolShed VSCode extension (VSIX or Marketplace).

Run setup:
Open PowerShell (as Administrator):
cd "C:\Program Files\AI_ToolShed_VScode\scripts"
powershell -ExecutionPolicy Bypass -File setup.ps1

setup.ps1 will:
• Create a virtual environment
• Install dependencies
• Generate venv_info.json
• Run bootstrap.py
• Prepare Continue config automatically

USAGE

Place any project files you want indexed into:

C:\Program Files\AI_ToolShed_VScode\workspace_files

The file watcher will detect changes and automatically:
• Chunk files
• Embed them
• Upsert them into Qdrant
• Make them available to Codestral

WORKFLOW

User selects the “codestral-local” model inside Continue.

User asks any question in Continue.

Continue sends the user query to Codestral AND sends a context request to:
http://127.0.0.1:5412/context

The orchestrator retrieves the top semantic matches from workspace_files.

Continue merges them into the system and user prompt.

Codestral produces an answer with project-wide awareness.

If the user asks Codestral to modify code, Continue applies the patch.

The watcher re-indexes the updated file.

VS CODE COMMANDS

Ctrl + Shift + P → type:

• AI ToolShed: Restart RAG Server
• AI ToolShed: Rebuild Index

DEVELOPMENT STATUS

• RAG engine: complete
• Watcher: complete
• Orchestrator: complete
• Continue integration: complete
• Auto-config override: complete
• Extension commands: complete
• Packaging and polish: in progress

DISCLAIMER

This project is in active development and not yet intended for production use.

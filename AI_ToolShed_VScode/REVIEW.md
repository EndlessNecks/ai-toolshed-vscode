# AI ToolShed RAG + Continue Integration Review

## Overview
This repository sets out to provide a local RAG layer that feeds Codestral through Continue. Current assets include a VS Code extension that spawns Python watcher/orchestrator processes, PowerShell setup scripts, and a Python RAG engine under `toolshed/`. The project is still mid-flight; several foundational gaps will prevent the current build from running successfully or delivering context to Continue.

## Critical gaps
1. **Missing Qdrant bootstrap utilities** — The RAG engine imports `rag_engine.qdrant_init` for `get_client`, `ensure_collection`, and `COLLECTION_NAME`, but no such module exists in the tree. Any attempt to index or retrieve vectors will currently raise `ModuleNotFoundError`, blocking the end-to-end pipeline.
2. **Unimplemented Continue orchestrator bridge** — `toolshed/glue_continue/vscode_hooks.py` calls `load_retriever()` and relies on `CodestralClient`/`CodestralOrchestrator` from an `orchestration` package that is not present. Continue cannot initialize a model-backed orchestrator in this state.
3. **Configuration overwrite risk** — The VS Code extension unconditionally copies `toolshed/configs/continue_config_template.yaml` into `~/.continue/config.yaml` on activation. Existing Continue configurations (models, key bindings, and other providers) will be silently replaced rather than merged.
4. **Workspace targeting mismatch** — The extension passes the open workspace path as `TOOLS_HED_WORKSPACE` when starting the Python services, but the RAG engine hardcodes its index root to the installer’s `workspace_files` directory. Users must manually mirror project files into that folder to be indexed; the running workspace is ignored.
5. **Detached processes with no diagnostics** — The orchestrator and watcher are spawned as fully detached, stdio-suppressed child processes. Failures (e.g., import errors from missing modules) will be silent, making debugging difficult for users.

## Recommended next steps
- **Add Qdrant bootstrapper**: Implement `rag_engine/qdrant_init.py` to create/open a local Qdrant store under `configs.paths.get_qdrant_path()`, define `COLLECTION_NAME`, and enforce a vector size that matches the chosen sentence-transformer model.
- **Finish the Continue glue layer**: Provide the missing `orchestration` package or adjust `glue_continue` to call the existing HTTP orchestrator. At minimum, supply a `load_retriever()` helper and a Codestral client shim that matches Continue’s context provider expectations.
- **Respect existing Continue config**: Update the extension to merge the template into `~/.continue/config.yaml` (or gate the copy behind a prompt/setting) instead of overwriting user configs.
- **Align indexing root with the active workspace**: Propagate the `TOOLS_HED_WORKSPACE` environment variable into the Python layer and use it as the index root when present so that users’ open projects are indexed without duplication.
- **Surface process output**: Start the watcher/orchestrator with visible logging (e.g., output channel or log files) and add startup health checks so VS Code can notify users when the RAG backend fails to launch.

These fixes will make the local RAG viable for Continue’s context puller workflow and reduce friction during installation and debugging.

const cp = require("child_process");
const path = require("path");
const fs = require("fs");
const vscode = require("vscode");

let orchestratorProc = null;
let watcherProc = null;

function startServers(python, ragRoot, workspaceRoot) {
    const env = { ...process.env, TOOLS_HED_WORKSPACE: workspaceRoot };

    const orch = path.join(ragRoot, "orchestrator.py");
    orchestratorProc = cp.spawn(python, [orch], {
        cwd: ragRoot,
        env,
        stdio: "ignore",
        detached: true
    });

    const watch = path.join(ragRoot, "watcher.py");
    watcherProc = cp.spawn(python, [watch], {
        cwd: ragRoot,
        env,
        stdio: "ignore",
        detached: true
    });
}

function stopServers() {
    try { if (orchestratorProc) orchestratorProc.kill(); } catch (_) {}
    try { if (watcherProc) watcherProc.kill(); } catch (_) {}
}

function restart(context, venvInfo) {
    stopServers();

    const python = venvInfo.venv_python;
    const ragRoot = venvInfo.rag_engine_root;

    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceRoot) {
        vscode.window.showErrorMessage("AI ToolShed: No workspace open.");
        return;
    }

    startServers(python, ragRoot, workspaceRoot);
    vscode.window.showInformationMessage("AI ToolShed RAG restarted.");
}

module.exports = {
    restart,
    startServers,
    stopServers
};

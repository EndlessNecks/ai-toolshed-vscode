const cp = require("child_process");
const path = require("path");
const fs = require("fs");
const vscode = require("vscode");

let orchestratorProc = null;
let watcherProc = null;
const output = vscode.window.createOutputChannel("AI ToolShed");

function attachLogging(proc, label) {
    if (!proc) return;

    proc.stdout?.on("data", (data) => {
        output.appendLine(`[${label}] ${data.toString().trimEnd()}`);
    });

    proc.stderr?.on("data", (data) => {
        output.appendLine(`[${label}][err] ${data.toString().trimEnd()}`);
    });

    proc.on("exit", (code, signal) => {
        output.appendLine(`[${label}] exited (code=${code} signal=${signal})`);
    });
}


// ------------------------------------------------------------
// Start servers (orchestrator + watcher)
// ------------------------------------------------------------
function startServers(python, ragRoot, workspaceRoot) {
    const env = { ...process.env, TOOLS_HED_WORKSPACE: workspaceRoot };

    const orch = path.join(ragRoot, "orchestrator.py");
    orchestratorProc = cp.spawn(python, [orch], {
        cwd: ragRoot,
        env,
        stdio: ["ignore", "pipe", "pipe"],
        detached: false
    });
    attachLogging(orchestratorProc, "orchestrator");

    const watch = path.join(ragRoot, "watcher.py");
    watcherProc = cp.spawn(python, [watch], {
        cwd: ragRoot,
        env,
        stdio: ["ignore", "pipe", "pipe"],
        detached: false
    });
    attachLogging(watcherProc, "watcher");

    output.show(true);
}


// ------------------------------------------------------------
// Stop servers cleanly
// ------------------------------------------------------------
function stopServers() {
    try { if (orchestratorProc) orchestratorProc.kill(); } catch (_) {}
    try { if (watcherProc) watcherProc.kill(); } catch (_) {}
}


// ------------------------------------------------------------
// Restart both servers
// ------------------------------------------------------------
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
    vscode.window.showInformationMessage("AI ToolShed: RAG restarted.");
}


// ------------------------------------------------------------
// Rebuild the index
// ------------------------------------------------------------
function rebuildIndex(venvInfo) {
    const installRoot = path.resolve(__dirname, "..");
    const script = path.join(installRoot, "scripts", "rebuild_index.ps1");

    cp.spawn("powershell.exe", [
        "-ExecutionPolicy", "Bypass",
        "-File", script
    ], {
        cwd: installRoot,
        detached: true,
        stdio: "ignore"
    });

    vscode.window.showInformationMessage("AI ToolShed: Rebuilding index…");
}


// ------------------------------------------------------------
module.exports = {
    startServers,
    stopServers,
    restart,
    rebuildIndex
};

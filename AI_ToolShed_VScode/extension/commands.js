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

    proc.on("error", (err) => {
        output.appendLine(`[${label}] failed to start: ${err.message}`);
    });
}


// ------------------------------------------------------------
// Start servers (orchestrator + watcher)
// ------------------------------------------------------------
function startServers(runtime) {
    const { python, ragRoot, workspaceRoot } = runtime;

    if (!python) {
        vscode.window.showErrorMessage("AI ToolShed: No Python interpreter configured.");
        return;
    }

    if (!ragRoot) {
        vscode.window.showErrorMessage("AI ToolShed: RAG engine path not configured.");
        return;
    }

    if (!workspaceRoot) {
        vscode.window.showErrorMessage("AI ToolShed: No workspace open.");
        return;
    }

    const env = { ...process.env, TOOLS_HED_WORKSPACE: workspaceRoot };

    const orch = path.join(ragRoot, "orchestrator.py");
    if (fs.existsSync(orch)) {
        orchestratorProc = cp.spawn(python, [orch], {
            cwd: ragRoot,
            env,
            stdio: ["ignore", "pipe", "pipe"],
            detached: false
        });
        attachLogging(orchestratorProc, "orchestrator");
    } else {
        vscode.window.showErrorMessage("AI ToolShed: orchestrator.py not found.");
    }

    const watch = path.join(ragRoot, "watcher.py");
    if (fs.existsSync(watch)) {
        watcherProc = cp.spawn(python, [watch], {
            cwd: ragRoot,
            env,
            stdio: ["ignore", "pipe", "pipe"],
            detached: false
        });
        attachLogging(watcherProc, "watcher");
    } else {
        vscode.window.showErrorMessage("AI ToolShed: watcher.py not found.");
    }

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
function restart(runtime) {
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

    stopServers();
    startServers({ ...runtime, workspaceRoot });
    vscode.window.showInformationMessage("AI ToolShed: RAG restarted.");
}


// ------------------------------------------------------------
// Rebuild the index
// ------------------------------------------------------------
function rebuildIndex(runtime) {
    const { python, ragRoot, workspaceRoot } = runtime;

    if (!python) {
        vscode.window.showErrorMessage("AI ToolShed: No Python interpreter configured.");
        return;
    }

    if (!ragRoot) {
        vscode.window.showErrorMessage("AI ToolShed: RAG engine path not configured.");
        return;
    }

    const script = path.join(ragRoot, "indexer.py");
    const env = { ...process.env, TOOLS_HED_WORKSPACE: workspaceRoot };

    cp.spawn(python, [script], {
        cwd: ragRoot,
        env,
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
    rebuildIndex,
    getOutputChannel: () => output
};

const cp = require("child_process");
const path = require("path");
const fs = require("fs");
const fse = require("fs-extra");
const vscode = require("vscode");

let orchestratorProc = null;
let watcherProc = null;
const output = vscode.window.createOutputChannel("AI ToolShed");
const EXCLUDE_FOLDERS = new Set([".git", "node_modules", "__pycache__", ".venv", "venv"]);

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
    const workspaceRoot = runtime.workspaceRoot ?? vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

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
// Import current VS Code workspace into <install_root>/workspace_files
// ------------------------------------------------------------
async function importWorkspace(runtime) {
    const { workspaceRoot, installRoot } = runtime;

    if (!workspaceRoot) {
        vscode.window.showErrorMessage("AI ToolShed: No workspace open to import.");
        return;
    }

    if (!installRoot) {
        vscode.window.showErrorMessage("AI ToolShed: Install root not configured.");
        return;
    }

    const destRoot = path.join(installRoot, "workspace_files");
    const srcRoot = workspaceRoot;

    const filter = (src) => {
        const rel = path.relative(srcRoot, src);
        if (rel.startsWith("..")) return false;

        const parts = rel.split(path.sep);
        if (parts.some((p) => EXCLUDE_FOLDERS.has(p))) return false;

        return true;
    };

    try {
        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: "AI ToolShed: Importing workspace…",
            },
            async () => {
                await fse.ensureDir(destRoot);
                await fse.emptyDir(destRoot);
                await fse.copy(srcRoot, destRoot, { filter });
            }
        );

        output.appendLine(`[import] Copied workspace from ${srcRoot} to ${destRoot}`);
        vscode.window.showInformationMessage(
            "AI ToolShed: Workspace imported. Run 'AI ToolShed: Rebuild RAG Index' to refresh the index."
        );
    } catch (err) {
        output.appendLine(`[import][err] ${err.message}`);
        vscode.window.showErrorMessage("AI ToolShed: Failed to import workspace. See output for details.");
    }
}


// ------------------------------------------------------------
// Remove imported projects/files from <install_root>/workspace_files
// ------------------------------------------------------------
async function purgeIndexEntries(targets, runtime) {
    const { python, ragRoot, workspaceRoot } = runtime;

    if (!python || !ragRoot || targets.length === 0) {
        return;
    }

    const script = path.join(ragRoot, "indexer.py");
    const env = { ...process.env, TOOLS_HED_WORKSPACE: workspaceRoot };

    return new Promise((resolve, reject) => {
        const proc = cp.spawn(python, [script, "--delete", ...targets], {
            cwd: ragRoot,
            env,
            stdio: ["ignore", "pipe", "pipe"],
            detached: false
        });

        proc.stdout?.on("data", (data) => {
            output.appendLine(`[prune] ${data.toString().trimEnd()}`);
        });

        proc.stderr?.on("data", (data) => {
            output.appendLine(`[prune][err] ${data.toString().trimEnd()}`);
        });

        proc.on("exit", (code) => {
            if (code === 0) {
                resolve();
            } else {
                reject(new Error(`Index cleanup exited with code ${code}`));
            }
        });

        proc.on("error", (err) => {
            reject(err);
        });
    });
}

async function removeImportedProjects(runtime) {
    const { installRoot, python, ragRoot } = runtime;
    const workspaceRoot = path.join(installRoot, "workspace_files");

    if (!installRoot || !fs.existsSync(workspaceRoot)) {
        vscode.window.showErrorMessage("AI ToolShed: No imported workspace to clean.");
        return;
    }

    const entries = await fs.promises.readdir(workspaceRoot, { withFileTypes: true });
    const candidates = entries
        .filter((e) => e.isDirectory() || e.isFile())
        .map((e) => ({
            label: e.name,
            description: e.isDirectory() ? "Folder" : "File",
            targetPath: path.join(workspaceRoot, e.name)
        }));

    if (candidates.length === 0) {
        vscode.window.showInformationMessage("AI ToolShed: No imported projects to remove.");
        return;
    }

    const selection = await vscode.window.showQuickPick(candidates, {
        canPickMany: true,
        placeHolder: "Select imported projects/files to remove from AI ToolShed workspace"
    });

    if (!selection || selection.length === 0) {
        return;
    }

    const purgeChoice = await vscode.window.showQuickPick(
        [
            { label: "Remove files only", purge: false },
            { label: "Remove files and indexed data", purge: true }
        ],
        { placeHolder: "Also delete indexed vectors for the selected entries?" }
    );

    if (!purgeChoice) {
        return;
    }

    const targets = selection.map((s) => s.targetPath);

    if (purgeChoice.purge && (!python || !ragRoot)) {
        vscode.window.showWarningMessage(
            "AI ToolShed: Python/RAG paths missing; removing files only."
        );
    }

    try {
        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: "AI ToolShed: Removing imported projects…",
            },
            async () => {
                for (const target of targets) {
                    await fse.remove(target);
                    output.appendLine(`[prune] Removed ${target}`);
                }

                if (purgeChoice.purge) {
                    await purgeIndexEntries(targets, { python, ragRoot, workspaceRoot });
                }
            }
        );

        vscode.window.showInformationMessage("AI ToolShed: Selected imports removed.");
    } catch (err) {
        output.appendLine(`[prune][err] ${err.message}`);
        vscode.window.showErrorMessage("AI ToolShed: Failed to remove selected imports. See output for details.");
    }
}


// ------------------------------------------------------------
module.exports = {
    startServers,
    stopServers,
    restart,
    rebuildIndex,
    importWorkspace,
    removeImportedProjects,
    getOutputChannel: () => output
};

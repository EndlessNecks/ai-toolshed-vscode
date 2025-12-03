// extension.js — minimal VS Code glue for AI ToolShed
// Starts orchestrator + watcher using the installed venv

const vscode = require("vscode");
const cp = require("child_process");
const fs = require("fs");
const path = require("path");

let orchestratorProc = null;
let watcherProc = null;

function activate(context) {
    const installRoot = path.resolve(__dirname, ".."); // AI_ToolShed_VScode
    const configDir = path.join(installRoot, "configs");
    const venvInfoPath = path.join(configDir, "venv_info.json");

    if (!fs.existsSync(venvInfoPath)) {
        vscode.window.showErrorMessage("AI ToolShed: Missing venv_info.json. Run setup.ps1.");
        return;
    }

    const info = JSON.parse(fs.readFileSync(venvInfoPath, "utf8"));

    const python = info.venv_python;
    const ragRoot = info.rag_engine_root;
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

    if (!workspaceRoot) {
        vscode.window.showErrorMessage("AI ToolShed: No workspace open.");
        return;
    }

    // Set workspace override for paths.py
    const env = {
        ...process.env,
        TOOLS_HED_WORKSPACE: workspaceRoot
    };

    // Launch orchestrator
    const orchPath = path.join(ragRoot, "orchestrator.py");
    orchestratorProc = cp.spawn(python, [orchPath], {
        cwd: ragRoot,
        env,
        stdio: "ignore",
        detached: true
    });

    // Launch watcher
    const watcherPath = path.join(ragRoot, "watcher.py");
    watcherProc = cp.spawn(python, [watcherPath], {
        cwd: ragRoot,
        env,
        stdio: "ignore",
        detached: true
    });

    vscode.window.showInformationMessage("AI ToolShed RAG server started.");
}

function deactivate() {
    try {
        if (orchestratorProc) orchestratorProc.kill();
    } catch (_) {}

    try {
        if (watcherProc) watcherProc.kill();
    } catch (_) {}
}

module.exports = {
    activate,
    deactivate
};

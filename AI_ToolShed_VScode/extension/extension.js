// extension.js — clean VS Code activation script for AI ToolShed

const vscode = require("vscode");
const fs = require("fs");
const path = require("path");
const { startServers, stopServers, restart } = require("./commands.js");

let venvInfo = null;

function activate(context) {
    const installRoot = path.resolve(__dirname, "..");
    const configDir = path.join(installRoot, "configs");
    const venvInfoPath = path.join(configDir, "venv_info.json");

    if (!fs.existsSync(venvInfoPath)) {
        vscode.window.showErrorMessage("AI ToolShed: Missing venv_info.json. Run setup.ps1.");
        return;
    }

    venvInfo = JSON.parse(fs.readFileSync(venvInfoPath, "utf8"));

    const python = venvInfo.venv_python;
    const ragRoot = venvInfo.rag_engine_root;
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

    if (!workspaceRoot) {
        vscode.window.showErrorMessage("AI ToolShed: No workspace open.");
        return;
    }

    startServers(python, ragRoot, workspaceRoot);

    const restartCmd = vscode.commands.registerCommand("ai-toolshed.restart", () => {
        restart(context, venvInfo);
    });

    context.subscriptions.push(restartCmd);
}

function deactivate() {
    stopServers();
}

module.exports = {
    activate,
    deactivate
};

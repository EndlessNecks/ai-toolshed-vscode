const vscode = require("vscode");
const fs = require("fs");
const path = require("path");
const {
    startServers,
    stopServers,
    restart,
    rebuildIndex
} = require("./commands.js");

let venvInfo = null;

function ensureContinueConfig(templatePath) {
    const home = process.env.USERPROFILE || process.env.HOME;
    if (!home) return;

    const continueDir = path.join(home, ".continue");
    const continueConfig = path.join(continueDir, "config.yaml");

    if (!fs.existsSync(continueDir)) {
        fs.mkdirSync(continueDir, { recursive: true });
    }

    // Respect existing user configuration; only seed when missing
    if (fs.existsSync(continueConfig)) {
        return;
    }

    try {
        fs.copyFileSync(templatePath, continueConfig);
    } catch (err) {
        vscode.window.showErrorMessage("AI ToolShed: Failed to apply Continue config.");
    }
}

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

    // --- APPLY CONTINUE CONFIG TEMPLATE ---
    const templatePath = path.join(installRoot, "toolshed", "configs", "continue_config_template.yaml");
    if (fs.existsSync(templatePath)) {
        ensureContinueConfig(templatePath);
    }

    // Start background servers
    startServers(python, ragRoot, workspaceRoot);

    // Restart command
    const restartCmd = vscode.commands.registerCommand("ai-toolshed.restart", () => {
        restart(context, venvInfo);
    });

    // Rebuild index command
    const rebuildCmd = vscode.commands.registerCommand("ai-toolshed.rebuildIndex", () => {
        rebuildIndex(venvInfo);
    });

    context.subscriptions.push(restartCmd);
    context.subscriptions.push(rebuildCmd);
}

function deactivate() {
    stopServers();
}

module.exports = {
    activate,
    deactivate
};

const vscode = require("vscode");
const fs = require("fs");
const path = require("path");
const {
    startServers,
    stopServers,
    restart,
    rebuildIndex,
    importWorkspace,
    getOutputChannel
} = require("./commands.js");
const yaml = require("yaml");

let venvInfo = null;

function resolvePython(fallback) {
    if (process.env.TOOLS_HED_PYTHON) {
        return process.env.TOOLS_HED_PYTHON;
    }

    return fallback || (process.platform === "win32" ? "python.exe" : "python3");
}

function ensureContinueConfig(templatePath, workspaceRoot) {
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
        const template = fs.readFileSync(templatePath, "utf8");
        const parsed = yaml.parse(template);

        if (workspaceRoot) {
            parsed.workspace_directory = workspaceRoot;
        }

        const serialized = yaml.stringify(parsed);
        fs.writeFileSync(continueConfig, serialized, "utf8");
    } catch (err) {
        vscode.window.showErrorMessage("AI ToolShed: Failed to apply Continue config.");
        getOutputChannel().appendLine(`[extension] Failed to seed Continue config: ${err.message}`);
    }
}

function activate(context) {
    const installRoot = path.resolve(__dirname, "..");
    const configDir = path.join(installRoot, "configs");
    const venvInfoPath = path.join(configDir, "venv_info.json");
    const output = getOutputChannel();

    if (fs.existsSync(venvInfoPath)) {
        venvInfo = JSON.parse(fs.readFileSync(venvInfoPath, "utf8"));
    } else {
        const toolshedRoot = path.join(installRoot, "toolshed");
        venvInfo = {
            install_root: installRoot,
            toolshed_root: toolshedRoot,
            rag_engine_root: path.join(toolshedRoot, "rag_engine"),
            venv_python: null
        };

        output.appendLine("[extension] venv_info.json missing; using workspace defaults.");
    }

    const python = resolvePython(venvInfo.venv_python);
    const ragRoot = venvInfo.rag_engine_root;
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    const workspaceFilesRoot = path.join(installRoot, "workspace_files");

    output.appendLine(`[extension] Python: ${python}`);
    output.appendLine(`[extension] RAG root: ${ragRoot}`);
    output.appendLine(`[extension] Workspace: ${workspaceRoot}`);
    output.appendLine(`[extension] Workspace files: ${workspaceFilesRoot}`);

    if (!workspaceRoot) {
        vscode.window.showErrorMessage("AI ToolShed: No workspace open.");
        return;
    }

    // --- APPLY CONTINUE CONFIG TEMPLATE ---
    const templatePath = path.join(installRoot, "toolshed", "configs", "continue_config_template.yaml");
    if (fs.existsSync(templatePath)) {
        ensureContinueConfig(templatePath, workspaceRoot);
    }

    // Start background servers
    startServers({ python, ragRoot, workspaceRoot: workspaceFilesRoot });

    // Restart command
    const restartCmd = vscode.commands.registerCommand("ai-toolshed.restart", () => {
        restart({ python, ragRoot, workspaceRoot: workspaceFilesRoot });
    });

    // Rebuild index command
    const rebuildCmd = vscode.commands.registerCommand("ai-toolshed.rebuildIndex", () => {
        rebuildIndex({ python, ragRoot, workspaceRoot: workspaceFilesRoot });
    });

    // Import workspace command
    const importCmd = vscode.commands.registerCommand("ai-toolshed.importWorkspace", () => {
        const currentWorkspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        importWorkspace({ installRoot, workspaceRoot: currentWorkspace });
    });

    context.subscriptions.push(restartCmd);
    context.subscriptions.push(rebuildCmd);
    context.subscriptions.push(importCmd);
}

function deactivate() {
    stopServers();
}

module.exports = {
    activate,
    deactivate
};

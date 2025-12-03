// extension.js
// AI ToolShed – VS Code Extension

const vscode = require('vscode');
const path = require('path');
const fs = require('fs-extra');
const { exec } = require('child_process');

function activate(context) {

    // ----------------------------
    // Resolve roots
    // ----------------------------
    const extensionRoot = context.extensionPath;
    const toolShedRoot = path.join(extensionRoot, "toolshed");
    const scriptRoot = path.join(extensionRoot, "scripts");

    console.log("[AI ToolShed] Extension Root:", extensionRoot);
    console.log("[AI ToolShed] Toolshed Root:", toolShedRoot);
    console.log("[AI ToolShed] Script Root:", scriptRoot);

    // ----------------------------
    // Execute a PowerShell script
    // ----------------------------
    function runPowerShellScript(scriptPath, callback) {
        const resolved = scriptPath.replace(/\\/g, "\\\\");
        const cmd = `powershell.exe -ExecutionPolicy Bypass -Command "& \\"${resolved}\\""`;        

        console.log("[AI ToolShed] Running PowerShell:", cmd);

        exec(cmd, { cwd: scriptRoot, windowsHide: false }, (err, stdout, stderr) => {
            if (stdout) console.log("[AI ToolShed][stdout]", stdout);
            if (stderr) console.log("[AI ToolShed][stderr]", stderr);

            if (err) {
                vscode.window.showErrorMessage("AI ToolShed setup failed. Check console.");
                console.error("[AI ToolShed] ERROR:", err);
                return callback(err);
            }

            callback(null);
        });
    }

    // ----------------------------
    // Sync Continue config
    // ----------------------------
    async function syncContinueConfig() {
        try {
            const continueHome = path.join(process.env.USERPROFILE, ".continue");
            await fs.ensureDir(continueHome);

            const srcCfg = path.join(toolShedRoot, "config.yaml");
            const dstCfg = path.join(continueHome, "config.yaml");

            console.log("[AI ToolShed] Syncing Continue config →", dstCfg);
            await fs.copy(srcCfg, dstCfg, { overwrite: true });

        } catch (e) {
            console.error("[AI ToolShed] Failed copying Continue config:", e);
        }
    }

    // ============================
    // COMMAND: Install / Reinitialize
    // ============================
    const installCmd = vscode.commands.registerCommand("aiToolshed.install", async () => {
        vscode.window.showInformationMessage("AI ToolShed: Beginning install...");

        await syncContinueConfig();

        const setupScript = path.join(scriptRoot, "setup.ps1");
        if (!fs.existsSync(setupScript)) {
            vscode.window.showErrorMessage("setup.ps1 missing in extension scripts folder.");
            return;
        }

        runPowerShellScript(setupScript, (err) => {
            if (!err) {
                vscode.window.showInformationMessage("AI ToolShed install completed.");
            }
        });
    });

    // ============================
    // COMMAND: Rebuild RAG Index
    // ============================
    const rebuildCmd = vscode.commands.registerCommand("aiToolshed.rebuildIndex", async () => {
        vscode.window.showInformationMessage("AI ToolShed: Rebuilding RAG index...");

        const rebuildScript = path.join(scriptRoot, "rebuild_index.ps1");
        if (!fs.existsSync(rebuildScript)) {
            vscode.window.showErrorMessage("rebuild_index.ps1 missing.");
            return;
        }

        runPowerShellScript(rebuildScript, (err) => {
            if (!err) {
                vscode.window.showInformationMessage("AI ToolShed: RAG index rebuilt.");
            }
        });
    });

    context.subscriptions.push(installCmd);
    context.subscriptions.push(rebuildCmd);

    console.log("[AI ToolShed] Activated successfully.");
}

function deactivate() {
    console.log("[AI ToolShed] Deactivated.");
}

module.exports = { activate, deactivate };

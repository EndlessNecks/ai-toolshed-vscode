# =============================================
# AI ToolShed - package_vsix.ps1
# Builds the extension’s VSIX package.
# Also installs Python deps into toolshed/.venv.
# Automatically checks/installs: Node.js, npm, vsce.
# =============================================

$ErrorActionPreference = "Stop"

Write-Host "`n=== Packaging AI ToolShed VSIX ===`n"

$Root         = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Toolshed     = Join-Path $Root "toolshed"
$VenvPath     = Join-Path $Toolshed ".venv"
$VenvPython   = Join-Path $VenvPath "Scripts\python.exe"
$RagEngine    = Join-Path $Toolshed "rag_engine"
$ReqsFile     = Join-Path $RagEngine "requirements.txt"
$ExtensionDir = Join-Path $Root "extension"

# ------------------------------------------------------------
# 1. Ensure venv exists
# ------------------------------------------------------------
if (-not (Test-Path $VenvPython)) {
    Write-Error "Venv not found. Run build_venv.ps1 first."
    exit 1
}

# ------------------------------------------------------------
# 2. Ensure Node.js exists
# ------------------------------------------------------------
$node = Get-Command node -ErrorAction SilentlyContinue

if (-not $node) {
    Write-Host "Node.js not found on system."
    Write-Host ""
    Write-Host "Please install Node.js from https://nodejs.org/"
    Write-Host "After installation, re-run this script."
    exit 1
}
else {
    Write-Host "Node.js found: $($node.Source)"
}

# ------------------------------------------------------------
# 3. Ensure npm exists
# ------------------------------------------------------------
$npm = Get-Command npm -ErrorAction SilentlyContinue

if (-not $npm) {
    Write-Host "`nERROR: npm is missing, even though Node is installed."
    Write-Host "This can happen on some systems where Node is installed without npm."
    Write-Host ""
    Write-Host "Please reinstall Node.js using the official installer."
    exit 1
}
else {
    Write-Host "npm found: $($npm.Source)"
}

# ------------------------------------------------------------
# 4. Ensure VSCE exists, otherwise install it
# ------------------------------------------------------------
$vsce = Get-Command vsce -ErrorAction SilentlyContinue

if (-not $vsce) {
    Write-Host "`nVSCE not found. Installing globally..."
    npm install -g @vscode/vsce

    # Re-check
    $vsce = Get-Command vsce -ErrorAction SilentlyContinue
    if (-not $vsce) {
        Write-Error "Failed to install VSCE."
        exit 1
    }

    Write-Host "VSCE installed successfully."
}
else {
    Write-Host "VSCE found: $($vsce.Source)"
}

# ------------------------------------------------------------
# 5. Install Python dependencies
# ------------------------------------------------------------
Write-Host "`nInstalling Python dependencies..."
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r $ReqsFile

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install Python requirements."
    exit $LASTEXITCODE
}

Write-Host "Python dependencies installed."

# ------------------------------------------------------------
# 6. Package VSIX using VSCE
# ------------------------------------------------------------
Write-Host "`nPackaging VSIX..."
Push-Location $ExtensionDir

vsce package

Pop-Location

Write-Host "`n=== VSIX packaged successfully ===`n"

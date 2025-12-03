# ---------------------------------------------
# AI ToolShed Setup Script (for packaged venv)
# ---------------------------------------------

$ErrorActionPreference = "Stop"

Write-Output "=== AI ToolShed Installer Starting ==="

# Script root
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Output "Script Root: $ScriptRoot"

# Toolshed root
$ToolShedRoot = Join-Path $ScriptRoot ".." | Resolve-Path
Write-Output "ToolShed Root: $ToolShedRoot"

# venv path (already bundled)
$VenvPath = Join-Path $ToolShedRoot "toolshed\.venv"
Write-Output "Venv Path: $VenvPath"

if (-not (Test-Path $VenvPath)) {
    Write-Output "ERROR: .venv not found inside extension. The VSIX may be corrupted." 
    exit 1
}

# Activate it
$Activate = Join-Path $VenvPath "Scripts\Activate.ps1"
if (-not (Test-Path $Activate)) {
    Write-Output "ERROR: Activate.ps1 missing!"
    exit 1
}

Write-Output "Activating venv..."
. $Activate

Write-Output "Venv activation complete."
Write-Output "`n=== AI ToolShed installation complete! ==="
exit 0

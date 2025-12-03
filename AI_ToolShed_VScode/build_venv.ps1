# =============================================
# AI ToolShed - build_venv.ps1
# Creates a local venv under toolshed/.venv
# without running the full installer.
# =============================================

$ErrorActionPreference = "Stop"

Write-Host "`n=== Building AI ToolShed venv ===`n"

# Detect root of the project
$ScriptRoot  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$InstallRoot = $ScriptRoot
$Toolshed    = Join-Path $InstallRoot "toolshed"
$VenvPath    = Join-Path $Toolshed ".venv"

if (Test-Path $VenvPath) {
    Write-Host "Deleting existing venv..."
    Remove-Item -Recurse -Force $VenvPath
}

# Locate Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) {
    Write-Error "Python not found."
    exit 1
}

$PythonExe = $python.Source

Write-Host "Using Python: $PythonExe"
Write-Host "Creating venv at: $VenvPath"

& $PythonExe -m venv $VenvPath

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create venv."
    exit $LASTEXITCODE
}

Write-Host "`n=== venv created successfully ===`n"

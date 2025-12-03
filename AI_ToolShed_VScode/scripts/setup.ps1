# ---------------------------------------------
# AI ToolShed Setup Script
# - Creates venv
# - Installs requirements
# - Logs to logs/setup.log
# ---------------------------------------------

$ErrorActionPreference = "Stop"

Write-Output "=== AI ToolShed Python Environment Setup ==="

# ---------------------------------------------
# Resolve paths
# ---------------------------------------------
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ToolShedRoot = Join-Path $ScriptRoot ".." | Resolve-Path | Select-Object -ExpandProperty Path

Write-Output "Script Root : $ScriptRoot"
Write-Output "ToolShed Root: $ToolShedRoot"

$LogsDir   = Join-Path $ToolShedRoot "logs"
$VenvDir   = Join-Path $ToolShedRoot "toolshed\.venv"
$ReqsFile  = Join-Path $ToolShedRoot "rag_engine\requirements.txt"
$VenvPyWin = Join-Path $VenvDir "Scripts\python.exe"
$VenvPyNix = Join-Path $VenvDir "bin\python"

if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}

$LogFile = Join-Path $LogsDir "setup.log"

# Simple logging helper
function Log {
    param([string]$Msg)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$timestamp [SETUP] $Msg"
    $line | Tee-Object -FilePath $LogFile -Append
}

Log "=== Starting AI ToolShed setup ==="
Log "ToolShed root: $ToolShedRoot"
Log "Venv directory: $VenvDir"
Log "Requirements: $ReqsFile"

# ---------------------------------------------
# Locate Python
# ---------------------------------------------
Log "Locating Python interpreter..."

$python = Get-Command python -ErrorAction SilentlyContinue

if (-not $python) {
    Log "'python' not found on PATH, trying 'py' launcher..."
    $python = Get-Command py -ErrorAction SilentlyContinue
    if (-not $python) {
        Log "ERROR: Neither 'python' nor 'py' found on PATH."
        Write-Error "Python is not on PATH. Install Python 3.x and restart VS Code / terminal."
        exit 1
    } else {
        Log "Using 'py' launcher at: $($python.Source)"
    }
} else {
    Log "Using 'python' at: $($python.Source)"
}

$pythonExe = $python.Source

# ---------------------------------------------
# Create venv if missing
# ---------------------------------------------
if (Test-Path $VenvDir) {
    Log "Virtual environment already exists at: $VenvDir"
} else {
    Log "Creating virtual environment at: $VenvDir"
    & $pythonExe -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Log "ERROR: venv creation failed (exit code $LASTEXITCODE)"
        Write-Error "Failed to create virtual environment."
        exit $LASTEXITCODE
    }
}

# Determine venv Python executable (Windows vs *nix)
$VenvPython = $VenvPyWin
if (-not (Test-Path $VenvPython)) {
    $VenvPython = $VenvPyNix
}

if (-not (Test-Path $VenvPython)) {
    Log "ERROR: Could not find python inside venv."
    Write-Error "Could not find python inside virtual environment."
    exit 1
}

Log "Venv Python: $VenvPython"

# ---------------------------------------------
# Upgrade pip + install requirements
# ---------------------------------------------
if (-not (Test-Path $ReqsFile)) {
    Log "ERROR: Requirements file not found at $ReqsFile"
    Write-Error "rag_engine/requirements.txt not found. Make sure it exists before running setup."
    exit 1
}

Log "Upgrading pip to >=23.0..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: pip upgrade failed (exit code $LASTEXITCODE)"
    Write-Error "pip upgrade failed."
    exit $LASTEXITCODE
}

Log "Installing Python requirements from $ReqsFile..."
& $VenvPython -m pip install -r $ReqsFile
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: requirements install failed (exit code $LASTEXITCODE)"
    Write-Error "Requirements installation failed."
    exit $LASTEXITCODE
}

# ---------------------------------------------
# Emit venv info for extension.js
# ---------------------------------------------
$ConfigDir = Join-Path $ToolShedRoot "configs"
if (-not (Test-Path $ConfigDir)) {
    New-Item -ItemType Directory -Path $ConfigDir | Out-Null
}

$VenvInfoPath = Join-Path $ConfigDir "venv_info.json"

$venvInfo = @{
    toolshed_root = $ToolShedRoot
    venv_dir      = $VenvDir
    venv_python   = $VenvPython
} | ConvertTo-Json -Depth 3

$venvInfo | Out-File -FilePath $VenvInfoPath -Encoding UTF8

Log "Wrote venv info to $VenvInfoPath"
Log "=== AI ToolShed setup completed successfully ==="

Write-Output ""
Write-Output "=== AI ToolShed setup completed successfully ==="
Write-Output "Venv Python: $VenvPython"
Write-Output "Log file:    $LogFile"
Write-Output ""
Write-Output "You can now use this venv for the RAG, watcher, and orchestrator."

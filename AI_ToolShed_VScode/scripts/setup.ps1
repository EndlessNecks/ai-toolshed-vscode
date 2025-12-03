# =============================================
# AI ToolShed Setup Script (FINAL)
# Creates venv, installs deps, writes venv_info.json,
# and runs bootstrap.py to initialize folders.
# =============================================

$ErrorActionPreference = "Stop"

Write-Output "`n=== AI ToolShed Python Environment Setup ===`n"

# ---------------------------------------------
# DETECT INSTALL ROOT
# ---------------------------------------------
$ScriptRoot  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$InstallRoot = Split-Path -Parent $ScriptRoot

# ---------------------------------------------
# PATHS
# ---------------------------------------------
$ToolshedRoot  = Join-Path $InstallRoot "toolshed"
$RagEngineRoot = Join-Path $ToolshedRoot "rag_engine"
$ReqsFile      = Join-Path $RagEngineRoot "requirements.txt"
$VenvDir       = Join-Path $ToolshedRoot ".venv"
$LogsDir       = Join-Path $InstallRoot "logs"
$ConfigDir     = Join-Path $InstallRoot "configs"

# Ensure logs/config dirs
if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Path $LogsDir | Out-Null }
if (-not (Test-Path $ConfigDir)) { New-Item -ItemType Directory -Path $ConfigDir | Out-Null }

$LogFile = Join-Path $LogsDir "setup.log"

function Log {
    param([string]$Msg)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts [SETUP] $Msg" | Tee-Object -FilePath $LogFile -Append
}

Log "Install root     : $InstallRoot"
Log "Toolshed root    : $ToolshedRoot"
Log "RAG engine root  : $RagEngineRoot"
Log "Requirements     : $ReqsFile"
Log "Venv directory   : $VenvDir"

# ---------------------------------------------
# VALIDATE REQUIREMENTS
# ---------------------------------------------
if (-not (Test-Path $ReqsFile)) {
    Log "ERROR: Missing requirements.txt"
    Write-Error "rag_engine/requirements.txt not found."
    exit 1
}

# ---------------------------------------------
# LOCATE PYTHON
# ---------------------------------------------
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }

if (-not $python) {
    Log "ERROR: Python not found."
    Write-Error "No Python interpreter on PATH."
    exit 1
}

$PythonExe = $python.Source
Log "Using Python: $PythonExe"

# ---------------------------------------------
# CREATE VENV
# ---------------------------------------------
if (-not (Test-Path $VenvDir)) {
    Log "Creating venv..."
    & $PythonExe -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Log "ERROR creating venv"
        exit $LASTEXITCODE
    }
}
else {
    Log "Venv already exists."
}

# Detect venv python
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $VenvPython = Join-Path $VenvDir "bin\python"
}

if (-not (Test-Path $VenvPython)) {
    Log "ERROR: No python in venv"
    exit 1
}

Log "Venv Python: $VenvPython"

# ---------------------------------------------
# UPGRADE PIP
# ---------------------------------------------
Log "Upgrading pip..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Log "ERROR upgrading pip"
    exit $LASTEXITCODE
}

# ---------------------------------------------
# INSTALL REQUIREMENTS
# ---------------------------------------------
Log "Installing dependencies..."
& $VenvPython -m pip install -r $ReqsFile
if ($LASTEXITCODE -ne 0) {
    Log "ERROR installing deps"
    exit $LASTEXITCODE
}

# ---------------------------------------------
# WRITE VENV INFO FILE
# ---------------------------------------------
$VenvInfoPath = Join-Path $ConfigDir "venv_info.json"

@{
    install_root    = $InstallRoot
    toolshed_root   = $ToolshedRoot
    rag_engine_root = $RagEngineRoot
    venv_dir        = $VenvDir
    venv_python     = $VenvPython
} | ConvertTo-Json -Depth 5 | Out-File -FilePath $VenvInfoPath -Encoding UTF8

Log "Wrote venv_info.json"

# ---------------------------------------------
# RUN BOOTSTRAP
# ---------------------------------------------
$BootstrapPath = Join-Path $ToolshedRoot "bootstrap.py"

if (Test-Path $BootstrapPath) {
    Log "Running bootstrap.py..."
    & $VenvPython $BootstrapPath
    if ($LASTEXITCODE -ne 0) {
        Log "ERROR: bootstrap.py failed"
        exit $LASTEXITCODE
    }
}
else {
    Log "WARNING: bootstrap.py missing, skipping."
}

Write-Output "`n=== AI ToolShed setup complete ===`n"
Write-Output "Venv Python: $VenvPython"
Write-Output "Log file:   $LogFile`n"

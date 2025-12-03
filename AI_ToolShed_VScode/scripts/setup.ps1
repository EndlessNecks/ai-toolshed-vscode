# =============================================
# AI ToolShed Setup Script (GENERIC INSTALL VERSION)
# - Detects install root from this script's location
# - Creates venv at <INSTALL_ROOT>\toolshed\.venv
# - Installs requirements from <INSTALL_ROOT>\toolshed\rag_engine\requirements.txt
# - Writes venv_info.json to <INSTALL_ROOT>\configs\venv_info.json
# =============================================

$ErrorActionPreference = "Stop"

Write-Output "`n=== AI ToolShed Python Environment Setup ===`n"

# ---------------------------------------------
# DETECT INSTALL ROOT
# ---------------------------------------------
# This script is expected at:
#   <INSTALL_ROOT>\scripts\setup.ps1
# So install root is the parent of this script's directory.

$ScriptRoot  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$InstallRoot = Split-Path -Parent $ScriptRoot

# Normalized for logs
Write-Output "Script Root : $ScriptRoot"
Write-Output "Install Root: $InstallRoot"

# ---------------------------------------------
# PROJECT PATHS (RELATIVE TO INSTALL ROOT)
# ---------------------------------------------
$ToolshedRoot  = Join-Path $InstallRoot "toolshed"
$RagEngineRoot = Join-Path $ToolshedRoot "rag_engine"
$ReqsFile      = Join-Path $RagEngineRoot "requirements.txt"
$VenvDir       = Join-Path $ToolshedRoot ".venv"
$LogsDir       = Join-Path $InstallRoot "logs"
$ConfigDir     = Join-Path $InstallRoot "configs"

# Ensure logs/config dirs
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}
if (-not (Test-Path $ConfigDir)) {
    New-Item -ItemType Directory -Path $ConfigDir | Out-Null
}

$LogFile = Join-Path $LogsDir "setup.log"

function Log {
    param([string]$Msg)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$timestamp [SETUP] $Msg"
    $line | Tee-Object -FilePath $LogFile -Append
}

Log "Install root     : $InstallRoot"
Log "Toolshed root    : $ToolshedRoot"
Log "RAG engine root  : $RagEngineRoot"
Log "Requirements file: $ReqsFile"
Log "Venv directory   : $VenvDir"

# ---------------------------------------------
# VALIDATE REQUIREMENTS FILE EXISTS
# ---------------------------------------------
if (-not (Test-Path $ReqsFile)) {
    Log "ERROR: Requirements file missing at: $ReqsFile"
    Write-Error "requirements.txt not found. Expected at $ReqsFile"
    exit 1
}

# ---------------------------------------------
# LOCATE PYTHON
# ---------------------------------------------
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}

if (-not $python) {
    Log "ERROR: No Python interpreter found."
    Write-Error "Python not found on PATH."
    exit 1
}

$PythonExe = $python.Source
Log "Using Python: $PythonExe"

# ---------------------------------------------
# CREATE VENV IF MISSING
# ---------------------------------------------
if (-not (Test-Path $VenvDir)) {
    Log "Creating venv at: $VenvDir"
    & $PythonExe -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Log "ERROR: venv creation failed (exit code $LASTEXITCODE)."
        exit $LASTEXITCODE
    }
} else {
    Log "Venv already exists."
}

# Detect venv Python path
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $VenvPython = Join-Path $VenvDir "bin\python"
}

if (-not (Test-Path $VenvPython)) {
    Log "ERROR: No python executable in venv."
    Write-Error "Failed to locate venv Python in $VenvDir"
    exit 1
}

Log "Venv Python: $VenvPython"

# ---------------------------------------------
# PIP UPGRADE
# ---------------------------------------------
Log "Upgrading pip..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: pip upgrade failed (exit code $LASTEXITCODE)."
    exit $LASTEXITCODE
}

# ---------------------------------------------
# INSTALL REQUIREMENTS
# ---------------------------------------------
Log "Installing dependencies from $ReqsFile..."
& $VenvPython -m pip install -r $ReqsFile
if ($LASTEXITCODE -ne 0) {
    Log "ERROR installing requirements (exit code $LASTEXITCODE)."
    exit $LASTEXITCODE
}

# ---------------------------------------------
# WRITE VENV INFO FILE
# ---------------------------------------------
$VenvInfoPath = Join-Path $ConfigDir "venv_info.json"

@{
    install_root   = $InstallRoot
    toolshed_root  = $ToolshedRoot
    rag_engine_root = $RagEngineRoot
    venv_dir       = $VenvDir
    venv_python    = $VenvPython
} | ConvertTo-Json -Depth 5 | Out-File -FilePath $VenvInfoPath -Encoding UTF8

Log "Wrote venv info → $VenvInfoPath"

Write-Output "`n=== AI ToolShed setup completed successfully ===`n"
Write-Output "Install Root: $InstallRoot"
Write-Output "Venv Python : $VenvPython"
Write-Output "Log file    : $LogFile`n"

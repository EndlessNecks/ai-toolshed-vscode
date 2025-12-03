# =============================================
# AI ToolShed Setup Script (FINAL WORKING VERSION)
# Hard-mapped to your confirmed project layout:
# D:\AI_Workspace\AI_ToolShed_VScode\toolshed\rag_engine\requirements.txt
# =============================================

$ErrorActionPreference = "Stop"

Write-Output "`n=== AI ToolShed Python Environment Setup ===`n"

# ---------------------------------------------
# PROJECT PATHS (ABSOLUTE — CONFIRMED BY USER)
# ---------------------------------------------
$ProjectRoot = "D:\AI_Workspace\AI_ToolShed_VScode"
$ToolshedRoot = Join-Path $ProjectRoot "toolshed"
$RagEngineRoot = Join-Path $ToolshedRoot "rag_engine"
$ReqsFile = Join-Path $RagEngineRoot "requirements.txt"
$VenvDir = Join-Path $ToolshedRoot ".venv"
$LogsDir = Join-Path $ProjectRoot "logs"

# Ensure logs dir
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}

$LogFile = Join-Path $LogsDir "setup.log"

function Log {
    param([string]$Msg)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$timestamp [SETUP] $Msg"
    $line | Tee-Object -FilePath $LogFile -Append
}

Log "Project root      : $ProjectRoot"
Log "Toolshed root     : $ToolshedRoot"
Log "RAG engine root   : $RagEngineRoot"
Log "Requirements file : $ReqsFile"
Log "Venv directory    : $VenvDir"

# ---------------------------------------------
# VALIDATE REQUIREMENTS FILE EXISTS
# ---------------------------------------------
if (-not (Test-Path $ReqsFile)) {
    Log "ERROR: Requirements file missing at: $ReqsFile"
    Write-Error "requirements.txt not found. Check your directory structure."
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
        Log "ERROR: venv creation failed."
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
    Log "ERROR: No python in venv."
    Write-Error "Failed to locate venv Python."
    exit 1
}

Log "Venv Python: $VenvPython"

# ---------------------------------------------
# PIP UPGRADE
# ---------------------------------------------
Log "Upgrading pip..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: pip upgrade failed."
    exit $LASTEXITCODE
}

# ---------------------------------------------
# INSTALL REQUIREMENTS
# ---------------------------------------------
Log "Installing dependencies..."
& $VenvPython -m pip install -r $ReqsFile
if ($LASTEXITCODE -ne 0) {
    Log "ERROR installing requirements."
    exit $LASTEXITCODE
}

# ---------------------------------------------
# WRITE VENV INFO FILE
# ---------------------------------------------
$ConfigDir = Join-Path $ProjectRoot "configs"
if (-not (Test-Path $ConfigDir)) {
    New-Item -ItemType Directory -Path $ConfigDir | Out-Null
}

$VenvInfoPath = Join-Path $ConfigDir "venv_info.json"

@{
    project_root = $ProjectRoot
    toolshed_root = $ToolshedRoot
    rag_engine_root = $RagEngineRoot
    venv_dir = $VenvDir
    venv_python = $VenvPython
} | ConvertTo-Json -Depth 5 | Out-File -FilePath $VenvInfoPath -Encoding UTF8

Log "Wrote venv info → $VenvInfoPath"

Write-Output "`n=== AI ToolShed setup completed successfully ===`n"
Write-Output "Venv Python: $VenvPython"
Write-Output "Log file:   $LogFile`n"

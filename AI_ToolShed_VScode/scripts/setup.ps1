# ---------------------------------------------
# AI ToolShed Setup Script (Corrected for toolshed/rag_engine layout)
# ---------------------------------------------

$ErrorActionPreference = "Stop"

Write-Output "=== AI ToolShed Python Environment Setup ==="

# ---------------------------------------------
# Resolve paths
# ---------------------------------------------
$ScriptRoot  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Join-Path $ScriptRoot ".." | Resolve-Path | Select-Object -ExpandProperty Path

Write-Output "Script Root : $ScriptRoot"
Write-Output "Project Root: $ProjectRoot"

# The real folder layout:
# ProjectRoot/
#   toolshed/
#     rag_engine/
#       requirements.txt
#     .venv/

$ToolshedRoot = Join-Path $ProjectRoot "toolshed"
$RagEngineRoot = Join-Path $ToolshedRoot "rag_engine"
$ReqsFile = Join-Path $RagEngineRoot "requirements.txt"

$VenvDir = Join-Path $ToolshedRoot ".venv"

$LogsDir = Join-Path $ProjectRoot "logs"
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

Log "=== Starting AI ToolShed setup ==="
Log "Project Root: $ProjectRoot"
Log "Toolshed Root: $ToolshedRoot"
Log "RAG Engine Root: $RagEngineRoot"
Log "Requirements File: $ReqsFile"
Log "Venv Directory: $VenvDir"

# ---------------------------------------------
# Validate requirements file exists
# ---------------------------------------------
if (-not (Test-Path $ReqsFile)) {
    Log "ERROR: rag_engine/requirements.txt not found at: $ReqsFile"
    Write-Error "rag_engine/requirements.txt not found. Make sure it exists before running setup."
    exit 1
}

# ---------------------------------------------
# Locate Python
# ---------------------------------------------
Log "Locating Python interpreter..."

$python = Get-Command python -ErrorAction SilentlyContinue

if (-not $python) {
    Log "No 'python' found, trying 'py' launcher..."
    $python = Get-Command py -ErrorAction SilentlyContinue

    if (-not $python) {
        Log "ERROR: No Python interpreter found."
        Write-Error "Python is not on PATH. Install Python 3.x and restart."
        exit 1
    } else {
        Log "Using 'py' launcher at: $($python.Source)"
    }
} else {
    Log "Using 'python' at: $($python.Source)"
}

$PythonExe = $python.Source

# ---------------------------------------------
# Create venv
# ---------------------------------------------
if (Test-Path $VenvDir) {
    Log "Virtual environment already exists at: $VenvDir"
} else {
    Log "Creating virtual environment..."
    & $PythonExe -m venv $VenvDir

    if ($LASTEXITCODE -ne 0) {
        Log "ERROR: Failed to create venv (exit code $LASTEXITCODE)"
        Write-Error "Failed to create virtual environment."
        exit $LASTEXITCODE
    }
}

# Determine venv python path
$VenvPythonWin = Join-Path $VenvDir "Scripts\python.exe"
$VenvPythonNix = Join-Path $VenvDir "bin\python"

$VenvPython = $VenvPythonWin
if (-not (Test-Path $VenvPython)) {
    $VenvPython = $VenvPythonNix
}

if (-not (Test-Path $VenvPython)) {
    Log "ERROR: Could not find python inside venv."
    Write-Error "Could not locate python executable in virtual environment."
    exit 1
}

Log "Venv Python: $VenvPython"

# ---------------------------------------------
# pip upgrade + install deps
# ---------------------------------------------
Log "Upgrading pip to >=23.0..."
& $VenvPython -m pip install --upgrade pip

if ($LASTEXITCODE -ne 0) {
    Log "ERROR: pip upgrade failed."
    Write-Error "pip upgrade failed."
    exit $LASTEXITCODE
}

Log "Installing Python dependencies..."
& $VenvPython -m pip install -r $ReqsFile

if ($LASTEXITCODE -ne 0) {
    Log "ERROR: dependency installation failed."
    Write-Error "Python dependency installation failed."
    exit $LASTEXITCODE
}

# ---------------------------------------------
# Save venv info
# ---------------------------------------------
$ConfigDir = Join-Path $ProjectRoot "configs"
if (-not (Test-Path $ConfigDir)) {
    New-Item -ItemType Directory -Path $ConfigDir | Out-Null
}

$VenvInfoFile = Join-Path $ConfigDir "venv_info.json"

$Data = @{
    project_root = $ProjectRoot
    toolshed_root = $ToolshedRoot
    rag_engine_root = $RagEngineRoot
    venv_dir = $VenvDir
    venv_python = $VenvPython
} | ConvertTo-Json -Depth 5

$Data | Out-File -FilePath $VenvInfoFile -Encoding UTF8

Log "Wrote venv info to $VenvInfoFile"
Log "=== Setup completed successfully ==="

Write-Output ""
Write-Output "=== AI ToolShed setup completed successfully ==="
Write-Output "Venv Python: $VenvPython"
Write-Output "Log file: $LogFile"
Write-Output ""

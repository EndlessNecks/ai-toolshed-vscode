# =============================================
# AI ToolShed — Rebuild Full Index
# Reindexes ONLY: <INSTALL_ROOT>/workspace_files
# =============================================

$ErrorActionPreference = "Stop"

Write-Output "`n=== AI ToolShed: Rebuilding Index ===`n"

# Detect install root from this script's directory
$ScriptRoot  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$InstallRoot = Split-Path -Parent $ScriptRoot

# Load venv info
$VenvInfoPath = Join-Path $InstallRoot "configs\venv_info.json"
if (-not (Test-Path $VenvInfoPath)) {
    Write-Error "venv_info.json missing — run setup.ps1 first."
    exit 1
}

$info = Get-Content $VenvInfoPath | ConvertFrom-Json

$python = $info.venv_python
$ragRoot = $info.rag_engine_root

$Indexer = Join-Path $ragRoot "indexer.py"

if (-not (Test-Path $Indexer)) {
    Write-Error "indexer.py missing: $Indexer"
    exit 1
}

Write-Output "Using Python: $python"
Write-Output "Indexing root: $(Join-Path $InstallRoot 'workspace_files')"
Write-Output ""

# Run the full indexer
& $python $Indexer
if ($LASTEXITCODE -ne 0) {
    Write-Error "Index rebuild failed (exit code $LASTEXITCODE)"
    exit $LASTEXITCODE
}

Write-Output "`n=== Index Rebuild Complete ===`n"

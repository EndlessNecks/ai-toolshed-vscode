# ---------------------------------------------
# AI ToolShed - Rebuild RAG Index
# ---------------------------------------------
$ErrorActionPreference = "Stop"

Write-Host "`n=== AI ToolShed: Rebuilding RAG Index ===" -ForegroundColor Cyan

# Script root
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ToolShedRoot = Join-Path $ScriptRoot ".." | Resolve-Path
$EngineRoot   = Join-Path $ToolShedRoot "toolshed\rag_engine"

Write-Host "Script Root: $ScriptRoot"
Write-Host "ToolShed Root: $ToolShedRoot"
Write-Host "Engine Root: $EngineRoot"

# Venv
$VenvPath = Join-Path $ToolShedRoot "toolshed\.venv"
$Activate = Join-Path $VenvPath "Scripts\Activate.ps1"

if (-not (Test-Path $Activate)) {
    Write-Host "ERROR: Virtual environment missing inside extension." -ForegroundColor Red
    exit 1
}

Write-Host "Activating virtual environment..."
. $Activate

# Python path
$Python = Join-Path $VenvPath "Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "ERROR: python.exe missing in venv!" -ForegroundColor Red
    exit 1
}

# Indexer path
$Indexer = Join-Path $EngineRoot "indexer.py"
if (-not (Test-Path $Indexer)) {
    Write-Host "ERROR: indexer.py missing!" -ForegroundColor Red
    exit 1
}

Write-Host "Running indexer..." -ForegroundColor Cyan
& $Python $Indexer

if ($LASTEXITCODE -ne 0) {
    Write-Host "RAG index build failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== RAG Index Build Complete! ===" -ForegroundColor Green
exit 0

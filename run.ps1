# 🧹 SWEEPER Windows Instant One-Liner
# Usage:
#   irm https://raw.githubusercontent.com/sovon1/sweeper/main/run.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "   ____                                    " -ForegroundColor Cyan
Write-Host "  / ___|_      _____  ___ _ __   ___ _ __  " -ForegroundColor Cyan
Write-Host "  \___ \ \ /\ / / _ \/ _ \ '_ \ / _ \ '__| " -ForegroundColor Cyan
Write-Host "   ___) \ V  V /  __/  __/ |_) |  __/ |    " -ForegroundColor Cyan
Write-Host "  |____/ \_/\_/ \___|\___| .__/ \___|_|    " -ForegroundColor Cyan
Write-Host "                         |_|   v1.0.0 ✨   " -ForegroundColor Magenta
Write-Host "  The intelligent, zero-dependency folder organizer" -ForegroundColor DarkGray
Write-Host ""

$installDir = [System.IO.Path]::Combine($env:LOCALAPPDATA, "Programs", "sweeper")
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

$sweeperScript = [System.IO.Path]::Combine($installDir, "sweeper.py")
$sweeperExe = [System.IO.Path]::Combine($installDir, "sweeper.exe")

# Check if Python is available
$hasPython = Get-Command python -ErrorAction SilentlyContinue

if ($hasPython) {
    Write-Host "⚡ Python detected. Launching sweeper..." -ForegroundColor Green
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/sovon1/sweeper/main/sweeper.py" -OutFile $sweeperScript -UseBasicParsing
    python $sweeperScript @args
} else {
    Write-Host "⚡ Standalone mode (zero Python required). Fetching sweeper.exe..." -ForegroundColor Cyan
    $releaseUrl = "https://github.com/sovon1/sweeper/releases/latest/download/sweeper-windows-amd64.exe"
    try {
        Invoke-WebRequest -Uri $releaseUrl -OutFile $sweeperExe -UseBasicParsing
        & $sweeperExe @args
    } catch {
        Write-Host "Could not fetch precompiled binary. Please install Python or download from GitHub Releases." -ForegroundColor Red
    }
}

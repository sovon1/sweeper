$ErrorActionPreference = 'SilentlyContinue'

$installDir = [System.IO.Path]::Combine($env:LOCALAPPDATA, 'Programs', 'sweeper')
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

$sweeperScript = [System.IO.Path]::Combine($installDir, 'sweeper.py')
$sweeperCmd = [System.IO.Path]::Combine($installDir, 'sweeper.cmd')
$sweeperExe = [System.IO.Path]::Combine($installDir, 'sweeper.exe')

# Create global command wrapper
Set-Content -Path $sweeperCmd -Value ('@echo off' + [char]13 + [char]10 + 'python "%~dp0sweeper.py" %*') -Force -Encoding ASCII

# Add to user PATH persistently if not already there
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($userPath -split ';' -notcontains $installDir) {
    [Environment]::SetEnvironmentVariable('Path', ($userPath + ';' + $installDir), 'User')
}
if ($env:Path -split ';' -notcontains $installDir) {
    $env:Path = $env:Path + ';' + $installDir
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/sovon1/sweeper/main/sweeper.py' -OutFile $sweeperScript -UseBasicParsing
    & python $sweeperScript @args
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    Set-Content -Path $sweeperCmd -Value ('@echo off' + [char]13 + [char]10 + 'py "%~dp0sweeper.py" %*') -Force -Encoding ASCII
    Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/sovon1/sweeper/main/sweeper.py' -OutFile $sweeperScript -UseBasicParsing
    & py $sweeperScript @args
} else {
    Write-Host 'Fetching standalone sweeper.exe...' -ForegroundColor Cyan
    $releaseUrl = 'https://github.com/sovon1/sweeper/releases/latest/download/sweeper-windows-amd64.exe'
    try {
        Invoke-WebRequest -Uri $releaseUrl -OutFile $sweeperExe -UseBasicParsing
        & $sweeperExe @args
    } catch {
        Write-Host 'Could not fetch precompiled binary. Please install Python or visit https://github.com/sovon1/sweeper/releases' -ForegroundColor Red
    }
}
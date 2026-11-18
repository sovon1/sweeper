@echo off
setlocal

set "INSTALL_DIR=%LOCALAPPDATA%\Programs\sweeper"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

set "SWEEPER_PY=%INSTALL_DIR%\sweeper.py"
set "SWEEPER_EXE=%INSTALL_DIR%\sweeper.exe"

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    curl -fsSL "https://raw.githubusercontent.com/sovon1/sweeper/main/sweeper.py" -o "%SWEEPER_PY%"
    python "%SWEEPER_PY%" %*
    exit /b %ERRORLEVEL%
)

where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    curl -fsSL "https://raw.githubusercontent.com/sovon1/sweeper/main/sweeper.py" -o "%SWEEPER_PY%"
    py "%SWEEPER_PY%" %*
    exit /b %ERRORLEVEL%
)

echo [sweeper] Standalone mode (zero Python required). Fetching sweeper.exe...
curl -fsSL "https://github.com/sovon1/sweeper/releases/latest/download/sweeper-windows-amd64.exe" -o "%SWEEPER_EXE%"
if exist "%SWEEPER_EXE%" (
    "%SWEEPER_EXE%" %*
    exit /b %ERRORLEVEL%
) else (
    echo [sweeper] Error: Could not download sweeper.exe. Please install Python or visit https://github.com/sovon1/sweeper/releases
    exit /b 1
)

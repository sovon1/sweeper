@echo off
setlocal

set "INSTALL_DIR=%LOCALAPPDATA%\Programs\sweeper"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

set "SWEEPER_PY=%INSTALL_DIR%\sweeper.py"
set "SWEEPER_CMD=%INSTALL_DIR%\sweeper.cmd"
set "SWEEPER_EXE=%INSTALL_DIR%\sweeper.exe"

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    curl -fsSL "https://raw.githubusercontent.com/sovon1/sweeper/main/sweeper.py" -o "%SWEEPER_PY%"
    echo @echo off > "%SWEEPER_CMD%"
    echo python "%%~dp0sweeper.py" %%* >> "%SWEEPER_CMD%"
    echo %PATH% | find /i "%INSTALL_DIR%" >nul 2>&1
    if errorlevel 1 (
        setx PATH "%PATH%;%INSTALL_DIR%" >nul 2>&1
    )
    python "%SWEEPER_PY%" %*
    exit /b %ERRORLEVEL%
)

where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    curl -fsSL "https://raw.githubusercontent.com/sovon1/sweeper/main/sweeper.py" -o "%SWEEPER_PY%"
    echo @echo off > "%SWEEPER_CMD%"
    echo py "%%~dp0sweeper.py" %%* >> "%SWEEPER_CMD%"
    echo %PATH% | find /i "%INSTALL_DIR%" >nul 2>&1
    if errorlevel 1 (
        setx PATH "%PATH%;%INSTALL_DIR%" >nul 2>&1
    )
    py "%SWEEPER_PY%" %*
    exit /b %ERRORLEVEL%
)

echo [sweeper] Standalone mode (zero Python required). Fetching sweeper.exe...
curl -fsSL "https://github.com/sovon1/sweeper/releases/latest/download/sweeper-windows-amd64.exe" -o "%SWEEPER_EXE%"
if exist "%SWEEPER_EXE%" (
    echo %PATH% | find /i "%INSTALL_DIR%" >nul 2>&1
    if errorlevel 1 (
        setx PATH "%PATH%;%INSTALL_DIR%" >nul 2>&1
    )
    "%SWEEPER_EXE%" %*
    exit /b %ERRORLEVEL%
) else (
    echo [sweeper] Error: Could not download sweeper.exe. Please install Python or visit https://github.com/sovon1/sweeper/releases
    exit /b 1
)
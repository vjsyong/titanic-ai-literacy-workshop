@echo off
setlocal EnableExtensions

title Vibe Coding Launcher

:: Work from the workshop project directory (the parent of this
:: "deployment" folder), so the OpenCode Web UI opens the workshop
:: project (AGENTS.md + 01_eda.py / 02_train.py / 03_dashboard.py).
:: pushd also handles UNC/network paths better than cd /d.
pushd "%~dp0.." >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR:
    echo The launcher folder could not be accessed.
    echo.
    echo Copy the Vibe Coding folder to your computer and try again.
    echo.
    pause
    exit /b 1
)

where powershell.exe >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR:
    echo Windows PowerShell could not be found.
    echo.
    echo Please show this message to your instructor.
    echo.
    pause
    popd
    exit /b 1
)

if not exist "%~dp0oneclick.ps1" (
    echo.
    echo ERROR:
    echo oneclick.ps1 is missing.
    echo.
    echo Keep these files together:
    echo   START VIBE CODING.bat
    echo   oneclick.ps1
    echo   key.txt
    echo.
    pause
    popd
    exit /b 1
)

if not exist "%~dp0key.txt" (
    echo.
    echo ERROR:
    echo key.txt is missing.
    echo.
    echo Please obtain a complete deployment package from your instructor.
    echo.
    pause
    popd
    exit /b 1
)

powershell.exe ^
    -NoLogo ^
    -NoProfile ^
    -ExecutionPolicy Bypass ^
    -File "%~dp0oneclick.ps1"

set "RESULT=%errorlevel%"

echo.
echo ==============================================
echo Launcher exit code: %RESULT%
echo ==============================================
echo.

if not "%RESULT%"=="0" (
    echo              SETUP DID NOT FINISH
    echo.
    echo Please take a screenshot of this window.
    echo You can safely run this launcher again.
    echo If it repeatedly fails, run:
    echo   REPAIR VIBE CODING.bat
    echo.
)

echo Detailed support log folder:
echo   %LOCALAPPDATA%\VibeCoding\logs
echo.
echo Send the instructor: this screenshot + latest.log
echo.
pause
popd
exit /b %RESULT%

@echo off
setlocal EnableExtensions

title Reset Workshop Progress

pushd "%~dp0..\.." >nul 2>&1

if errorlevel 1 (
    echo Unable to access the deployment folder.
    pause
    exit /b 1
)

if not exist "%~dp0reset_workshop.ps1" (
    echo reset_workshop.ps1 is missing.
    pause
    popd
    exit /b 1
)

echo.
echo ==============================================
echo         RESET WORKSHOP PROGRESS
echo ==============================================
echo.
echo This restores the three workshop scripts to their
echo original scaffold state and deletes generated
echo artifacts.
echo.
echo The classroom runtime, the API key, and
echo data\titanic.csv are NOT touched.
echo.

powershell.exe ^
    -NoLogo ^
    -NoProfile ^
    -ExecutionPolicy Bypass ^
    -File "%~dp0reset_workshop.ps1"

set "RESULT=%errorlevel%"

echo.
echo ==============================================
echo Reset exit code: %RESULT%
echo ==============================================
echo.

if not "%RESULT%"=="0" (
    echo Reset did not complete.
    echo Please send the instructor:
    echo   %LOCALAPPDATA%\VibeCoding\logs\latest.log
    echo.
)
pause
popd
exit /b %RESULT%

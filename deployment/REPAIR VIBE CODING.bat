@echo off
setlocal EnableExtensions

title Vibe Coding Repair

pushd "%~dp0.." >nul 2>&1

if errorlevel 1 (
    echo Unable to access the deployment folder.
    pause
    exit /b 1
)

if not exist "%~dp0oneclick.ps1" (
    echo oneclick.ps1 is missing.
    pause
    popd
    exit /b 1
)

echo.
echo ==============================================
echo             VIBE CODING REPAIR
echo ==============================================
echo.
echo This will revalidate/rebuild the classroom Python
echo environment, Node.js runtime, OpenCode installation,
echo Tencent connection, and OpenCode profile.
echo.
echo Student project files are not touched.
echo.

powershell.exe ^
    -NoLogo ^
    -NoProfile ^
    -ExecutionPolicy Bypass ^
    -File "%~dp0oneclick.ps1" ^
    -Repair

set "RESULT=%errorlevel%"

echo.
echo ==============================================
echo Repair exit code: %RESULT%
echo ==============================================
echo.

if not "%RESULT%"=="0" (
    echo Repair did not complete.
    echo Please send the instructor:
    echo   %LOCALAPPDATA%\VibeCoding\logs\latest.log
    echo.
)
pause
popd
exit /b %RESULT%

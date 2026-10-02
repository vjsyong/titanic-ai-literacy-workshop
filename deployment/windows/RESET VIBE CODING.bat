@echo off
setlocal EnableExtensions

title Reset Vibe Coding Environment

echo.
echo ==============================================
echo       RESET VIBE CODING ENVIRONMENT
echo ==============================================
echo.
echo This removes ONLY the managed classroom runtime:
echo.
echo   %%LOCALAPPDATA%%\VibeCoding
echo   %%USERPROFILE%%\.vibecoding
echo.
echo It does NOT remove student projects, system Python,
echo system Node.js, or the student's normal OpenCode data.
echo.
set /p CONFIRM=Type RESET to continue: 

if /I not "%CONFIRM%"=="RESET" (
    echo Cancelled.
    exit /b 0
)

:: Best-effort stop of the isolated OpenCode service first.
if exist "%LOCALAPPDATA%\VibeCoding\opencode-cli\opencode.cmd" (
    set "XDG_DATA_HOME=%LOCALAPPDATA%\VibeCoding\opencode-profile\data"
    set "XDG_CONFIG_HOME=%LOCALAPPDATA%\VibeCoding\opencode-profile\config"
    set "XDG_CACHE_HOME=%LOCALAPPDATA%\VibeCoding\opencode-profile\cache"
    set "XDG_STATE_HOME=%LOCALAPPDATA%\VibeCoding\opencode-profile\state"
    "%LOCALAPPDATA%\VibeCoding\opencode-cli\opencode.cmd" service stop >nul 2>&1
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command ^
    "Remove-Item -LiteralPath $env:LOCALAPPDATA\VibeCoding -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -LiteralPath $env:USERPROFILE\.vibecoding -Recurse -Force -ErrorAction SilentlyContinue"

echo.
echo Classroom environment reset.
echo Run START VIBE CODING.bat to rebuild it.
echo.
pause

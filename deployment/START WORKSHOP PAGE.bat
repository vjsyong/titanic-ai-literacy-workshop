@echo off
setlocal EnableExtensions

title Workshop Web Page

:: Work from the workshop project directory (the parent of this
:: "deployment" folder) so 04_classroom.py finds its files.
:: pushd also handles UNC/network paths better than cd /d.
pushd "%~dp0.." >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR:
    echo The workshop folder could not be accessed.
    echo.
    echo Copy the workshop folder to your computer and try again.
    echo.
    pause
    exit /b 1
)

if not exist "serve_workshop.py" (
    echo.
    echo ERROR:
    echo serve_workshop.py is missing from the workshop folder.
    echo.
    echo Please ask your instructor for a complete workshop folder.
    echo.
    pause
    popd
    exit /b 1
)

set "CLASS_PYTHON=%LOCALAPPDATA%\VibeCoding\python\Scripts\python.exe"

if not exist "%CLASS_PYTHON%" (
    echo.
    echo ERROR:
    echo The Vibe Coding environment is not set up yet.
    echo.
    echo First double-click:
    echo   START VIBE CODING.bat
    echo.
    echo Then run this file again.
    echo.
    pause
    popd
    exit /b 1
)

"%CLASS_PYTHON%" "serve_workshop.py"

set "RESULT=%errorlevel%"

if not "%RESULT%"=="0" (
    echo.
    echo The workshop page could not be started.
    echo.
    echo Try:
    echo   1. Run this file again.
    echo   2. If it still fails, double-click REPAIR VIBE CODING.bat.
    echo   3. Then show your instructor this window.
    echo.
    pause
    popd
    exit /b %RESULT%
)

echo.
echo The workshop page is ready in your browser.
echo It is safe to close this window.
echo.
timeout /t 5 >nul
popd
exit /b 0

# ============================================================
# Reset Workshop Progress
# ============================================================
# Restores the workshop project to its original scaffold state:
# - Restores 01_eda.py / 02_train.py / 03_dashboard.py from the
#   bundled deployment\baseline copies (git fallback for the
#   instructor's working copy).
# - Deletes generated artifacts (titanic_model.pkl, __pycache__,
#   .workshop logs).
#
# Deliberately NOT touched:
# - The classroom runtime (%LOCALAPPDATA%\VibeCoding)
# - The API credential (deployment\key.txt, %USERPROFILE%\.vibecoding)
# - data\titanic.csv
# - web\ (UI source and the committed web\dist bundle)
# - Any other file in the workshop project
#
# The running workshop server hot-reloads the restored scripts, so
# an already-open page refreshes back to step 1 by itself.
# ============================================================

param(
    [switch]$Force
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$WorkshopRoot = (Get-Item -LiteralPath $PSScriptRoot).Parent.FullName
$BaselineRoot = Join-Path $PSScriptRoot "baseline"
$WorkshopScripts = @("01_eda.py", "02_train.py", "03_dashboard.py")

Write-Host ""
Write-Host "==============================================" 
Write-Host "         RESET WORKSHOP PROGRESS" 
Write-Host "==============================================" 
Write-Host ""
Write-Host "Restores the three workshop scripts to their"
Write-Host "original scaffold state and deletes generated"
Write-Host "artifacts (titanic_model.pkl, caches, logs)."
Write-Host ""
Write-Host "NOT touched: classroom runtime, API key,"
Write-Host "data\titanic.csv, web UI."
Write-Host ""

$confirmed = $false

if ($Force) {
    $confirmed = $true
}
else {
    $answer = Read-Host "Type RESET to continue"

    if ($answer -ieq "RESET") {
        $confirmed = $true
    }
}

if (-not $confirmed) {
    Write-Host "Cancelled."
    exit 0
}

# ============================================================
# Console helpers (kept identical to oneclick.ps1)
# ============================================================

function Write-Section {
    param([string]$Text)
    Write-Host ""
    Write-Host "== $Text ==" -ForegroundColor Cyan
}

function Write-OK {
    param([string]$Text)
    Write-Host "[OK] $Text" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Text)
    Write-Host "[WARN] $Text" -ForegroundColor Yellow
}

# ------------------------------------------------------------
# 1. Restore the workshop scripts
# ------------------------------------------------------------
Write-Section "Restoring workshop scripts"

$restored = @()

foreach ($scriptName in $WorkshopScripts) {
    $target = Join-Path $WorkshopRoot $scriptName
    $baseline = Join-Path $BaselineRoot $scriptName

    if (Test-Path -LiteralPath $baseline) {
        Copy-Item -LiteralPath $baseline -Destination $target -Force
        $restored += $scriptName
        Write-OK "Restored $scriptName from baseline"
    }
    else {
        # Fallback for the instructor's git working copy: the
        # committed scaffolds are the same pristine originals.
        Push-Location -LiteralPath $WorkshopRoot
        try {
            $gitOutput = & git checkout -- $scriptName 2>&1
            $gitExit = $LASTEXITCODE
        }
        finally {
            Pop-Location
        }

        if ($gitExit -eq 0) {
            $restored += $scriptName
            Write-OK "Restored $scriptName via git"
        }
        else {
            Write-Warn "Could not restore ${scriptName}: no baseline copy and git restore failed."
            if ($gitOutput) {
                Write-Host $gitOutput -ForegroundColor DarkGray
            }
        }
    }
}

if ($restored.Count -eq 0) {
    Write-Host ""
    Write-Host "Nothing was restored. Workshop progress unchanged." -ForegroundColor Yellow
    exit 1
}

# ------------------------------------------------------------
# 2. Delete generated artifacts
# ------------------------------------------------------------
Write-Section "Removing generated artifacts"

$artifacts = @(
    (Join-Path $WorkshopRoot "titanic_model.pkl"),
    (Join-Path $WorkshopRoot "__pycache__"),
    (Join-Path $WorkshopRoot ".workshop")
)

foreach ($artifact in $artifacts) {
    if (Test-Path -LiteralPath $artifact) {
        try {
            Remove-Item -LiteralPath $artifact -Recurse -Force -ErrorAction Stop
            Write-OK "Removed $(Split-Path -Leaf $artifact)"
        }
        catch {
            # .workshop logs may be locked by the running page server;
            # that is harmless, the files regenerate.
            Write-Warn "Could not remove $(Split-Path -Leaf $artifact) (in use?). Safe to ignore."
        }
    }
}

# ------------------------------------------------------------
# 3. Make sure the workshop page reflects the reset
# ------------------------------------------------------------
Write-Section "Workshop page"

$serve = Join-Path $WorkshopRoot "serve_workshop.py"
$classPython = Join-Path $env:LOCALAPPDATA "VibeCoding\python\Scripts\python.exe"

$pageRunning = $false

try {
    $probe = Invoke-WebRequest `
        -Uri "http://127.0.0.1:4097/api/health" `
        -UseBasicParsing `
        -TimeoutSec 3

    if ($probe.StatusCode -ge 200 -and $probe.StatusCode -lt 500) {
        $pageRunning = $true
    }
}
catch {}

if ($pageRunning) {
    Write-OK "Workshop page is running - the open tab refreshes back to step 1 by itself."
}
elseif ((Test-Path -LiteralPath $classPython) -and (Test-Path -LiteralPath $serve)) {
    Push-Location -LiteralPath $WorkshopRoot
    try {
        & $classPython $serve | Out-Host
        $serveExit = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    if ($serveExit -eq 0) {
        Write-OK "Workshop page restarted."
    }
    else {
        Write-Warn "Workshop page did not start. Use START WORKSHOP PAGE.bat."
    }
}
else {
    Write-Warn "Workshop page is not running. Start it with START WORKSHOP PAGE.bat."
}

# ------------------------------------------------------------
# Done
# ------------------------------------------------------------
Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "          WORKSHOP RESET COMPLETE" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""
Write-Host "All 18 checkpoints are locked again." 
Write-Host "Tip: start a fresh chat with the AI Teaching Assistant" 
Write-Host "so it does not remember the previous run." 
Write-Host "Reference prompts already unlocked in this browser stay" 
Write-Host "unlocked (clear the site's data to start them fresh)." 
Write-Host ""
exit 0

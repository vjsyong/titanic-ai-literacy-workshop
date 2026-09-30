param(
    [switch]$Repair,
    [switch]$SkipTencentTest
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# ============================================================
# Vibe Coding Classroom Bootstrap
# ============================================================
# Design goals:
# - No Administrator rights required
# - Do not change the student's permanent PATH
# - Reuse healthy Python 3.12 when possible; otherwise install
#   a private Python 3.12 runtime
# - Use a private, checksummed Node.js runtime
# - Use a private OpenCode V2 npm prefix
# - Isolate OpenCode data/config/cache/state from any existing
#   OpenCode installation
# - Force the classroom model/provider at runtime so project
#   configs cannot accidentally redirect inference elsewhere
# - Never kill an unknown process just because it owns port 4096
# - Every run is safe to repeat
# - Keep a support log
#
# Tencent:
# - Endpoint: https://tokenhub-intl.tencentcloudmaas.com/v1
# - Model:    glm-5.3-flash
# - key.txt beside this script is copied to:
#       %USERPROFILE%\.vibecoding\tencent-key.txt
#   and referenced through OpenCode's {file:~...} substitution.
# ============================================================

$BootstrapVersion = "2026.09.30.13"

# ----------------------------
# Pinned classroom runtimes
# ----------------------------
# Python 3.12.10 is intentionally pinned because it is the final
# Python 3.12 release with official Windows binary installers.
$PythonVersion = "3.12.10"

# Current Node 24 LTS release at packaging time.
$NodeVersion = "24.21.0"

# Stay on the latest OpenCode V2 build without crossing to a
# future major release.
$OpenCodePackage = "@opencode/cli@2.0.20"

# The classroom Python packages the workshop scripts need. The list is
# stored in the package-cache state file, so changing it here forces a
# fresh install check on machines that already ran an older launcher.
$WorkshopPackageSignature = "pandas,scikit-learn,fastapi,uvicorn"

# ----------------------------
# Tencent configuration
# ----------------------------
$TencentBaseUrl = "https://tokenhub-intl.tencentcloudmaas.com/v1"
$TencentCompletionUrl = "$TencentBaseUrl/chat/completions"
$TencentProviderId = "tencent"
$TencentModelId = "glm-5.3-flash"
$TencentModelRef = "$TencentProviderId/$TencentModelId"

# ----------------------------
# Web UI configuration
# ----------------------------
$PreferredPort = 4096
$LastPort = 4196
$PreferredWorkshopPort = 4097
$LastWorkshopPort = 4197
$OpenCodeUsername = "opencode"

# ----------------------------
# Per-user locations
# ----------------------------
$LocalAppData = [Environment]::GetFolderPath("LocalApplicationData")
$UserProfile = [Environment]::GetFolderPath("UserProfile")

if ([string]::IsNullOrWhiteSpace($LocalAppData)) {
    throw "Windows LocalAppData could not be resolved."
}
if ([string]::IsNullOrWhiteSpace($UserProfile)) {
    throw "Windows user profile directory could not be resolved."
}

$AppRoot = Join-Path $LocalAppData "VibeCoding"
$RuntimeRoot = Join-Path $AppRoot "runtime"
$DownloadRoot = Join-Path $AppRoot "downloads"
$LogRoot = Join-Path $AppRoot "logs"
$StateRoot = Join-Path $AppRoot "state"

$PythonManagedRoot = Join-Path $RuntimeRoot "python-$PythonVersion"
$PythonVenvRoot = Join-Path $AppRoot "python"
$NodeRoot = Join-Path $RuntimeRoot "node-v$NodeVersion"

$OpenCodePrefix = Join-Path $AppRoot "opencode-cli"
$OpenCodeProfile = Join-Path $AppRoot "opencode-profile"
$NpmCache = Join-Path $AppRoot "npm-cache"
$NpmGlobal = Join-Path $AppRoot "npm-global"

$DeploymentKeyFile = Join-Path $PSScriptRoot "key.txt"
$SecretRoot = Join-Path $UserProfile ".vibecoding"
$TencentKeyFile = Join-Path $SecretRoot "tencent-key.txt"

$CredentialsFile = Join-Path $StateRoot "web-credentials.json"
$TencentTestStateFile = Join-Path $StateRoot "tencent-test.json"
$OpenCodeProviderTestStateFile = Join-Path $StateRoot "opencode-provider-test.json"

$PayloadRoot = Join-Path $PSScriptRoot "payload"

# The workshop project (AGENTS.md, 01_eda.py, 02_train.py, 03_dashboard.py)
# lives in the parent of this deployment folder. The OpenCode Web UI service
# should open that project by default, so the launcher pins the service
# working directory to the workshop root.
$ClassroomProjectRoot = (Get-Item -LiteralPath $PSScriptRoot).Parent.FullName

$TimeStamp = Get-Date -Format "yyyyMMdd-HHmmss"
$LogFile = Join-Path $LogRoot "setup-$TimeStamp.log"
$LatestLog = Join-Path $LogRoot "latest.log"

$TranscriptStarted = $false
$Mutex = $null
$MutexAcquired = $false
$ExitCode = 0

# ============================================================
# Console helpers
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

# ============================================================
# Filesystem helpers
# ============================================================

function Ensure-Directory {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Remove-Robust {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    for ($i = 1; $i -le 3; $i++) {
        try {
            Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
            return
        }
        catch {
            if ($i -eq 3) {
                throw "Could not remove '$Path'. Close development tools and run REPAIR VIBE CODING.bat."
            }
            Start-Sleep -Milliseconds (500 * $i)
        }
    }
}

# ============================================================
# Platform detection
# ============================================================

function Get-WindowsArchitecture {
    $architecture = $env:PROCESSOR_ARCHITEW6432
    if ([string]::IsNullOrWhiteSpace($architecture)) {
        $architecture = $env:PROCESSOR_ARCHITECTURE
    }

    switch ($architecture.ToUpperInvariant()) {
        "AMD64" { return "x64" }
        "ARM64" { return "arm64" }
        default {
            throw "Unsupported Windows architecture: $architecture. This package supports 64-bit x64 and ARM64 Windows."
        }
    }
}

# ============================================================
# Proxy handling
# ============================================================

function Ensure-LoopbackNoProxy {
    $required = @("localhost", "127.0.0.1", "::1")
    $current = @()

    if (-not [string]::IsNullOrWhiteSpace($env:NO_PROXY)) {
        $current = @(
            $env:NO_PROXY -split "," |
            ForEach-Object { $_.Trim() } |
            Where-Object { $_ }
        )
    }

    foreach ($item in $required) {
        if ($current -notcontains $item) {
            $current += $item
        }
    }

    $env:NO_PROXY = ($current -join ",")
    $env:no_proxy = $env:NO_PROXY
}

# ============================================================
# Download helpers
# ============================================================

function Copy-PayloadIfPresent {
    param(
        [string]$FileName,
        [string]$Destination
    )

    $source = Join-Path $PayloadRoot $FileName

    if (Test-Path -LiteralPath $source) {
        Ensure-Directory (Split-Path -Parent $Destination)
        Copy-Item -LiteralPath $source -Destination $Destination -Force
        Write-Host "Using bundled payload: $FileName" -ForegroundColor DarkGray
        return $true
    }

    return $false
}

function Download-File {
    param(
        [Parameter(Mandatory=$true)][string]$Uri,
        [Parameter(Mandatory=$true)][string]$Destination,
        [Parameter(Mandatory=$true)][string]$Description
    )

    Ensure-Directory (Split-Path -Parent $Destination)

    for ($attempt = 1; $attempt -le 3; $attempt++) {
        try {
            if (Test-Path -LiteralPath $Destination) {
                Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
            }

            Write-Host "Downloading $Description (attempt $attempt/3)..." -ForegroundColor DarkGray

            Invoke-WebRequest `
                -Uri $Uri `
                -OutFile $Destination `
                -UseBasicParsing `
                -TimeoutSec 180 `
                -Headers @{ "User-Agent" = "VibeCodingBootstrap/$BootstrapVersion" }

            $file = Get-Item -LiteralPath $Destination -ErrorAction Stop
            if ($file.Length -lt 1024) {
                throw "Downloaded file is unexpectedly small."
            }

            return
        }
        catch {
            Write-Warn "$Description download attempt $attempt failed: $($_.Exception.Message)"
            if ($attempt -lt 3) {
                Start-Sleep -Seconds ([int][Math]::Pow(2, $attempt))
            }
        }
    }

    # BITS can succeed on managed Windows networks where
    # Invoke-WebRequest behaves poorly.
    if (Get-Command Start-BitsTransfer -ErrorAction SilentlyContinue) {
        try {
            Write-Host "Trying Windows BITS for $Description..." -ForegroundColor DarkGray

            if (Test-Path -LiteralPath $Destination) {
                Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
            }

            Start-BitsTransfer -Source $Uri -Destination $Destination -ErrorAction Stop

            if ((Get-Item -LiteralPath $Destination).Length -ge 1024) {
                return
            }
        }
        catch {
            Write-Warn "BITS fallback failed: $($_.Exception.Message)"
        }
    }

    throw @"
Unable to download $Description.

Check:
- Internet access
- Captive portal/login page
- Campus firewall
- VPN/proxy configuration

URL:
$Uri
"@
}

# ============================================================
# Port helpers
# ============================================================

function Test-PortAvailable {
    param([int]$Port)

    $listener = $null

    try {
        $listener = New-Object System.Net.Sockets.TcpListener(
            [System.Net.IPAddress]::Loopback,
            $Port
        )
        $listener.Start()
        return $true
    }
    catch {
        return $false
    }
    finally {
        if ($listener) {
            try { $listener.Stop() } catch {}
        }
    }
}

function Find-FreePort {
    param(
        [int]$StartPort,
        [int]$EndPort
    )

    for ($port = $StartPort; $port -le $EndPort; $port++) {
        if (Test-PortAvailable $port) {
            return $port
        }
    }

    throw "No free localhost port was found between $StartPort and $EndPort."
}

# ============================================================
# Python helpers
# ============================================================

function Test-Python312 {
    param(
        [string]$Command,
        [string[]]$PrefixArgs = @()
    )

    if (-not (Test-Path -LiteralPath $Command)) {
        return $false
    }

    try {
        $output = & $Command @PrefixArgs `
            -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" `
            2>$null

        return (
            ($LASTEXITCODE -eq 0) -and
            (($output | Out-String).Trim() -match "^3\.12\.")
        )
    }
    catch {
        return $false
    }
}

function New-PythonInfo {
    param(
        [string]$Command,
        [string[]]$PrefixArgs,
        [bool]$Managed
    )

    return [PSCustomObject]@{
        Command = $Command
        PrefixArgs = $PrefixArgs
        Managed = $Managed
    }
}

function Find-Python312 {
    # Our own runtime first.
    $managedPython = Join-Path $PythonManagedRoot "python.exe"
    if (Test-Python312 $managedPython) {
        return New-PythonInfo $managedPython @() $true
    }

    # Python launcher.
    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) {
        if (Test-Python312 $py.Source @("-3.12")) {
            return New-PythonInfo $py.Source @("-3.12") $false
        }
    }

    # Registered Python.org installs.
    $registryPaths = @(
        "HKCU:\Software\Python\PythonCore\3.12\InstallPath",
        "HKLM:\Software\Python\PythonCore\3.12\InstallPath",
        "HKLM:\Software\WOW6432Node\Python\PythonCore\3.12\InstallPath"
    )

    foreach ($registryPath in $registryPaths) {
        try {
            $installPath = (Get-Item -Path $registryPath -ErrorAction Stop).GetValue("")
            if ($installPath) {
                $candidate = Join-Path $installPath "python.exe"
                if (Test-Python312 $candidate) {
                    return New-PythonInfo $candidate @() $false
                }
            }
        }
        catch {}
    }

    # PATH, rejecting the Microsoft Store alias.
    $pythonCommands = @(Get-Command python.exe -All -ErrorAction SilentlyContinue)
    foreach ($python in $pythonCommands) {
        if ($python.Source -like "*\WindowsApps\python.exe") {
            continue
        }
        if (Test-Python312 $python.Source) {
            return New-PythonInfo $python.Source @() $false
        }
    }

    # Common paths.
    $common = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:ProgramFiles\Python312\python.exe"
    )

    foreach ($candidate in $common) {
        if (Test-Python312 $candidate) {
            return New-PythonInfo $candidate @() $false
        }
    }

    return $null
}

function Install-PrivatePython {
    param([string]$Architecture)

    Write-Section "Installing private Python $PythonVersion"

    if ($Architecture -eq "arm64") {
        $fileName = "python-$PythonVersion-arm64.exe"
    }
    else {
        $fileName = "python-$PythonVersion-amd64.exe"
    }

    $installer = Join-Path $DownloadRoot $fileName
    $url = "https://www.python.org/ftp/python/$PythonVersion/$fileName"

    $havePayload = Copy-PayloadIfPresent $fileName $installer
    if (-not $havePayload) {
        Download-File $url $installer "Python $PythonVersion"
    }

    # Authenticode verification before execution.
    $signature = Get-AuthenticodeSignature -FilePath $installer

    if ($signature.Status -ne "Valid") {
        Remove-Item -LiteralPath $installer -Force -ErrorAction SilentlyContinue
        throw "Python installer signature validation failed. The installer was deleted and was not executed."
    }

    Ensure-Directory $PythonManagedRoot

    $arguments = @(
        "/quiet",
        "InstallAllUsers=0",
        "TargetDir=`"$PythonManagedRoot`"",
        "PrependPath=0",
        "AppendPath=0",
        "Include_launcher=0",
        "InstallLauncherAllUsers=0",
        "AssociateFiles=0",
        "Shortcuts=0",
        "Include_pip=1",
        "Include_test=0",
        "Include_doc=0",
        "Include_dev=1",
        "Include_exe=1",
        "Include_lib=1"
    ) -join " "

    $process = Start-Process `
        -FilePath $installer `
        -ArgumentList $arguments `
        -Wait `
        -PassThru

    if (($process.ExitCode -ne 0) -and ($process.ExitCode -ne 3010)) {
        throw "Python installer exited with code $($process.ExitCode)."
    }

    $python = Join-Path $PythonManagedRoot "python.exe"

    if (-not (Test-Python312 $python)) {
        throw "Python installation completed but the interpreter failed its health check."
    }

    return New-PythonInfo $python @() $true
}

function Test-ClassPython {
    $python = Join-Path $PythonVenvRoot "Scripts\python.exe"

    if (-not (Test-Python312 $python)) {
        return $false
    }

    try {
        & $python -m pip --version *> $null
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
}

function Create-ClassPython {
    param($PythonInfo)

    Write-Section "Preparing isolated Python environment"

    if (Test-Path -LiteralPath $PythonVenvRoot) {
        Remove-Robust $PythonVenvRoot
    }

    $venvArgs = @($PythonInfo.PrefixArgs) + @("-m", "venv", $PythonVenvRoot)
    & $PythonInfo.Command @venvArgs

    if ($LASTEXITCODE -ne 0) {
        throw "Python could not create the classroom virtual environment."
    }

    $python = Join-Path $PythonVenvRoot "Scripts\python.exe"

    & $python -m ensurepip --upgrade *> $null

    if (-not (Test-ClassPython)) {
        throw "The classroom Python environment was created but failed validation."
    }
}

function Test-WorkshopPackages {
    $python = Join-Path $PythonVenvRoot "Scripts\python.exe"

    if (-not (Test-Path -LiteralPath $python)) {
        return $false
    }

    $result = Invoke-NativeCapture `
        -FilePath $python `
        -Arguments @(
            "-c",
            "import pandas,sklearn,fastapi,uvicorn; import pandas as p; print('ok', p.__version__)"
        )

    return ($result.ExitCode -eq 0)
}

# A cold "import fastapi/uvicorn" is quick, but this check also proves
# the workshop scripts' pandas/scikit-learn stack is healthy. Once a
# classroom venv has proven healthy we remember that and re-answer
# instantly; a changed package list or recreated venv invalidates it.
function Test-WorkshopPackagesFast {
    $stateFile = Join-Path $StateRoot "workshop-packages-ok.json"

    $state = $null
    if (Test-Path -LiteralPath $stateFile) {
        try {
            $state = Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json
        }
        catch {
            $state = $null
        }
    }

    if ($state -and ($state.venv -eq $PythonVenvRoot) -and ($state.ok -eq $true) -and ($state.packages -eq $WorkshopPackageSignature)) {
        return $true
    }

    if (Test-WorkshopPackages) {
        try {
            [ordered]@{
                ok   = $true
                venv = $PythonVenvRoot
                packages = $WorkshopPackageSignature
                checkedAt = (Get-Date).ToString("o")
            } |
                ConvertTo-Json |
                Set-Content -LiteralPath $stateFile -Encoding UTF8
        }
        catch {}

        return $true
    }

    return $false
}

function Install-WorkshopDependencies {
    Write-Section "Preparing workshop Python packages"

    if (Test-WorkshopPackagesFast) {
        Write-OK "Workshop packages already present (pandas / scikit-learn / fastapi / uvicorn)"
        return
    }

    # Keep downloaded wheels between runs/hostel resets in the classroom
    # profile instead of the user's global pip cache.
    $env:PIP_CACHE_DIR = Join-Path $AppRoot "pip-cache"

    Write-Host ""
    Write-Host "First run only: installing pandas / scikit-learn / fastapi / uvicorn."
    Write-Host "Target (isolated classroom venv): $PythonVenvRoot" -ForegroundColor Cyan
    Write-Host "This can take a few minutes on classroom Wi-Fi (several hundred MB of wheels)." -ForegroundColor Yellow
    Write-Host "Progress appears below when each package is collected/downloaded, so the window is NOT hung:" -ForegroundColor Yellow
    Write-Host ""

    $python = Join-Path $PythonVenvRoot "Scripts\python.exe"

    $wheelRoot = Join-Path $PayloadRoot "wheels"
    $wheelArgs = @()

    # Optional offline shortcut: the instructor may pre-download all wheels
    # into deployment/payload/wheels (see README-FIRST.txt). Then no Wi-Fi
    # is needed at all.
    if ((Test-Path -LiteralPath $wheelRoot) -and
        ((Get-ChildItem -LiteralPath $wheelRoot -Filter "*.whl" -ErrorAction SilentlyContinue) )) {
        Write-Host "Bundled offline wheels found: $wheelRoot" -ForegroundColor DarkGray
        $wheelArgs = @("--no-index", "--find-links", ('"{0}"' -f $wheelRoot))
    }

    # Live progress, not a silent wait: pip runs as a background process
    # whose output lands in a temporary log, while this console keeps a
    # PowerShell progress bar updated every second (elapsed time, number
    # of wheels fetched, and the latest Collecting/Downloading action).
    $logOut = Join-Path $DownloadRoot "pip-install.log"
    $argList = @(
        "-m", "pip", "install",
        "--only-binary=:all:",
        "--disable-pip-version-check",
        "--progress-bar", "off"
    ) + $wheelArgs + @("pandas", "scikit-learn", "fastapi", "uvicorn")

    $started = Get-Date
    $pipProc = Start-Process `
        -FilePath $python `
        -ArgumentList $argList `
        -WorkingDirectory $AppRoot `
        -RedirectStandardOutput $logOut `
        -RedirectStandardError (Join-Path $DownloadRoot "pip-install.err.log") `
        -NoNewWindow `
        -PassThru

    $lastAction = "starting pip"
    $downloadCount = 0
    $installDone = $false

    while (-not $pipProc.HasExited) {
        Start-Sleep -Milliseconds 1200

        # Feed the heartbeat from whatever pip wrote since the last tick.
        try {
            $lines = Get-Content -LiteralPath $logOut -ErrorAction SilentlyContinue
            if ($lines) {
                $downloads = @($lines | Where-Object { $_ -match "Downloading " })
                $downloadCount = $downloads.Count
                $latest = ($lines | Where-Object { $_.Trim() }) | Select-Object -Last 1
                if ($latest) {
                    $lastAction = $latest.Trim()
                    if ($lastAction.Length -gt 58) { $lastAction = $lastAction.Substring(0, 58) + "..." }
                }
                if ($lines | Where-Object { $_ -match "Successfully installed" }) {
                    $installDone = $true
                }
            }
        }
        catch {}

        $span = (Get-Date) - $started
        $elapsed = "{0}m {1:00}s" -f [int][Math]::Floor($span.TotalMinutes), $span.Seconds
        Write-Progress `
            -Activity "Installing workshop packages (pandas / scikit-learn / fastapi / uvicorn)" `
            -Status "$elapsed elapsed | $downloadCount wheels fetched | $lastAction" `
            -PercentComplete ([Math]::Min(95, 10 + $downloadCount * 8))
    }

    Write-Progress -Activity "Installing workshop packages" -Completed

    try {
        $tail = Get-Content -LiteralPath $logOut -ErrorAction SilentlyContinue | Select-Object -Last 6
        if ($tail) {
            $tail | ForEach-Object {
                if ($_ -and $_.Trim()) { Write-Host ("  " + $_.Trim()) -ForegroundColor DarkGray }
            }
        }
    }
    catch {}

    $pipExitCode = $pipProc.ExitCode

    if ((Test-WorkshopPackages)) {
        try {
            [ordered]@{
                ok   = $true
                venv = $PythonVenvRoot
                packages = $WorkshopPackageSignature
                checkedAt = (Get-Date).ToString("o")
            } |
                ConvertTo-Json |
                Set-Content -LiteralPath (Join-Path $StateRoot "workshop-packages-ok.json") -Encoding UTF8
        }
        catch {}

        Write-Host ""
        Write-OK "Workshop packages installed"
    }
    else {
        # The classroom machines are expected to have internet access
        # (npm and PyPI must be reachable); if this install fails in a
        # blocked network, keep setup alive so the OpenCode console still
        # opens on the project root and the instructor is pointed at the
        # fix instead of a silent dead dashboard later.
        Write-Warn "pip exit code was $pipExitCode. Continuing, but scripts like 01_eda.py need pandas/scikit-learn."
    }
}

# ============================================================
# Node.js helpers
# ============================================================

function Test-PrivateNode {
    $node = Join-Path $NodeRoot "node.exe"
    $npm = Join-Path $NodeRoot "npm.cmd"

    if ((-not (Test-Path -LiteralPath $node)) -or
        (-not (Test-Path -LiteralPath $npm))) {
        return $false
    }

    try {
        $version = (& $node --version 2>$null | Out-String).Trim()
        & $npm --version *> $null

        return (
            ($LASTEXITCODE -eq 0) -and
            ($version -eq "v$NodeVersion")
        )
    }
    catch {
        return $false
    }
}

function Install-PrivateNode {
    param([string]$Architecture)

    Write-Section "Installing private Node.js $NodeVersion"

    $fileName = "node-v$NodeVersion-win-$Architecture.zip"
    $checksumName = "SHASUMS256.txt"
    $baseUrl = "https://nodejs.org/dist/v$NodeVersion"

    $zipFile = Join-Path $DownloadRoot $fileName
    $checksumFile = Join-Path $DownloadRoot "node-v$NodeVersion-SHASUMS256.txt"

    if (-not (Copy-PayloadIfPresent $fileName $zipFile)) {
        Download-File "$baseUrl/$fileName" $zipFile "Node.js $NodeVersion"
    }

    if (-not (Copy-PayloadIfPresent $checksumName $checksumFile)) {
        Download-File "$baseUrl/SHASUMS256.txt" $checksumFile "Node.js checksums"
    }

    $checksumLine = Get-Content -LiteralPath $checksumFile |
        Where-Object { $_ -match "\s+$([regex]::Escape($fileName))$" } |
        Select-Object -First 1

    if (-not $checksumLine) {
        throw "Node.js checksum file did not contain $fileName."
    }

    $expected = (($checksumLine -split "\s+")[0]).ToUpperInvariant()
    $actual = (Get-FileHash -LiteralPath $zipFile -Algorithm SHA256).Hash.ToUpperInvariant()

    if ($expected -ne $actual) {
        Remove-Item -LiteralPath $zipFile -Force -ErrorAction SilentlyContinue
        throw "Node.js SHA256 validation failed. The archive was deleted and was not extracted."
    }

    if (Test-Path -LiteralPath $NodeRoot) {
        Remove-Robust $NodeRoot
    }

    $stage = Join-Path $RuntimeRoot "node-stage-$PID"

    if (Test-Path -LiteralPath $stage) {
        Remove-Robust $stage
    }

    Ensure-Directory $stage

    try {
        Expand-Archive -LiteralPath $zipFile -DestinationPath $stage -Force

        $folderName = "node-v$NodeVersion-win-$Architecture"
        $extracted = Join-Path $stage $folderName

        if (-not (Test-Path -LiteralPath $extracted)) {
            throw "Node archive did not contain $folderName."
        }

        Move-Item -LiteralPath $extracted -Destination $NodeRoot
    }
    finally {
        if (Test-Path -LiteralPath $stage) {
            Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    if (-not (Test-PrivateNode)) {
        throw "Node.js extracted successfully but failed its health check."
    }
}

function Find-SystemNodeFallback {
    $node = Get-Command node.exe -ErrorAction SilentlyContinue
    $npm = Get-Command npm.cmd -ErrorAction SilentlyContinue

    if (-not $node -or -not $npm) {
        return $null
    }

    try {
        $version = (& $node.Source --version 2>$null | Out-String).Trim()

        if ($version -notmatch "^v(\d+)\.") {
            return $null
        }

        $major = [int]$Matches[1]
        & $npm.Source --version *> $null

        if (($LASTEXITCODE -eq 0) -and ($major -ge 20)) {
            return [PSCustomObject]@{
                Node = $node.Source
                Npm = $npm.Source
                Managed = $false
            }
        }
    }
    catch {}

    return $null
}

# ============================================================
# Native command helpers
# ============================================================
#
# Windows PowerShell 5.1 can convert native-program stderr into
# NativeCommandError / RemoteException records. Because this
# bootstrap normally uses ErrorActionPreference=Stop, a harmless
# native warning can otherwise terminate the whole installer.
#
# These helpers temporarily use Continue only around the native
# process, capture its output as text, and make the native exit
# code authoritative.
# ============================================================

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory=$true)]
        [string]$FilePath,

        [string[]]$Arguments = @(),

        [string]$WorkingDirectory
    )

    $previousPreference = $ErrorActionPreference

    try {
        $ErrorActionPreference = "Continue"

        $items = @(
            if ($WorkingDirectory) {
                Push-Location -LiteralPath $WorkingDirectory
            }

            try {
                & $FilePath @Arguments 2>&1
            }
            finally {
                if ($WorkingDirectory) {
                    Pop-Location
                }
            }
        )

        $exitCode = $LASTEXITCODE

        $lines = foreach ($item in $items) {
            if ($null -eq $item) {
                continue
            }

            if ($item -is [System.Management.Automation.ErrorRecord]) {
                if ($item.Exception -and $item.Exception.Message) {
                    $item.Exception.Message
                }
                else {
                    $item.ToString()
                }
            }
            else {
                $item.ToString()
            }
        }

        return [PSCustomObject]@{
            ExitCode = [int]$exitCode
            Output = ($lines -join [Environment]::NewLine)
        }
    }
    catch {
        return [PSCustomObject]@{
            ExitCode = -1
            Output = $_.Exception.Message
        }
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
}

function Invoke-NativeQuiet {
    param(
        [Parameter(Mandatory=$true)]
        [string]$FilePath,

        [string[]]$Arguments = @()
    )

    return Invoke-NativeCapture `
        -FilePath $FilePath `
        -Arguments $Arguments
}

# ============================================================
# npm install-script policy helper
# ============================================================

function Get-NpmMajorVersion {
    param([string]$Npm)

    $result = Invoke-NativeCapture `
        -FilePath $Npm `
        -Arguments @("--version")

    if (($result.ExitCode -eq 0) -and
        ($result.Output.Trim() -match "^(\d+)\.")) {
        return [int]$Matches[1]
    }

    return $null
}

function Install-GlobalNpmPackage {
    param(
        [string]$Npm,
        [string]$Prefix,
        [string]$Package,
        [string]$Registry = ""
    )

    $npmMajor = Get-NpmMajorVersion $Npm

    $arguments = @(
        "install",
        "--global",
        "--prefix", $Prefix,
        $Package,
        "--no-audit",
        "--no-fund",
        "--loglevel=warn"
    )

    # npm 11+ requires explicit approval for global package
    # lifecycle scripts. OpenCode's official npm package relies on
    # its postinstall script to select/install the native binary.
    if (($null -ne $npmMajor) -and ($npmMajor -ge 11)) {
        $arguments += "--allow-scripts=@opencode/cli"
    }
    else {
        # Older npm versions do not implement the allow-scripts
        # policy. Explicitly make sure lifecycle scripts are enabled.
        $arguments += "--ignore-scripts=false"
    }

    if (-not [string]::IsNullOrWhiteSpace($Registry)) {
        $arguments += @("--registry", $Registry)
    }

    $result = Invoke-NativeCapture `
        -FilePath $Npm `
        -Arguments $arguments

    if (-not [string]::IsNullOrWhiteSpace($result.Output)) {
        Write-Host $result.Output
    }

    return [int]$result.ExitCode
}

# ============================================================
# OpenCode helpers
# ============================================================

function Get-OpenCodeVersion {
    param([string]$Command)

    if (-not (Test-Path -LiteralPath $Command)) {
        return $null
    }

    $result = Invoke-NativeCapture `
        -FilePath $Command `
        -Arguments @("--version")

    if ($result.ExitCode -ne 0) {
        return $null
    }

    $output = $result.Output.Trim()

    if ($output -match '(?i)\bv?(2\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)\b') {
        return [PSCustomObject]@{
            Version = $Matches[1]
            Raw = $output
        }
    }

    return [PSCustomObject]@{
        Version = $null
        Raw = $output
    }
}

function Test-OpenCode {
    param([string]$Command)

    $versionInfo = Get-OpenCodeVersion $Command

    if (-not $versionInfo) {
        return $false
    }

    if ([string]::IsNullOrWhiteSpace($versionInfo.Version)) {
        return $false
    }

    if (-not $versionInfo.Version.StartsWith("2.")) {
        return $false
    }

    $help = Invoke-NativeCapture `
        -FilePath $Command `
        -Arguments @("service", "--help")

    return ($help.ExitCode -eq 0)
}

function Get-OpenCodeCandidates {
    # npm normally creates a global .cmd shim directly under the
    # chosen prefix. Also check the package's native binary because
    # it is a useful fallback on Windows if shim creation behaves
    # differently across npm versions.
    return @(
        (Join-Path $OpenCodePrefix "opencode.cmd"),
        (Join-Path $OpenCodePrefix "opencode.exe"),
        (Join-Path $OpenCodePrefix "node_modules\@opencode\cli\bin\opencode.exe"),
        (Join-Path $OpenCodePrefix "node_modules\@opencode\cli\bin\opencode")
    )
}

function Find-OpenCode {
    foreach ($candidate in (Get-OpenCodeCandidates)) {
        if (Test-OpenCode $candidate) {
            return $candidate
        }
    }

    return $null
}

function Write-OpenCodeDiagnostics {
    Write-Host "OpenCode candidate diagnostics:" -ForegroundColor DarkGray

    foreach ($candidate in (Get-OpenCodeCandidates)) {
        if (-not (Test-Path -LiteralPath $candidate)) {
            Write-Host "  MISSING  $candidate" -ForegroundColor DarkGray
            continue
        }

        $info = Get-OpenCodeVersion $candidate

        if ($info) {
            Write-Host "  FOUND    $candidate" -ForegroundColor DarkGray
            Write-Host "           version output: $($info.Raw)" -ForegroundColor DarkGray
        }
        else {
            Write-Host "  FOUND    $candidate" -ForegroundColor DarkGray
            Write-Host "           version command failed" -ForegroundColor DarkGray
        }
    }
}

function Install-OpenCode {
    param([string]$Npm)

    Write-Section "Installing private OpenCode V2"

    if (Test-Path -LiteralPath $OpenCodePrefix) {
        Remove-Robust $OpenCodePrefix
    }

    Ensure-Directory $OpenCodePrefix
    Ensure-Directory $NpmCache

    $env:NPM_CONFIG_CACHE = $NpmCache
    $env:NPM_CONFIG_FUND = "false"
    $env:NPM_CONFIG_AUDIT = "false"
    $env:NPM_CONFIG_UPDATE_NOTIFIER = "false"

    for ($attempt = 1; $attempt -le 2; $attempt++) {
        Write-Host "Installing OpenCode (attempt $attempt/2)..." -ForegroundColor DarkGray

        $result = Install-GlobalNpmPackage `
            -Npm $Npm `
            -Prefix $OpenCodePrefix `
            -Package $OpenCodePackage
        $openCode = Find-OpenCode

        if (($result -eq 0) -and $openCode) {
            $versionInfo = Get-OpenCodeVersion $openCode
            Write-OK "OpenCode install validated: $($versionInfo.Raw)"
            return $openCode
        }

        Write-Warn "OpenCode installation did not validate (npm exit code: $result)."
        Write-OpenCodeDiagnostics

        [void](Invoke-NativeQuiet -FilePath $Npm -Arguments @("cache", "verify"))
        Start-Sleep -Seconds 2
    }

    # A stale custom npm registry is common on managed/student
    # machines. Only bypass it after the normal route fails.
    Write-Warn "Retrying OpenCode against the public npm registry."

    $result = Install-GlobalNpmPackage `
        -Npm $Npm `
        -Prefix $OpenCodePrefix `
        -Package $OpenCodePackage `
        -Registry "https://registry.npmjs.org/"

    $openCode = Find-OpenCode

    if (($result -eq 0) -and $openCode) {
        $versionInfo = Get-OpenCodeVersion $openCode
        Write-OK "OpenCode install validated: $($versionInfo.Raw)"
        return $openCode
    }

    Write-Warn "Final OpenCode validation failed (npm exit code: $result)."
    Write-OpenCodeDiagnostics

    throw "OpenCode installation failed. See the candidate diagnostics above and the support log."
}

# ============================================================
# OpenCode profile / Tencent configuration
# ============================================================

function Configure-OpenCodeProfile {
    $data = Join-Path $OpenCodeProfile "data"
    $config = Join-Path $OpenCodeProfile "config"
    $cache = Join-Path $OpenCodeProfile "cache"
    $state = Join-Path $OpenCodeProfile "state"
    $temp = Join-Path $OpenCodeProfile "tmp"

    foreach ($path in @($data, $config, $cache, $state, $temp)) {
        Ensure-Directory $path
    }

    $env:XDG_DATA_HOME = $data
    $env:XDG_CONFIG_HOME = $config
    $env:XDG_CACHE_HOME = $cache
    $env:XDG_STATE_HOME = $state
    $env:TMPDIR = $temp
    $env:OPENCODE_DISABLE_AUTOUPDATE = "1"

    return [PSCustomObject]@{
        Data = $data
        Config = $config
        Cache = $cache
        State = $state
        Temp = $temp
    }
}

function Install-TencentCredential {
    if (-not (Test-Path -LiteralPath $DeploymentKeyFile)) {
        throw @"
Tencent API credential is missing.

Expected:
$DeploymentKeyFile

Make sure key.txt is in the same folder as:
- START VIBE CODING.bat
- oneclick.ps1
"@
    }

    $apiKey = (Get-Content -LiteralPath $DeploymentKeyFile -Raw).Trim()

    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        throw "key.txt is empty."
    }

    if ($apiKey -eq "PASTE_TENCENT_KEY_HERE") {
        throw "key.txt still contains the placeholder. Replace it with the Tencent API key before distribution."
    }

    if (($apiKey.Length -lt 20) -or (-not $apiKey.StartsWith("sk-"))) {
        throw "key.txt does not look like the expected Tencent API key format."
    }

    Ensure-Directory $SecretRoot

    # No trailing newline and no BOM.
    [System.IO.File]::WriteAllText(
        $TencentKeyFile,
        $apiKey,
        (New-Object System.Text.UTF8Encoding($false))
    )

    # The credential is deliberately stored inside the current
    # student's user profile. We do not rewrite the file ACL here:
    # constructing a replacement ACL with Set-Acl can request
    # SeSecurityPrivilege on some non-admin Windows installations.
    # The student's normal user-profile ACL remains in force.

    return $apiKey
}

function Get-KeyFingerprint {
    param([string]$Key)

    $sha = [System.Security.Cryptography.SHA256]::Create()

    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Key)
        $hash = $sha.ComputeHash($bytes)
        return ([BitConverter]::ToString($hash) -replace "-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function New-OpenCodeClassroomConfig {
    # OpenCode 2.0.20 schema, pinned to the exact CLI version.
    #
    # IMPORTANT:
    # v2.0.20's tagged documentation uses:
    #   provider            (singular)
    #   provider.<id>.npm
    #   provider.<id>.options.baseURL
    #   provider.<id>.options.apiKey
    #   provider.<id>.models
    #
    # enabled_providers makes Tencent the only provider the
    # runtime is allowed to load.
    $config = [ordered]@{
        '$schema' = "https://opencode.ai/config.json"

        model = $TencentModelRef

        enabled_providers = @(
            $TencentProviderId
        )

        provider = [ordered]@{
            tencent = [ordered]@{
                name = "Tencent Cloud MaaS"

                npm = "@ai-sdk/openai-compatible"

                options = [ordered]@{
                    baseURL = $TencentBaseUrl
                    apiKey = "{env:TENCENT_API_KEY}"
                    timeout = 600000
                    chunkTimeout = 120000
                }

                models = [ordered]@{
                    "glm-5.3-flash" = [ordered]@{
                        name = "GLM 5.3 Flash"

                        limit = [ordered]@{
                            context = 1000000
                            output = 128000
                        }
                    }
                }
            }
        }
    }

    return ($config | ConvertTo-Json -Depth 20 -Compress)
}

function Get-OpenCodeConfigPath {
    param([string]$OpenCode)

    $result = Invoke-NativeCapture `
        -FilePath $OpenCode `
        -Arguments @("debug", "paths", "config")

    if ($result.ExitCode -ne 0) {
        return $null
    }

    $path = $result.Output.Trim()

    if (-not [string]::IsNullOrWhiteSpace($path)) {
        return $path
    }

    return $null
}

function Test-PathUnderRoot {
    param(
        [string]$Path,
        [string]$Root
    )

    try {
        $fullPath = [IO.Path]::GetFullPath($Path).TrimEnd("\")
        $fullRoot = [IO.Path]::GetFullPath($Root).TrimEnd("\")

        return $fullPath.StartsWith(
            $fullRoot + "\",
            [System.StringComparison]::OrdinalIgnoreCase
        ) -or $fullPath.Equals(
            $fullRoot,
            [System.StringComparison]::OrdinalIgnoreCase
        )
    }
    catch {
        return $false
    }
}

function Resolve-ClassroomOpenCodeConfigDirectory {
    param(
        [string]$OpenCode,
        $Profile
    )

    # First try XDG_CONFIG_HOME, which should resolve the global
    # OpenCode config underneath our isolated profile.
    $env:XDG_CONFIG_HOME = $Profile.Config
    Remove-Item Env:OPENCODE_CONFIG -ErrorAction SilentlyContinue
    Remove-Item Env:OPENCODE_CONFIG_DIR -ErrorAction SilentlyContinue

    $path = Get-OpenCodeConfigPath $OpenCode

    if ($path -and (Test-PathUnderRoot $path $OpenCodeProfile)) {
        return $path
    }

    # V2 beta builds have had inconsistent CONFIG_DIR semantics.
    # In builds where it replaces the global config root, that
    # behavior is useful for our isolated classroom profile.
    $fallback = Join-Path $Profile.Config "opencode"
    Ensure-Directory $fallback
    $env:OPENCODE_CONFIG_DIR = $fallback

    $path = Get-OpenCodeConfigPath $OpenCode

    if ($path -and (Test-PathUnderRoot $path $OpenCodeProfile)) {
        Write-Warn "Using OpenCode V2 CONFIG_DIR compatibility fallback."
        return $path
    }

    throw @"
OpenCode did not resolve its config directory inside the isolated classroom profile.

Expected it under:
$OpenCodeProfile

Resolved:
$path

Setup stopped rather than modifying the student's normal OpenCode configuration.
"@
}

function Install-ClassroomOpenCodeConfig {
    param(
        [string]$ConfigDirectory,
        [string]$ConfigJson
    )

    Ensure-Directory $ConfigDirectory

    $configFile = Join-Path $ConfigDirectory "opencode.json"

    [System.IO.File]::WriteAllText(
        $configFile,
        ($ConfigJson | ConvertFrom-Json | ConvertTo-Json -Depth 20),
        (New-Object System.Text.UTF8Encoding($false))
    )

    return $configFile
}

function Test-OpenCodeProvider {
    param(
        [string]$OpenCode,
        [string]$Fingerprint,
        [string]$OpenCodeVersion
    )

    if ((-not $Repair) -and (Test-Path -LiteralPath $OpenCodeProviderTestStateFile)) {
        try {
            $state = Get-Content -LiteralPath $OpenCodeProviderTestStateFile -Raw | ConvertFrom-Json

            if (($state.fingerprint -eq $Fingerprint) -and
                ($state.model -eq $TencentModelRef) -and
                ($state.opencodeVersion -eq $OpenCodeVersion) -and
                ($state.success -eq $true)) {
                Write-OK "OpenCode-to-Tencent provider was previously validated"
                return
            }
        }
        catch {}
    }

    Write-Host "Testing OpenCode -> Tencent provider routing..." -ForegroundColor DarkGray

    # This validates the actual OpenCode provider adapter rather
    # than only Tencent's raw HTTP endpoint. Capture output so it
    # does not clutter the classroom setup console.
    $result = Invoke-NativeCapture `
        -FilePath $OpenCode `
        -Arguments @(
            "run",
            "--model",
            $TencentModelRef,
            "Reply with exactly OK."
        ) `
        -WorkingDirectory $ClassroomProjectRoot

    if ($result.ExitCode -ne 0) {
        throw @"
OpenCode could not complete a direct request through the Tencent classroom model.

Exit code:
$($result.ExitCode)

OpenCode output:
$($result.Output)
"@
    }

    $state = [ordered]@{
        success = $true
        testedAt = (Get-Date).ToString("o")
        fingerprint = $Fingerprint
        model = $TencentModelRef
        opencodeVersion = $OpenCodeVersion
    }

    $state |
        ConvertTo-Json |
        Set-Content -LiteralPath $OpenCodeProviderTestStateFile -Encoding UTF8

    Write-OK "OpenCode -> Tencent provider request succeeded"
}

function Test-TencentAPI {
    param(
        [string]$ApiKey,
        [string]$Fingerprint
    )

    if ($SkipTencentTest) {
        Write-Warn "Tencent API smoke test skipped by command-line option."
        return
    }

    if ((-not $Repair) -and (Test-Path -LiteralPath $TencentTestStateFile)) {
        try {
            $state = Get-Content -LiteralPath $TencentTestStateFile -Raw | ConvertFrom-Json

            if (($state.fingerprint -eq $Fingerprint) -and
                ($state.endpoint -eq $TencentBaseUrl) -and
                ($state.model -eq $TencentModelId) -and
                ($state.success -eq $true)) {
                Write-OK "Tencent API credential was previously validated"
                return
            }
        }
        catch {}
    }

    Write-Host "Testing Tencent GLM 5.3 Flash connectivity..." -ForegroundColor DarkGray

    $headers = @{
        Authorization = "Bearer $ApiKey"
        "Content-Type" = "application/json"
    }

    # Deliberately use only fields shown in the supplied Tencent
    # Chat Completions example, minimizing compatibility assumptions.
    $body = @{
        model = $TencentModelId
        messages = @(
            @{
                role = "user"
                content = "Reply with exactly OK."
            }
        )
        stream = $false
    } | ConvertTo-Json -Depth 10 -Compress

    try {
        $response = Invoke-RestMethod `
            -Method Post `
            -Uri $TencentCompletionUrl `
            -Headers $headers `
            -Body $body `
            -TimeoutSec 90 `
            -ErrorAction Stop

        if (-not $response) {
            throw "Tencent returned an empty response."
        }

        $state = [ordered]@{
            success = $true
            testedAt = (Get-Date).ToString("o")
            fingerprint = $Fingerprint
            endpoint = $TencentBaseUrl
            model = $TencentModelId
        }

        $state |
            ConvertTo-Json |
            Set-Content -LiteralPath $TencentTestStateFile -Encoding UTF8

        Write-OK "Tencent GLM 5.3 Flash API reachable"
    }
    catch {
        throw @"
Tencent GLM 5.3 Flash API test failed.

$($_.Exception.Message)

Possible causes:
- Invalid/expired key
- Tencent credits or entitlement issue
- Campus firewall/proxy
- Captive portal
- Tencent endpoint unavailable

The API key itself has not been written to the support log.
"@
    }
}

# ============================================================
# Web UI credentials
# ============================================================

function New-RandomPassword {
    $alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    $bytes = New-Object byte[] 24
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()

    try {
        $rng.GetBytes($bytes)
    }
    finally {
        $rng.Dispose()
    }

    $characters = foreach ($byte in $bytes) {
        $alphabet[$byte % $alphabet.Length]
    }

    return (-join $characters)
}

function Get-WebCredentials {
    if (Test-Path -LiteralPath $CredentialsFile) {
        try {
            $credentials = Get-Content -LiteralPath $CredentialsFile -Raw | ConvertFrom-Json

            if ($credentials.username -and $credentials.password) {
                return $credentials
            }
        }
        catch {}
    }

    $credentials = [PSCustomObject]@{
        username = $OpenCodeUsername
        password = (New-RandomPassword)
    }

    $credentials |
        ConvertTo-Json |
        Set-Content -LiteralPath $CredentialsFile -Encoding UTF8

    return $credentials
}

# ============================================================
# Browser helper
# ============================================================

function Open-Browser {
    param([string]$Url)

    try {
        Start-Process $Url -ErrorAction Stop
        return $true
    }
    catch {
        try {
            $rundll = Join-Path $env:SystemRoot "System32\rundll32.exe"
            & $rundll "url.dll,FileProtocolHandler" $Url
            return $true
        }
        catch {
            return $false
        }
    }
}

# ============================================================
# OpenCode service
# ============================================================

function Set-ServiceEnv {
    param(
        [string]$OpenCode,
        [string]$Name,
        [string]$Value
    )

    $result = Invoke-NativeCapture `
        -FilePath $OpenCode `
        -Arguments @(
            "service",
            "set",
            "env",
            $Name,
            $Value
        )

    if ($result.ExitCode -ne 0) {
        throw @"
Could not set OpenCode service environment variable: $Name

OpenCode output:
$($result.Output)
"@
    }
}

# The OpenCode Web UI service is started so its working directory is the
# workshop project root; the isolated profile environment keeps the
# provider/config isolation intact.
function Start-ClassOpenCodeService {
    param(
        [string]$OpenCode,
        [string]$ArgumentsKind = "start"
    )

    return Invoke-NativeCapture `
        -FilePath $OpenCode `
        -Arguments @("service", $ArgumentsKind) `
        -WorkingDirectory $ClassroomProjectRoot
}

# The workshop browser page (workshop_server.py + the React UI in web/dist)
# is a SECOND classroom service on its own port (default 4097). Serving it
# here means students get everything automatically:
#     OpenCode chat  : http://127.0.0.1:4096
#     Workshop page  : http://127.0.0.1:<workshop port>
# serve_workshop.py starts the server in the background, waits until the
# page really answers and returns; the server then auto-refreshes the open
# page whenever the AI assistant saves a gate.
function Start-WorkshopPage {
    param(
        [string]$Python,
        [string]$ProjectRoot,
        [int]$Port
    )

    $serve = Join-Path $ProjectRoot "serve_workshop.py"
    $server = Join-Path $ProjectRoot "workshop_server.py"

    if ((-not (Test-Path -LiteralPath $serve)) -or (-not (Test-Path -LiteralPath $server))) {
        Write-Warn "serve_workshop.py / workshop_server.py were not found in: $ProjectRoot"
        Write-Host "Servers to run manually:  python serve_workshop.py" -ForegroundColor Yellow
        return $null
    }

    Write-Host "Starting the workshop page on port $Port..." -ForegroundColor DarkGray

    Push-Location -LiteralPath $ProjectRoot
    try {
        & $Python $serve --port $Port --no-browser
        $serveExit = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    if ($serveExit -ne 0) {
        Write-Warn "serve_workshop.py exited with code $serveExit."
        Write-Host "Start it manually once:  python serve_workshop.py  (leave that terminal open)" -ForegroundColor Yellow
        return $null
    }

    # serve_workshop.py already waited for readiness; double-check quickly.
    for ($attempt = 0; $attempt -lt 10; $attempt++) {
        try {
            $pageResponse = Invoke-WebRequest `
                -Uri ("http://127.0.0.1:{0}/api/health" -f $Port) `
                -UseBasicParsing `
                -TimeoutSec 5
            if ($pageResponse.StatusCode -ge 200 -and $pageResponse.StatusCode -lt 500) {
                Write-OK "Workshop page ready at http://127.0.0.1:$Port"
                return [PSCustomObject]@{ Port = $Port; Ok = $true }
            }
        }
        catch {}
        Start-Sleep -Seconds 1
    }

    Write-Warn "Workshop page did not answer on port $Port."
    Write-Host "Start it manually once:  python serve_workshop.py  (leave that terminal open)" -ForegroundColor Yellow
    return $null
}


# A tiny detached watchdog: keeps polling the classroom web pages every 10
# seconds for up to 8 hours, and cleanly restarts the classroom services if
# they stop answering (e.g. students report "the page loads and loads" after
# the launcher window closes). Restart writes a line into the watchdog log.
function Start-ClassWatchdog {
    param(
        [string]$OpenCode,
        [int]$Port,
        [string]$WatchdogLog,
        [string]$Python,
        [int]$PagePort,
        [string]$ProjectRoot
    )

    $watchdogScript = Join-Path $AppRoot "watchdog.ps1"

    $watchdogBody = @'
param(
    [string]$OpenCode,
    [int]$Port,
    [string]$Log,
    [string]$ProjectRoot,
    [string]$Python,
    [int]$PagePort
)

$ErrorActionPreference = "Continue"
$deadline = (Get-Date).AddHours(8)
$failures = 0
$pageFailures = 0
$baseUrl = "http://127.0.0.1:{0}" -f $Port
$pageUrl = "http://127.0.0.1:{0}" -f $PagePort

while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 10

    # --- workshop page (OpenCode) ---
    $alive = $false
    try {
        $response = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing -TimeoutSec 8
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
            $alive = $true
        }
    }
    catch {}

    if ($alive) {
        $failures = 0
    }
    else {
        $failures = $failures + 1
        if ($failures -ge 3) {
            Push-Location -LiteralPath $ProjectRoot
            try {
                $null = & $OpenCode service restart 2>&1
                $failures = 0
                Add-Content -LiteralPath $Log -Value ((Get-Date -Format o) + " watchdog restarted the classroom service (page was not answering).")
            }
            catch {
                Add-Content -LiteralPath $Log -Value ((Get-Date -Format o) + " watchdog failed to restart: " + $_.Exception.Message)
            }
            finally {
                Pop-Location
            }
        }
    }

    # --- workshop page (workshop_server.py + React UI) ---
    $pageAlive = $false
    try {
        $pageResponse = Invoke-WebRequest -Uri $pageUrl -UseBasicParsing -TimeoutSec 8
        if ($pageResponse.StatusCode -ge 200 -and $pageResponse.StatusCode -lt 500) {
            $pageAlive = $true
        }
    }
    catch {}

    if ($pageAlive) {
        $pageFailures = 0
    }
    else {
        $pageFailures = $pageFailures + 1
        if ($pageFailures -ge 3) {
            try {
                $serve = Join-Path $ProjectRoot "serve_workshop.py"
                $null = Start-Process -FilePath $Python -ArgumentList @(('"{0}"' -f $serve), "--port", "$PagePort", "--no-browser") -WorkingDirectory $ProjectRoot -WindowStyle Minimized
                $pageFailures = 0
                Add-Content -LiteralPath $Log -Value ((Get-Date -Format o) + " watchdog restarted the workshop page (workshop server) on port " + $PagePort + ".")
            }
            catch {
                Add-Content -LiteralPath $Log -Value ((Get-Date -Format o) + " watchdog failed to restart the workshop page: " + $_.Exception.Message)
            }
        }
    }
}
'@

    Set-Content -LiteralPath $watchdogScript -Value $watchdogBody -Encoding UTF8

    Start-Process `
        -FilePath "powershell.exe" `
        -WindowStyle Hidden `
        -ArgumentList @(
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", ('"{0}"' -f $watchdogScript),
            "-OpenCode", ('"{0}"' -f $OpenCode),
            "-Port", "$Port",
            "-Log", ('"{0}"' -f $WatchdogLog),
            "-ProjectRoot", ('"{0}"' -f $ClassroomProjectRoot),
            "-Python", ('"{0}"' -f $Python),
            "-PagePort", "$WorkshopPagePort"
        )
}

function Start-OpenCodeService {
    param(
        [string]$OpenCode,
        [int]$Port,
        $Credentials,
        [string]$ManagedPath,
        $Profile,
        [string]$TencentApiKey,
        [string]$InlineConfig
    )

    Write-Section "Starting OpenCode Web UI"

    [void](Invoke-NativeQuiet `
        -FilePath $OpenCode `
        -Arguments @("service", "stop"))

    [void](Invoke-NativeQuiet `
        -FilePath $OpenCode `
        -Arguments @("service", "unset", "disabled"))

    $result = Invoke-NativeCapture `
        -FilePath $OpenCode `
        -Arguments @("service", "set", "hostname", "127.0.0.1")
    if ($result.ExitCode -ne 0) {
        throw "Could not configure OpenCode hostname. $($result.Output)"
    }

    $result = Invoke-NativeCapture `
        -FilePath $OpenCode `
        -Arguments @("service", "set", "port", "$Port")
    if ($result.ExitCode -ne 0) {
        throw "Could not configure OpenCode port. $($result.Output)"
    }

    $result = Invoke-NativeCapture `
        -FilePath $OpenCode `
        -Arguments @("service", "set", "password", $Credentials.password)
    if ($result.ExitCode -ne 0) {
        throw "Could not configure OpenCode Web UI password. $($result.Output)"
    }

    # Explicitly pass the isolated profile and classroom runtime
    # to the background process. Do not rely on
    # OPENCODE_CONFIG_CONTENT: V2 beta builds have had provider
    # resolution regressions with inline configuration.
    Set-ServiceEnv $OpenCode "PATH" $ManagedPath
    Set-ServiceEnv $OpenCode "XDG_DATA_HOME" $Profile.Data
    Set-ServiceEnv $OpenCode "XDG_CONFIG_HOME" $Profile.Config
    Set-ServiceEnv $OpenCode "XDG_CACHE_HOME" $Profile.Cache
    Set-ServiceEnv $OpenCode "XDG_STATE_HOME" $Profile.State
    Set-ServiceEnv $OpenCode "TMPDIR" $Profile.Temp
    Set-ServiceEnv $OpenCode "OPENCODE_DISABLE_AUTOUPDATE" "1"
    Set-ServiceEnv $OpenCode "OPENCODE_CONFIG_CONTENT" $InlineConfig

    if (-not [string]::IsNullOrWhiteSpace($env:OPENCODE_CONFIG_DIR)) {
        Set-ServiceEnv $OpenCode "OPENCODE_CONFIG_DIR" $env:OPENCODE_CONFIG_DIR
    }

    Set-ServiceEnv $OpenCode "TENCENT_API_KEY" $TencentApiKey
    Set-ServiceEnv $OpenCode "NO_PROXY" $env:NO_PROXY
    Set-ServiceEnv $OpenCode "no_proxy" $env:NO_PROXY
    Set-ServiceEnv $OpenCode "PYTHONUTF8" "1"
    Set-ServiceEnv $OpenCode "PIP_DISABLE_PIP_VERSION_CHECK" "1"
    Set-ServiceEnv $OpenCode "NPM_CONFIG_PREFIX" $NpmGlobal
    Set-ServiceEnv $OpenCode "NPM_CONFIG_CACHE" $NpmCache

    $startResult = Start-ClassOpenCodeService $OpenCode "start"

    if ($startResult.ExitCode -ne 0) {
        Write-Warn "OpenCode service start failed. Trying one restart."

        $startResult = Start-ClassOpenCodeService $OpenCode "restart"
    }

    if ($startResult.ExitCode -ne 0) {
        throw @"
OpenCode service could not start.

OpenCode output:
$($startResult.Output)
"@
    }

    # API health check: process existence/listening port alone is
    # not enough. Confirm the OpenCode API actually answers.
    $healthy = $false

    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        try {
            $healthResult = Invoke-NativeCapture `
                -FilePath $OpenCode `
                -Arguments @("api", "GET", "/api/session")

            if ($healthResult.ExitCode -eq 0) {
                $healthy = $true
                break
            }
        }
        catch {}

        Start-Sleep -Milliseconds 500
    }

    if (-not $healthy) {
        Write-Warn "OpenCode API health check failed. Trying one clean restart."

        [void](Invoke-NativeQuiet `
            -FilePath $OpenCode `
            -Arguments @("service", "stop"))

        Start-Sleep -Seconds 1

        $startResult = Start-ClassOpenCodeService $OpenCode "start"

        if ($startResult.ExitCode -ne 0) {
            Write-Warn "OpenCode service restart failed."
        }

        for ($attempt = 0; $attempt -lt 30; $attempt++) {
            try {
                $healthResult = Invoke-NativeCapture `
                    -FilePath $OpenCode `
                    -Arguments @("api", "GET", "/api/session")

                if ($healthResult.ExitCode -eq 0) {
                    $healthy = $true
                    break
                }
            }
            catch {}

            Start-Sleep -Milliseconds 500
        }
    }

    if (-not $healthy) {
        try {
            Write-Host "OpenCode service status:" -ForegroundColor DarkGray
            $statusResult = Invoke-NativeCapture `
                -FilePath $OpenCode `
                -Arguments @("service", "status")

            Write-Host $statusResult.Output
        }
        catch {}

        throw "OpenCode service failed its API health check."
    }

    $baseUrl = "http://127.0.0.1:$Port"
    $pairOutput = ""

    # FAST PATH: if the browser session already exists (auth persisted on
    # this machine from a previous run), reuse it and open the plain URL.
    # Pairing on every launch produced a hanging /auth/connect page: a
    # one-time token that is already consumed just spins in the browser.
    $alreadyAuthed = $false

    try {
        $authHeader = "Basic " + [Convert]::ToBase64String(
            [Text.Encoding]::ASCII.GetBytes("$($Credentials.username):$($Credentials.password)")
        )
        $authResponse = Invoke-WebRequest `
            -Uri "$baseUrl/api/session" `
            -UseBasicParsing `
            -Headers @{ Authorization = $authHeader } `
            -TimeoutSec 8

        if ($authResponse.StatusCode -eq 200) {
            $alreadyAuthed = $true
        }
    }
    catch {}

    if ($alreadyAuthed) {
        Write-OK "Existing classroom web session recognized -- opening the workshop page directly."
        $loginUrl = $baseUrl

        if (-not (Open-Browser $loginUrl)) {
            Write-Warn "Could not launch the default browser."
            Write-Host "Open manually: $loginUrl"
        }

        return [PSCustomObject]@{
            Url = $baseUrl
            Port = $Port
            Paired = $false
            PageOk = $true
        }
    }

    $pairOutput = ""

    try {
        $pairResult = Invoke-NativeCapture `
            -FilePath $OpenCode `
            -Arguments @("pair", "--url", $baseUrl)

        $pairOutput = $pairResult.Output
    }
    catch {}

    # Strip ANSI escape sequences before parsing.
    $plainOutput = [regex]::Replace(
        $pairOutput,
        "\x1B\[[0-9;?]*[ -/]*[@-~]",
        ""
    )

    $loginUrl = $null
    $urls = [regex]::Matches($plainOutput, "https?://[^\s]+")

    foreach ($match in $urls) {
        $candidate = $match.Value.Trim().TrimEnd(")", "]", "}", ",", ";")

        if (($candidate -like "$baseUrl*") -and
            ($candidate -like "*/auth/connect/*")) {
            $loginUrl = $candidate
            break
        }
    }

    if (-not $loginUrl) {
        Write-Warn "Automatic one-time pair-link parsing failed. Opening the Web UI normally."
        $loginUrl = $baseUrl
    }

    if (-not (Open-Browser $loginUrl)) {
        Write-Warn "Could not launch the default browser."
        Write-Host "Open manually: $loginUrl"
    }

    # Browser-side smoke test: the API health check above proves the
    # backend answers, but a student seeing an endlessly spinning page is
    # the same kind of outage. Ask the local HTTP server directly.
    $pageOk = $false
    try {
        $pageResponse = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing -TimeoutSec 10
        if ($pageResponse.StatusCode -ge 200 -and $pageResponse.StatusCode -lt 500) {
            $pageOk = $true
        }
    }
    catch {}

    if ($pageOk) {
        Write-OK "Workshop web page answers at $baseUrl"
    }
    else {
        Write-Warn "The workshop web page did not answer an HTTP request."
        Write-Host "A hidden watchdog will keep retrying and restart the service if needed." -ForegroundColor Yellow
    }

    return [PSCustomObject]@{
        Url = $baseUrl
        Port = $Port
        Paired = ($loginUrl -ne $baseUrl)
        PageOk = $pageOk
    }
}

# ============================================================
# MAIN
# ============================================================

try {
    # Prevent concurrent double-clicks.
    $Mutex = New-Object System.Threading.Mutex(
        $false,
        "Local\VibeCodingClassroomBootstrap"
    )

    try {
        $MutexAcquired = $Mutex.WaitOne(0, $false)
    }
    catch [System.Threading.AbandonedMutexException] {
        $MutexAcquired = $true
    }

    if (-not $MutexAcquired) {
        throw "Another Vibe Coding setup is already running. Close the other setup window first."
    }

    foreach ($directory in @(
        $AppRoot,
        $RuntimeRoot,
        $DownloadRoot,
        $LogRoot,
        $StateRoot,
        $OpenCodeProfile,
        $NpmCache,
        $NpmGlobal,
        $SecretRoot
    )) {
        Ensure-Directory $directory
    }

    try {
        Start-Transcript -Path $LogFile -Force | Out-Null
        $TranscriptStarted = $true
    }
    catch {
        Write-Warn "Transcript logging could not start."
    }

    Clear-Host
    Write-Host "==============================================" -ForegroundColor Cyan
    Write-Host "       Vibe Coding Classroom Launcher         " -ForegroundColor Cyan
    Write-Host "==============================================" -ForegroundColor Cyan
    Write-Host "Bootstrap: $BootstrapVersion"
    Write-Host "Data:      $AppRoot"
    Write-Host "Log:       $LogFile"

    # Older Windows PowerShell installations may not default to
    # TLS 1.2.
    try {
        [Net.ServicePointManager]::SecurityProtocol =
            [Net.ServicePointManager]::SecurityProtocol -bor
            [Net.SecurityProtocolType]::Tls12
    }
    catch {}

    Ensure-LoopbackNoProxy

    $Architecture = Get-WindowsArchitecture
    Write-OK "Windows architecture: $Architecture"

    # Verify the working area really is writable.
    $probe = Join-Path $AppRoot ".write-test-$PID"
    Set-Content -LiteralPath $probe -Value "ok" -Encoding ASCII
    Remove-Item -LiteralPath $probe -Force
    Write-OK "Classroom environment directory is writable"

    # Disk-space warning/failure.
    try {
        $rootPath = [IO.Path]::GetPathRoot($AppRoot)
        $driveName = $rootPath.Substring(0, 1)
        $drive = Get-PSDrive -Name $driveName -ErrorAction Stop

        if ($drive.Free -lt 1GB) {
            throw "Less than 1 GB of free disk space remains."
        }

        Write-OK ("Free disk: {0:N1} GB" -f ($drive.Free / 1GB))
    }
    catch {
        if ($_.Exception.Message -like "Less than 1 GB*") {
            throw
        }
        Write-Warn "Free disk space could not be determined."
    }

    # ========================================================
    # Tencent key first, so a bad deployment package fails
    # before downloading large runtimes.
    # ========================================================
    Write-Section "Checking Tencent classroom credential"

    $TencentKey = Install-TencentCredential
    $KeyFingerprint = Get-KeyFingerprint $TencentKey
    Write-OK "Tencent credential loaded"

    Test-TencentAPI $TencentKey $KeyFingerprint

    # OpenCode V2 uses this declared provider environment variable
    # to mark the custom provider as available and to populate the
    # OpenAI-compatible Authorization header.
    $env:TENCENT_API_KEY = $TencentKey

    # ========================================================
    # Python
    # ========================================================
    Write-Section "Checking Python"

    $PythonInfo = Find-Python312

    if ($PythonInfo) {
        Write-OK "Python 3.12 found"
    }
    else {
        $PythonInfo = Install-PrivatePython $Architecture
        Write-OK "Private Python $PythonVersion installed"
    }

    if ($Repair -or (-not (Test-ClassPython))) {
        try {
            Create-ClassPython $PythonInfo
        }
        catch {
            # An existing Python can be subtly broken: missing
            # venv/ensurepip, unusual distributor build, etc.
            if (-not $PythonInfo.Managed) {
                Write-Warn "Existing Python could not create a healthy environment. Falling back to classroom Python."
                $PythonInfo = Install-PrivatePython $Architecture
                Create-ClassPython $PythonInfo
            }
            else {
                throw
            }
        }
    }

    $ClassPython = Join-Path $PythonVenvRoot "Scripts\python.exe"
    $PythonScripts = Join-Path $PythonVenvRoot "Scripts"
    $PythonVersionText = (& $ClassPython --version 2>&1 | Out-String).Trim()
    Write-OK "$PythonVersionText + pip"

    # Workshop packages (pandas / scikit-learn / fastapi / uvicorn) for
    # the Titanic scripts (01_eda.py, 02_train.py, 03_dashboard.py).
    Install-WorkshopDependencies

    # ========================================================
    # Node.js
    # ========================================================
    Write-Section "Checking Node.js"

    $NodeInfo = $null

    if ((-not $Repair) -and (Test-PrivateNode)) {
        $NodeInfo = [PSCustomObject]@{
            Node = Join-Path $NodeRoot "node.exe"
            Npm = Join-Path $NodeRoot "npm.cmd"
            Managed = $true
        }
        Write-OK "Private Node.js is ready"
    }
    else {
        try {
            Install-PrivateNode $Architecture

            $NodeInfo = [PSCustomObject]@{
                Node = Join-Path $NodeRoot "node.exe"
                Npm = Join-Path $NodeRoot "npm.cmd"
                Managed = $true
            }

            Write-OK "Private Node.js installed"
        }
        catch {
            Write-Warn "Private Node setup failed: $($_.Exception.Message)"
            $NodeInfo = Find-SystemNodeFallback

            if (-not $NodeInfo) {
                throw
            }

            Write-Warn "Using the student's existing Node.js as fallback."
        }
    }

    $NodeVersionResult = Invoke-NativeCapture `
        -FilePath $NodeInfo.Node `
        -Arguments @("--version")

    $NpmVersionResult = Invoke-NativeCapture `
        -FilePath $NodeInfo.Npm `
        -Arguments @("--version")

    $NodeVersionText = $NodeVersionResult.Output.Trim()
    $NpmVersionText = $NpmVersionResult.Output.Trim()
    Write-OK "Node $NodeVersionText / npm $NpmVersionText"

    # ========================================================
    # Controlled process PATH
    # ========================================================
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $nodeDirectory = Split-Path -Parent $NodeInfo.Node

    $pathParts = @(
        $PythonScripts,
        $nodeDirectory,
        $NpmGlobal,
        $OpenCodePrefix,
        $machinePath,
        $userPath
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }

    $ManagedPath = ($pathParts -join ";")

    # Only this process and OpenCode receive this PATH.
    $env:Path = $ManagedPath
    $env:PYTHONUTF8 = "1"
    $env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
    $env:NPM_CONFIG_PREFIX = $NpmGlobal
    $env:NPM_CONFIG_CACHE = $NpmCache
    $env:NPM_CONFIG_FUND = "false"
    $env:NPM_CONFIG_AUDIT = "false"
    $env:NPM_CONFIG_UPDATE_NOTIFIER = "false"

    # ========================================================
    # OpenCode
    # ========================================================
    Write-Section "Checking OpenCode"

    $Profile = Configure-OpenCodeProfile
    $ClassroomConfigJson = New-OpenCodeClassroomConfig

    # Resolve the exact global configuration directory from the
    # installed OpenCode build and keep a readable copy there.
    # The enforced copy is injected later through
    # OPENCODE_CONFIG_CONTENT using the exact 2.0.20 schema.
    Remove-Item Env:OPENCODE_CONFIG_CONTENT -ErrorAction SilentlyContinue
    Remove-Item Env:OPENCODE_CONFIG -ErrorAction SilentlyContinue

    $OpenCode = Find-OpenCode

    if ($Repair -or (-not $OpenCode)) {
        $OpenCode = Install-OpenCode $NodeInfo.Npm
    }

    if (-not (Test-OpenCode $OpenCode)) {
        throw "OpenCode failed its V2 health check."
    }

    $OpenCodeVersionInfo = Get-OpenCodeVersion $OpenCode
    $OpenCodeVersion = $OpenCodeVersionInfo.Raw
    Write-OK "$OpenCodeVersion"

    # Kill any previously auto-started V2 service before model/config
    # validation. Earlier test bundles may have spawned a shared service
    # with stale OPENCODE_CONFIG_CONTENT in its environment.
    [void](Invoke-NativeQuiet `
        -FilePath $OpenCode `
        -Arguments @("service", "stop"))

    # Force this exact classroom config at the highest normal runtime
    # precedence. This also prevents project-level opencode.json files
    # from redirecting students to another provider.
    $env:OPENCODE_CONFIG_CONTENT = $ClassroomConfigJson

    $ResolvedConfigDirectory = Resolve-ClassroomOpenCodeConfigDirectory `
        $OpenCode `
        $Profile

    $ClassroomConfigFile = Install-ClassroomOpenCodeConfig `
        $ResolvedConfigDirectory `
        $ClassroomConfigJson

    Write-OK "Classroom config: $ClassroomConfigFile"

    # Model listing is advisory only.
    #
    # OpenCode 2.x has a known class of issues where custom
    # OpenAI-compatible models may be absent from model lists/UI even
    # though direct provider/model inference works. A real completion
    # is therefore the authoritative validation for this deployment.
    $modelResult = Invoke-NativeCapture `
        -FilePath $OpenCode `
        -Arguments @("models", "--standalone")

    $modelOutput = $modelResult.Output
    $modelExitCode = $modelResult.ExitCode

    if (($modelExitCode -eq 0) -and
        ($modelOutput -match [regex]::Escape($TencentModelRef))) {

        Write-OK "Model list contains: $TencentModelRef"
    }
    elseif ($modelExitCode -eq 0) {

        Write-Warn "OpenCode model listing did not display the custom Tencent model."
        Write-Host "Testing direct inference instead." -ForegroundColor DarkGray
    }
    else {

        Write-Warn "OpenCode model listing returned exit code $modelExitCode."

        if (-not [string]::IsNullOrWhiteSpace($modelOutput)) {
            Write-Host $modelOutput -ForegroundColor DarkGray
        }

        Write-Host "Testing direct inference instead." -ForegroundColor DarkGray
    }

    # Validate the actual OpenCode adapter once per key/OpenCode
    # version. This is the authoritative provider/model test.
    Test-OpenCodeProvider `
        $OpenCode `
        $KeyFingerprint `
        $OpenCodeVersion

    # ========================================================
    # Service
    # ========================================================
    $Credentials = Get-WebCredentials

    # Stop our isolated service before probing ports, otherwise
    # our own previous instance would make its port look occupied.
    [void](Invoke-NativeQuiet `
        -FilePath $OpenCode `
        -Arguments @("service", "stop"))

    $Port = Find-FreePort $PreferredPort $LastPort

    if ($Port -ne $PreferredPort) {
        Write-Warn "Port $PreferredPort is already in use. Using $Port instead. No process was killed."
    }

    $Server = Start-OpenCodeService `
        $OpenCode `
        $Port `
        $Credentials `
        $ManagedPath `
        $Profile `
        $env:TENCENT_API_KEY `
        $ClassroomConfigJson

    # ========================================================
    # Workshop page (React UI + workshop server, separate service)
    # ========================================================
    $WorkshopPagePort = Find-FreePort $PreferredWorkshopPort $LastWorkshopPort

    Write-Section "Starting the workshop web page (React UI + workshop server)"

    $WorkshopPage = Start-WorkshopPage `
        -Python $ClassPython `
        -ProjectRoot $ClassroomProjectRoot `
        -Port $WorkshopPagePort

    if ($WorkshopPage -and $WorkshopPage.Ok) {
        [void](Open-Browser ("http://127.0.0.1:{0}" -f $WorkshopPage.Port))
    }

    # ========================================================
    # Success
    # ========================================================
    Write-Host ""
    Write-Host "==============================================" -ForegroundColor Green
    Write-Host "              READY TO VIBE CODE              " -ForegroundColor Green
    Write-Host "==============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "OpenCode:     $($Server.Url)"
    if ($WorkshopPage -and $WorkshopPage.Ok) {
        Write-Host "Workshop page: http://127.0.0.1:$($WorkshopPage.Port)"
    }
    Write-Host "Model:        $TencentModelRef"
    Write-Host "Python:       $PythonVersionText"
    Write-Host "Node:         $NodeVersionText"
    Write-Host ""

        if ($Server.Paired) {
            Write-Host "The browser should already be signed in." -ForegroundColor Green
        }
        else {
            Write-Host "Browser pairing could not be automated." -ForegroundColor Yellow
            Write-Host "Sign in with:" -ForegroundColor Yellow
            Write-Host "  Username: $($Credentials.username)"
            Write-Host "  Password: $($Credentials.password)"
        }

        # Always show the manual recovery route (never assume the browser staged itself).
        Write-Host ""
        Write-Host "If a page keeps loading:"
        Write-Host "  1. Refresh the browser (F5), or open manually: $($Server.Url)"
        if ($WorkshopPage -and $WorkshopPage.Ok) {
            Write-Host "     workshop page: http://127.0.0.1:$($WorkshopPage.Port)"
        }
        Write-Host "  2. Username: $($Credentials.username)   Password: $($Credentials.password)"
        Write-Host "  3. A hidden watchdog restarts both servers automatically if they stop answering."

        # A detached watchdog keeps both classroom services healthy even
        # after this window closes (auto-restarts for up to 8 hours).
        try {
            Start-ClassWatchdog `
                -OpenCode $OpenCode `
                -Port $Server.Port `
                -WatchdogLog $LatestLog `
                -Python $ClassPython `
                -PagePort $WorkshopPagePort `
                -ProjectRoot $ClassroomProjectRoot
            Write-OK "Watchdog running (keeps both classroom pages alive for the next 8 hours)"
        }
        catch {
            Write-Warn "Watchdog could not start: $($_.Exception.Message)"
        }

        Write-Host ""
        Write-Host "Support log:" -ForegroundColor DarkGray
        Write-Host "  $LogFile" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "It is safe to close this window." -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "Press ENTER to close this window (read the notes above first)." -ForegroundColor Green
        [void](Read-Host)
}
catch {
    $ExitCode = 1

    Write-Host ""
    Write-Host "==============================================" -ForegroundColor Red
    Write-Host "                 SETUP FAILED                 " -ForegroundColor Red
    Write-Host "==============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "It is safe to run the launcher again." -ForegroundColor Yellow
    Write-Host "If normal launch keeps failing, run REPAIR VIBE CODING.bat." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Support log:"
    Write-Host "  $LogFile"
    Write-Host ""
    Write-Host "Classroom environment:"
    Write-Host "  $AppRoot"
    Write-Host ""
}
finally {
    if ($TranscriptStarted) {
        try { Stop-Transcript | Out-Null } catch {}
    }

    if (Test-Path -LiteralPath $LogFile) {
        try {
            Copy-Item -LiteralPath $LogFile -Destination $LatestLog -Force
        }
        catch {}
    }

    if ($Mutex -and $MutexAcquired) {
        try { $Mutex.ReleaseMutex() } catch {}
    }

    if ($Mutex) {
        try { $Mutex.Dispose() } catch {}
    }
}

exit $ExitCode

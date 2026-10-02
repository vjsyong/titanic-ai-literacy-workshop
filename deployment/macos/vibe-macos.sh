#!/bin/bash
# ============================================================
# Vibe Coding Classroom Launcher -- macOS
# ============================================================
# Mirrors the Windows launcher (deployment/oneclick.ps1):
#
#   1. verifies the OpenRouter classroom credential
#   2. prepares a private Python (uv-managed) + workshop packages
#   3. prepares a private Node.js
#   4. installs and pins OpenCode 2.0.20
#   5. starts the OpenCode Web UI + the workshop web page
#   6. starts a watchdog that keeps both pages alive for 8 hours
#
# Everything private lives in:
#   ~/Library/Application Support/VibeCoding
# The API key lives in:
#   ~/.vibecoding/openrouter-key.txt
#
# Commands:
#   start            normal launch (default)
#   repair           rebuild the runtimes without touching the project
#   start-page       start/reopen just the workshop page
#   reset-workshop   restore scripts + data to their original state
#   reset-env        remove the classroom runtime and the stored key
#
# This script targets macOS (bash 3.2 compatible). It cannot be run
# on Windows or Linux.
# ============================================================

set -u

COMMAND="${1:-start}"
REPAIR=0

case "$COMMAND" in
    repair)         REPAIR=1; COMMAND="start" ;;
    start|start-page|reset-workshop|reset-env) ;;
    *) echo "Unknown command: $COMMAND"; exit 2 ;;
esac

# ============================================================
# Locations
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
DEPLOY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$DEPLOY_DIR/.." && pwd)"
KEY_FILE="$DEPLOY_DIR/key.txt"
BASELINE_ROOT="$DEPLOY_DIR/baseline"

APP_ROOT="$HOME/Library/Application Support/VibeCoding"
RUNTIME_ROOT="$APP_ROOT/runtime"
LOG_ROOT="$APP_ROOT/logs"
STATE_ROOT="$APP_ROOT/state"
DOWNLOAD_ROOT="$APP_ROOT/downloads"
PYTHON_VENV="$APP_ROOT/python"
SECRET_ROOT="$HOME/.vibecoding"
SECRET_KEY="$SECRET_ROOT/openrouter-key.txt"

PROFILE_ROOT="$RUNTIME_ROOT/opencode-profile"
PROFILE_CONFIG="$PROFILE_ROOT/config"
PROFILE_DATA="$PROFILE_ROOT/data"
PROFILE_CACHE="$PROFILE_ROOT/cache"
PROFILE_STATE="$PROFILE_ROOT/state"
PROFILE_TEMP="$PROFILE_ROOT/temp"
NPM_GLOBAL="$RUNTIME_ROOT/npm-global"
NPM_CACHE="$RUNTIME_ROOT/npm-cache"
NODE_ROOT="$RUNTIME_ROOT/node"
UV_ROOT="$RUNTIME_ROOT/uv"
UV_BIN="$RUNTIME_ROOT/bin/uv"
UV_PYTHON_DIR="$RUNTIME_ROOT/uv-python"
CLASS_PYTHON="$PYTHON_VENV/bin/python"

LOCK_DIR="$STATE_ROOT/launcher.lock"
LAUNCHER_STATE="$STATE_ROOT/launcher.json"
WATCHDOG_PID_FILE="$STATE_ROOT/watchdog.pid"
PAIR_STATE="$STATE_ROOT/browser-pair.txt"
CREDENTIALS_FILE="$STATE_ROOT/web-credentials.json"
PROVIDER_TEST_STATE="$STATE_ROOT/provider-test.txt"

LOG_FILE="$LOG_ROOT/setup-$(date +%Y%m%d-%H%M%S).log"
LATEST_LOG="$LOG_ROOT/latest.log"

NODE_VERSION="24.21.0"
OPENCODE_VERSION="2.0.20"
BOOTSTRAP_VERSION="2026-10-02.1-macos"

OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
OPENROUTER_MODEL="xiaomi/mimo-v2.6-flash"
OPENROUTER_MODEL_REF="openrouter/$OPENROUTER_MODEL"

PREFERRED_OPENCODE_PORT=4096
LAST_OPENCODE_PORT=4196
PREFERRED_PAGE_PORT=4097
LAST_PAGE_PORT=4197
OPENCODE_USERNAME="opencode"

OPENCODE_BIN=""
NODE_BIN=""
NPM_BIN=""
CLASSROOM_CONFIG=""

# ============================================================
# Console helpers
# ============================================================

if [ -t 1 ]; then
    C_CYAN="$(printf '\033[36m')"; C_GREEN="$(printf '\033[32m')"
    C_YELLOW="$(printf '\033[33m')"; C_RED="$(printf '\033[31m')"
    C_DIM="$(printf '\033[2m')"; C_RESET="$(printf '\033[0m')"
else
    C_CYAN=""; C_GREEN=""; C_YELLOW=""; C_RED=""; C_DIM=""; C_RESET=""
fi

info()    { printf '%s\n' "$1"; }
section() { printf '\n%s== %s ==%s\n' "$C_CYAN" "$1" "$C_RESET"; }
ok()      { printf '%s[OK] %s%s\n' "$C_GREEN" "$1" "$C_RESET"; }
warn()    { printf '%s[WARN] %s%s\n' "$C_YELLOW" "$1" "$C_RESET"; }

die() {
    printf '\n%s==============================================%s\n' "$C_RED" "$C_RESET"
    printf '%s                 SETUP FAILED                 %s\n' "$C_RED" "$C_RESET"
    printf '%s==============================================%s\n' "$C_RED" "$C_RESET"
    printf '\n%s\n\n' "$1"
    info "It is safe to run the launcher again."
    info "If normal launch keeps failing, run REPAIR VIBE CODING."
    printf '\nSupport log:\n  %s\n\n' "$LOG_FILE"
    exit 1
}

# ============================================================
# Cleanup / locking
# ============================================================

cleanup() {
    lock_pid="$(cat "$LOCK_DIR/pid" 2>/dev/null || echo "")"
    if [ "$lock_pid" = "$$" ]; then
        rm -rf "$LOCK_DIR"
        rm -f "$LAUNCHER_STATE"
    fi
}

trap cleanup EXIT

tty_read() {
    # Read one line from the user; works from double-clicked .command files.
    if [ -r /dev/tty ]; then
        read -r -p "$1" REPLY_VALUE < /dev/tty || REPLY_VALUE=""
    else
        REPLY_VALUE=""
    fi
}

current_lock_pid() {
    [ -f "$LOCK_DIR/pid" ] || { echo ""; return; }
    cat "$LOCK_DIR/pid" 2>/dev/null
}

launcher_processes() {
    # Every running vibe-macos.sh besides this one (catches stale locks).
    pgrep -f "vibe-macos.sh" 2>/dev/null | grep -vx "$$" || true
}

stop_previous_session() {
    # Watchdog first: it would restart services mid-launch.
    if [ -f "$WATCHDOG_PID_FILE" ]; then
        watchdog_pid="$(cat "$WATCHDOG_PID_FILE" 2>/dev/null)"
        if [ -n "$watchdog_pid" ] && kill -0 "$watchdog_pid" 2>/dev/null; then
            kill "$watchdog_pid" 2>/dev/null || true
        fi
        rm -f "$WATCHDOG_PID_FILE"
    fi

    killed=0

    for other_pid in $(launcher_processes); do
        if [ -n "$other_pid" ] && [ "$other_pid" != "$$" ]; then
            kill "$other_pid" 2>/dev/null || true
            killed=1
        fi
    done

    lock_pid="$(current_lock_pid)"
    if [ -n "$lock_pid" ] && [ "$lock_pid" != "$$" ]; then
        kill "$lock_pid" 2>/dev/null || true
        killed=1
    fi

    sleep 1
    rm -rf "$LOCK_DIR"
    rm -f "$LAUNCHER_STATE"

    return $killed
}

acquire_lock() {
    if mkdir "$LOCK_DIR" 2>/dev/null; then
        echo "$$" > "$LOCK_DIR/pid"
        return 0
    fi

    lock_pid="$(current_lock_pid)"
    other_alive=0
    [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null && other_alive=1

    if [ "$other_alive" -eq 0 ] && [ -z "$(launcher_processes)" ]; then
        # Stale lock from a crashed run.
        rm -rf "$LOCK_DIR"
        mkdir "$LOCK_DIR" 2>/dev/null && echo "$$" > "$LOCK_DIR/pid" && return 0
    fi

    # --------------------------------------------------------
    # Another session is running. That is harmless: tell the
    # student, and offer to stop it and start fresh.
    # --------------------------------------------------------
    printf '\n%s==============================================%s\n' "$C_CYAN" "$C_RESET"
    printf '%s       VIBE CODING IS ALREADY RUNNING         %s\n' "$C_CYAN" "$C_RESET"
    printf '%s==============================================%s\n' "$C_CYAN" "$C_RESET"
    printf '\nAnother Vibe Coding window is already open.\n'
    printf 'Everything is fine -- you can keep using it.\n\n'

    if [ -f "$LAUNCHER_STATE" ]; then
        started="$(sed -n 's/.*"startedAt":"\([^"]*\)".*/\1/p' "$LAUNCHER_STATE" 2>/dev/null)"
        [ -n "$started" ] && printf '%sIt has been running since %s.%s\n\n' "$C_DIM" "$started" "$C_RESET"
    fi

    REPLY_VALUE=""
    tty_read "Stop the other session and start a fresh one here? [y/N] "

    case "$REPLY_VALUE" in
        y|Y|yes|YES|Yes) ;;
        *)
            printf '\n%sKeeping the existing session. Nothing to worry about.%s\n' "$C_GREEN" "$C_RESET"
            printf 'To watch the workshop page, run START WORKSHOP PAGE.\n'
            printf 'To start fresh later, close that window first or answer [y] here.\n\n'
            exit 0
            ;;
    esac

    info "Stopping the other session..."
    stop_previous_session
    ok "Stopped the other session"

    acquired=0
    for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 \
             21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40; do
        if mkdir "$LOCK_DIR" 2>/dev/null; then
            echo "$$" > "$LOCK_DIR/pid"
            acquired=1
            break
        fi
        sleep 0.25
    done

    if [ "$acquired" -ne 1 ]; then
        printf '\nSomething else grabbed the session; try again in a moment.\n\n'
        exit 0
    fi

    ok "Starting a fresh session"
    printf '\n'
    return 0
}

# ============================================================
# Start here
# ============================================================

if [ "$(uname -s)" != "Darwin" ]; then
    echo "This launcher is for macOS only. Use START VIBE CODING.bat on Windows."
    exit 2
fi

case "$(uname -m)" in
    arm64) UV_ARCH="aarch64"; NODE_ARCH="arm64" ;;
    x86_64) UV_ARCH="x86_64"; NODE_ARCH="x64" ;;
    *) echo "Unsupported Mac architecture: $(uname -m)"; exit 2 ;;
esac

mkdir -p "$APP_ROOT" "$LOG_ROOT" "$STATE_ROOT" "$DOWNLOAD_ROOT"

# Mirror the whole console to the support log.
exec > >(tee -a "$LOG_FILE") 2>&1

if [ "$COMMAND" = "reset-env" ]; then
    printf '\n==============================================\n'
    printf '       RESET VIBE CODING ENVIRONMENT\n'
    printf '==============================================\n\n'
    printf 'This removes ONLY the managed classroom runtime:\n\n'
    printf '  %s\n' "$APP_ROOT"
    printf '  %s\n\n' "$SECRET_ROOT"
    printf 'It does NOT remove student projects or your normal OpenCode data.\n\n'

    REPLY_VALUE=""
    tty_read "Type RESET to continue: "

    if [ "$REPLY_VALUE" != "RESET" ]; then
        echo "Cancelled."
        exit 0
    fi

    # Stop any running classroom session before pulling the runtime out.
    stop_previous_session >/dev/null 2>&1 || true

    if [ -x "$NPM_GLOBAL/bin/opencode" ]; then
        "$NPM_GLOBAL/bin/opencode" service stop >/dev/null 2>&1 || true
    fi

    rm -rf "$APP_ROOT" "$SECRET_ROOT"
    echo
    echo "Classroom environment reset."
    echo "Run START VIBE CODING to rebuild it."
    echo
    exit 0
fi

# Single-instance lock (also handles the friendly conflict prompt).
acquire_lock

mkdir -p \
    "$RUNTIME_ROOT" "$STATE_ROOT" "$DOWNLOAD_ROOT" \
    "$PROFILE_CONFIG" "$PROFILE_DATA" "$PROFILE_CACHE" "$PROFILE_STATE" "$PROFILE_TEMP" \
    "$NPM_GLOBAL" "$NPM_CACHE" "$SECRET_ROOT"

{ printf '{"pid":%s,"startedAt":"%s","script":"%s"}\n' \
    "$$" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$SCRIPT_DIR/vibe-macos.sh"; } > "$LAUNCHER_STATE"

printf '\n==============================================\n'
printf '       Vibe Coding Classroom Launcher         \n'
printf '==============================================\n'
printf 'Bootstrap: %s\n' "$BOOTSTRAP_VERSION"
printf 'Data:      %s\n' "$APP_ROOT"
printf 'Log:       %s\n' "$LOG_FILE"

# ============================================================
# Port helper (used by the page commands below)
# ============================================================

find_free_port() {
    "$CLASS_PYTHON" - "$1" "$2" <<'PY'
import socket
import sys

for port in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", port))
        print(port)
        sys.exit(0)
    except OSError:
        pass
    finally:
        sock.close()

sys.exit(1)
PY
}

# ============================================================
# Workshop page only (START WORKSHOP PAGE)
# ============================================================

start_workshop_page() {
    if [ ! -x "$CLASS_PYTHON" ]; then
        die "The classroom Python is not installed yet. Run START VIBE CODING first."
    fi

    if [ ! -f "$PROJECT_ROOT/serve_workshop.py" ]; then
        die "serve_workshop.py is missing from the workshop folder."
    fi

    section "Workshop page"

    page_port="$(find_free_port "$PREFERRED_PAGE_PORT" "$LAST_PAGE_PORT")" \
        || die "No free port for the workshop page."

    ( cd "$PROJECT_ROOT" && "$CLASS_PYTHON" serve_workshop.py --port "$page_port" --no-browser ) \
        || die "serve_workshop.py could not start the page."

    open "http://127.0.0.1:$page_port" 2>/dev/null || true
    ok "Workshop page ready at http://127.0.0.1:$page_port"
}

if [ "$COMMAND" = "start-page" ]; then
    start_workshop_page
    printf '\nPress ENTER to close this window.\n'
    tty_read ""
    exit 0
fi

# ============================================================
# Reset workshop (RESET WORKSHOP)
# ============================================================

restore_from_baseline() {
    relative="$1"
    baseline="$BASELINE_ROOT/$relative"
    target="$PROJECT_ROOT/$relative"

    if [ -f "$baseline" ]; then
        mkdir -p "$(dirname "$target")"
        cp -f "$baseline" "$target"
        ok "Restored $relative"
        return 0
    fi

    if command -v git >/dev/null 2>&1 && [ -d "$PROJECT_ROOT/.git" ]; then
        ( cd "$PROJECT_ROOT" && git checkout -- "$relative" ) 2>/dev/null \
            && { ok "Restored $relative (git)"; return 0; }
    fi

    warn "Could not restore $relative"
    return 1
}

if [ "$COMMAND" = "reset-workshop" ]; then
    printf '\n==============================================\n'
    printf '         RESET WORKSHOP PROGRESS\n'
    printf '==============================================\n\n'
    printf 'Restores the three workshop scripts AND the\n'
    printf 'passenger data to their original state, and\n'
    printf 'deletes generated artifacts.\n\n'
    printf 'NOT touched: classroom runtime, API key, web UI.\n\n'

    REPLY_VALUE=""
    tty_read "Type RESET to continue: "

    if [ "$REPLY_VALUE" != "RESET" ]; then
        echo "Cancelled."
        exit 0
    fi

    section "Restoring workshop scripts"
    restore_from_baseline "01_eda.py" || true
    restore_from_baseline "02_train.py" || true
    restore_from_baseline "03_dashboard.py" || true

    section "Restoring passenger data"
    restore_from_baseline "data/titanic.csv" || true

    section "Removing generated artifacts"
    rm -rf "$PROJECT_ROOT/titanic_model.pkl" \
           "$PROJECT_ROOT/__pycache__" \
           "$PROJECT_ROOT/.workshop"
    ok "Removed generated artifacts"

    printf '\n%s==============================================%s\n' "$C_GREEN" "$C_RESET"
    printf '%s          WORKSHOP RESET COMPLETE%s\n' "$C_GREEN" "$C_RESET"
    printf '%s==============================================%s\n\n' "$C_GREEN" "$C_RESET"
    printf 'All 18 checkpoints are locked again.\n'
    printf 'Tip: start a fresh chat with the AI Teaching Assistant\n'
    printf 'so it does not remember the previous run.\n\n'
    printf 'Press ENTER to close this window.\n'
    tty_read ""
    exit 0
fi

# ============================================================
# Helpers used by the main flow
# ============================================================

strip_ansi() {
    esc="$(printf '\033')"
    LC_ALL=C sed "s/${esc}\[[0-9;?]*[ -/]*[@-~]//g"
}

ensure_credential() {
    section "Checking OpenRouter classroom credential"

    if [ -f "$KEY_FILE" ]; then
        key="$(tr -d '\r\n' < "$KEY_FILE" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
    else
        key=""
    fi

    if [ -z "$key" ] || [ "$key" = "PASTE_OPENROUTER_KEY_HERE" ]; then
        if [ -f "$SECRET_KEY" ] && [ -s "$SECRET_KEY" ]; then
            key="$(tr -d '\r\n' < "$SECRET_KEY")"
            warn "deployment/key.txt is missing -- reusing the already installed credential."
        else
            die "The OpenRouter API key is missing. Put it in deployment/key.txt (starts with sk-or-)."
        fi
    fi

    case "$key" in
        sk-or-*) ;;
        *) die "key.txt does not look like an OpenRouter API key (should start with sk-or-)." ;;
    esac

    if [ "${#key}" -lt 20 ]; then
        die "key.txt does not look like the expected OpenRouter API key format."
    fi

    chmod 700 "$SECRET_ROOT" 2>/dev/null || true
    printf '%s' "$key" > "$SECRET_KEY"
    chmod 600 "$SECRET_KEY"
    ok "OpenRouter credential loaded"

    section "Testing OpenRouter connectivity"
    http_code="$(curl -s -o /dev/null -w '%{http_code}' -m 90 \
        -X POST "$OPENROUTER_BASE_URL/chat/completions" \
        -H "Authorization: Bearer $key" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"$OPENROUTER_MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply with exactly OK.\"}],\"stream\":false,\"reasoning\":{\"enabled\":false},\"provider\":{\"only\":[\"xiaomi/fp8\"],\"allow_fallbacks\":false}}" \
        2>/dev/null || echo "000")"

    if [ "$http_code" != "200" ]; then
        die "OpenRouter test failed (HTTP $http_code).

Possible causes:
- Invalid or expired key
- No OpenRouter credits or entitlement
- Campus firewall/proxy
- OpenRouter unreachable right now

The API key itself was not written to this log."
    fi

    ok "Xiaomi MiMo v2.6 Flash API reachable via OpenRouter"
    key=""
}

ensure_uv() {
    if [ "$REPAIR" -eq 0 ] && [ -x "$UV_BIN" ]; then
        return 0
    fi

    section "Installing private Python tooling (uv)"
    mkdir -p "$(dirname "$UV_BIN")"

    url="https://github.com/astral-sh/uv/releases/latest/download/uv-${UV_ARCH}-apple-darwin.tar.gz"
    archive="$DOWNLOAD_ROOT/uv-${UV_ARCH}.tar.gz"
    rm -f "$archive"

    if ! curl -fL --retry 3 --retry-delay 2 -o "$archive" "$url"; then
        return 1
    fi

    rm -rf "$UV_ROOT"
    mkdir -p "$UV_ROOT"

    if ! tar -xzf "$archive" -C "$UV_ROOT" 2>/dev/null; then
        return 1
    fi

    found="$(find "$UV_ROOT" -type f -name uv 2>/dev/null | head -1)"
    [ -n "$found" ] || return 1

    mv -f "$found" "$UV_BIN"
    chmod +x "$UV_BIN"
    return 0
}

ensure_python() {
    section "Checking Python"

    if [ "$REPAIR" -eq 0 ] && [ -x "$CLASS_PYTHON" ] \
        && "$CLASS_PYTHON" -c 'import pandas, sklearn, fastapi, uvicorn' >/dev/null 2>&1; then
        ok "Classroom Python is ready"
        return 0
    fi

    rm -rf "$PYTHON_VENV"
    mkdir -p "$UV_PYTHON_DIR"

    if ensure_uv; then
        UV_PYTHON_INSTALL_DIR="$UV_PYTHON_DIR" \
            "$UV_BIN" venv --python 3.12 "$PYTHON_VENV" >/dev/null 2>&1 \
            || die "Could not create the classroom Python environment."

        UV_PYTHON_INSTALL_DIR="$UV_PYTHON_DIR" \
            "$UV_BIN" pip install --python "$CLASS_PYTHON" \
            pandas scikit-learn fastapi uvicorn \
            || die "Could not install the workshop Python packages."
    else
        warn "uv download failed -- trying the Mac's own Python 3."
        system_python="$(command -v python3 2>/dev/null || true)"

        if [ -z "$system_python" ] \
            || ! "$system_python" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
            die "No usable Python 3.10+ found and the private Python download failed.
Check the internet connection (or the campus proxy) and try again."
        fi

        "$system_python" -m venv "$PYTHON_VENV" \
            || die "Could not create the classroom Python environment."

        "$CLASS_PYTHON" -m pip install --quiet --upgrade pip >/dev/null 2>&1 || true
        "$CLASS_PYTHON" -m pip install \
            pandas scikit-learn fastapi uvicorn \
            || die "Could not install the workshop Python packages."
    fi

    ok "$("$CLASS_PYTHON" --version) + workshop packages"
}

ensure_node() {
    section "Checking Node.js"

    if [ "$REPAIR" -eq 0 ] && [ -x "$NODE_ROOT/bin/node" ] && [ -x "$NODE_ROOT/bin/npm" ]; then
        NODE_BIN="$NODE_ROOT/bin/node"
        NPM_BIN="$NODE_ROOT/bin/npm"
        ok "Private Node.js is ready ($("$NODE_BIN" --version))"
        return 0
    fi

    tarball="node-v${NODE_VERSION}-darwin-${NODE_ARCH}.tar.gz"
    base="https://nodejs.org/dist/v${NODE_VERSION}"
    archive="$DOWNLOAD_ROOT/$tarball"

    rm -f "$archive"
    curl -fL --retry 3 --retry-delay 2 -o "$archive" "$base/$tarball" \
        || die "Could not download Node.js. Check the internet connection and try again."

    curl -fsL -o "$archive.sha256" "$base/SHASUMS256.txt" 2>/dev/null || true
    if [ -s "$archive.sha256" ]; then
        expected="$(grep " $tarball\$" "$archive.sha256" | awk '{print $1}')"
        actual="$(shasum -a 256 "$archive" | awk '{print $1}')"
        if [ -n "$expected" ] && [ "$expected" != "$actual" ]; then
            die "Node.js download failed its checksum. Try again on a better connection."
        fi
    fi

    rm -rf "$NODE_ROOT"
    mkdir -p "$NODE_ROOT"
    tar -xzf "$archive" -C "$NODE_ROOT" --strip-components=1 \
        || die "Could not unpack Node.js."

    NODE_BIN="$NODE_ROOT/bin/node"
    NPM_BIN="$NODE_ROOT/bin/npm"
    ok "Private Node.js installed ($("$NODE_BIN" --version))"
}

ensure_opencode() {
    section "Checking OpenCode"

    OPENCODE_BIN="$NPM_GLOBAL/bin/opencode"

    if [ "$REPAIR" -eq 0 ] && [ -x "$OPENCODE_BIN" ]; then
        version="$("$OPENCODE_BIN" --version 2>/dev/null | tr -d '\r')"
        ok "OpenCode $version"
        return 0
    fi

    export NPM_CONFIG_PREFIX="$NPM_GLOBAL"
    export NPM_CONFIG_CACHE="$NPM_CACHE"
    export NPM_CONFIG_FUND="false"
    export NPM_CONFIG_AUDIT="false"
    export NPM_CONFIG_UPDATE_NOTIFIER="false"

    "$NPM_BIN" install -g "@opencode/cli@${OPENCODE_VERSION}" >/dev/null \
        || die "Could not install OpenCode with npm."

    [ -x "$OPENCODE_BIN" ] || die "OpenCode was installed but its launcher is missing."
    ok "OpenCode installed ($("$OPENCODE_BIN" --version 2>/dev/null | tr -d '\r'))"
}

write_classroom_config() {
    mkdir -p "$PROFILE_CONFIG/opencode"

    CLASSROOM_CONFIG="$(cat <<'JSON'
{
  "$schema": "https://opencode.ai/config.json",
  "model": "openrouter/xiaomi/mimo-v2.6-flash",
  "enabled_providers": ["openrouter"],
  "permissions": [
    { "action": "read", "resource": "*", "effect": "allow" },
    { "action": "glob", "resource": "*", "effect": "allow" },
    { "action": "grep", "resource": "*", "effect": "deny" },
    { "action": "question", "resource": "*", "effect": "allow" },
    { "action": "edit", "resource": "*", "effect": "deny" },
    { "action": "edit", "resource": "01_eda.py", "effect": "allow" },
    { "action": "edit", "resource": "*/01_eda.py", "effect": "allow" },
    { "action": "edit", "resource": "02_train.py", "effect": "allow" },
    { "action": "edit", "resource": "*/02_train.py", "effect": "allow" },
    { "action": "edit", "resource": "03_dashboard.py", "effect": "allow" },
    { "action": "edit", "resource": "*/03_dashboard.py", "effect": "allow" },
    { "action": "read", "resource": "deployment/*", "effect": "deny" },
    { "action": "read", "resource": "*/deployment/*", "effect": "deny" },
    { "action": "shell", "resource": "*", "effect": "deny" },
    { "action": "shell", "resource": "python 01_eda.py *", "effect": "allow" },
    { "action": "shell", "resource": "python 02_train.py *", "effect": "allow" },
    { "action": "shell", "resource": "python 03_dashboard.py *", "effect": "allow" },
    { "action": "external_directory", "resource": "*", "effect": "deny" },
    { "action": "webfetch", "resource": "*", "effect": "deny" },
    { "action": "websearch", "resource": "*", "effect": "deny" },
    { "action": "subagent", "resource": "*", "effect": "deny" },
    { "action": "skill", "resource": "*", "effect": "deny" },
    { "action": "execute", "resource": "*", "effect": "deny" }
  ],
  "provider": {
    "openrouter": {
      "name": "OpenRouter",
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "https://openrouter.ai/api/v1",
        "apiKey": "{file:~/.vibecoding/openrouter-key.txt}",
        "timeout": 600000,
        "chunkTimeout": 120000,
        "body": { "reasoning": { "enabled": false } }
      },
      "models": {
        "xiaomi/mimo-v2.6-flash": {
          "name": "Xiaomi MiMo v2.6 Flash",
          "limit": { "context": 1050000, "output": 131072 }
        }
      }
    }
  }
}
JSON
)"

    printf '%s\n' "$CLASSROOM_CONFIG" > "$PROFILE_CONFIG/opencode/opencode.json"
    ok "Classroom config: $PROFILE_CONFIG/opencode/opencode.json"
}

managed_path() {
    printf '%s:%s:%s:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin' \
        "$PYTHON_VENV/bin" "$NODE_ROOT/bin" "$NPM_GLOBAL/bin"
}

# Keep the OpenCode profile + controlled PATH for direct CLI calls.
opencode_env() {
    export PATH="$(managed_path)"
    export XDG_DATA_HOME="$PROFILE_DATA"
    export XDG_CONFIG_HOME="$PROFILE_CONFIG"
    export XDG_CACHE_HOME="$PROFILE_CACHE"
    export XDG_STATE_HOME="$PROFILE_STATE"
    export TMPDIR="$PROFILE_TEMP"
    export OPENCODE_DISABLE_AUTOUPDATE=1
    export OPENCODE_CONFIG_CONTENT="$CLASSROOM_CONFIG"
    export PYTHONUTF8=1
    export NPM_CONFIG_PREFIX="$NPM_GLOBAL"
    export NPM_CONFIG_CACHE="$NPM_CACHE"
}

test_provider() {
    section "Validating the classroom model"

    fingerprint="$(shasum -a 256 "$SECRET_KEY" | awk '{print substr($1,1,16)}')"
    opencode_version="$("$OPENCODE_BIN" --version 2>/dev/null | tr -d '\r')"

    if [ "$REPAIR" -eq 0 ] && [ -f "$PROVIDER_TEST_STATE" ]; then
        if [ "$(cat "$PROVIDER_TEST_STATE")" = "$fingerprint:$opencode_version" ]; then
            ok "Classroom provider was already validated"
            return 0
        fi
    fi

    printf '%sTesting OpenCode -> OpenRouter provider routing...%s\n' "$C_DIM" "$C_RESET"

    opencode_env
    if ! ( cd "$PROJECT_ROOT" && "$OPENCODE_BIN" run --standalone \
            --model "$OPENROUTER_MODEL_REF" "Reply with exactly OK." ) \
            > "$DOWNLOAD_ROOT/provider-test.out" 2>&1; then
        tail -n 20 "$DOWNLOAD_ROOT/provider-test.out" || true
        die "OpenCode could not complete a request through the OpenRouter classroom model."
    fi

    printf '%s:%s\n' "$fingerprint" "$opencode_version" > "$PROVIDER_TEST_STATE"
    ok "OpenCode -> OpenRouter provider request succeeded"
}

service_env() {
    "$OPENCODE_BIN" service set env "$1" "$2" >/dev/null 2>&1 \
        || die "Could not set OpenCode service environment variable: $1"
}

start_service() {
    section "Starting OpenCode Web UI"

    port="$1"
    password="$2"

    "$OPENCODE_BIN" service stop >/dev/null 2>&1 || true
    "$OPENCODE_BIN" service unset disabled >/dev/null 2>&1 || true

    "$OPENCODE_BIN" service set hostname 127.0.0.1 >/dev/null 2>&1 \
        || die "Could not configure the OpenCode hostname."
    "$OPENCODE_BIN" service set port "$port" >/dev/null 2>&1 \
        || die "Could not configure the OpenCode port."
    "$OPENCODE_BIN" service set password "$password" >/dev/null 2>&1 \
        || die "Could not configure the OpenCode Web UI password."

    service_env PATH "$(managed_path)"
    service_env XDG_DATA_HOME "$PROFILE_DATA"
    service_env XDG_CONFIG_HOME "$PROFILE_CONFIG"
    service_env XDG_CACHE_HOME "$PROFILE_CACHE"
    service_env XDG_STATE_HOME "$PROFILE_STATE"
    service_env TMPDIR "$PROFILE_TEMP"
    service_env OPENCODE_DISABLE_AUTOUPDATE 1
    service_env OPENCODE_CONFIG_CONTENT "$CLASSROOM_CONFIG"
    service_env PYTHONUTF8 1
    service_env NPM_CONFIG_PREFIX "$NPM_GLOBAL"
    service_env NPM_CONFIG_CACHE "$NPM_CACHE"

    if ! ( cd "$PROJECT_ROOT" && "$OPENCODE_BIN" service start ) >/dev/null 2>&1; then
        warn "OpenCode service start failed. Trying one restart."
        ( cd "$PROJECT_ROOT" && "$OPENCODE_BIN" service restart ) >/dev/null 2>&1 \
            || die "OpenCode service could not start."
    fi

    healthy=0
    for _ in $(seq 1 60); do
        if opencode_env; "$OPENCODE_BIN" api GET /api/session >/dev/null 2>&1; then
            healthy=1
            break
        fi
        sleep 0.5
    done

    if [ "$healthy" -ne 1 ]; then
        "$OPENCODE_BIN" service stop >/dev/null 2>&1 || true
        sleep 1
        ( cd "$PROJECT_ROOT" && "$OPENCODE_BIN" service start ) >/dev/null 2>&1 || true

        for _ in $(seq 1 30); do
            if opencode_env; "$OPENCODE_BIN" api GET /api/session >/dev/null 2>&1; then
                healthy=1
                break
            fi
            sleep 0.5
        done
    fi

    [ "$healthy" -eq 1 ] || die "OpenCode service failed its API health check."
}

get_web_password() {
    if [ -f "$CREDENTIALS_FILE" ]; then
        stored="$(sed -n 's/.*"password":"\([^"]*\)".*/\1/p' "$CREDENTIALS_FILE" 2>/dev/null)"
        if [ -n "$stored" ]; then
            WEB_PASSWORD="$stored"
            return 0
        fi
    fi

    WEB_PASSWORD="$(LC_ALL=C tr -dc 'A-Za-z2-9' < /dev/urandom | head -c 24)"
    printf '{"username":"%s","password":"%s"}\n' "$OPENCODE_USERNAME" "$WEB_PASSWORD" \
        > "$CREDENTIALS_FILE"
    chmod 600 "$CREDENTIALS_FILE"
}

open_pairing() {
    base_url="$1"

    # One-time pairing keys must never be opened twice (a consumed key
    # hangs the browser tab). Remember the last key we handed out.
    pair_completed=0
    last_key=""
    if [ -f "$PAIR_STATE" ]; then
        pair_completed="$(sed -n 's/^completed=//p' "$PAIR_STATE" | head -1)"
        last_key="$(sed -n 's/^lastKey=//p' "$PAIR_STATE" | head -1)"
    fi

    if [ "$pair_completed" = "1" ]; then
        ok "Browser paired on a previous launch -- opening the workshop page directly."
        open "$base_url" 2>/dev/null || warn "Open manually: $base_url"
        PAIRED=1
        return 0
    fi

    PAIRED=0
    pair_output="$("$OPENCODE_BIN" pair --url "$base_url" 2>&1 || true)"
    login_url="$(printf '%s' "$pair_output" \
        | strip_ansi \
        | grep -oE 'https?://[^[:space:]]+' \
        | grep -F "$base_url" | grep -F "/auth/connect" | head -1 || true)"
    # Drop trailing punctuation that the printed URL may pick up.
    login_url="$(printf '%s' "$login_url" | sed 's/[])\]},;]*$//')"

    if [ -z "$login_url" ]; then
        warn "Automatic one-time pair-link parsing failed. Opening the Web UI normally."
        open "$base_url" 2>/dev/null || true
        return 0
    fi

    key_part="$(printf '%s' "$login_url" | grep -oE '[?&](token|key)=[^&[:space:]]+' | head -1 || true)"

    if [ -n "$key_part" ] && [ "$key_part" = "$last_key" ]; then
        warn "Pairing key was already used once -- skipping the auth URL to avoid a hanging page."
        open "$base_url" 2>/dev/null || true
        return 0
    fi

    if open "$login_url" 2>/dev/null; then
        PAIRED=1
    else
        warn "Could not open the browser. Open manually: $login_url"
    fi

    { printf 'completed=%s\nlastKey=%s\nrecordedAt=%s\n' \
        "$PAIRED" "$key_part" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$PAIR_STATE"
}

start_watchdog() {
    opencode_path="$1"; opencode_port="$2"
    python_path="$3"; page_port="$4"; project="$5"
    log="$6"

    watchdog_script="$APP_ROOT/watchdog.sh"

    cat > "$watchdog_script" <<WATCHDOG
#!/bin/bash
OPENCODE="$opencode_path"
PORT="$opencode_port"
PYTHON="$python_path"
PAGE_PORT="$page_port"
PROJECT="$project"
LOG="$log"

deadline=\$(( \$(date +%s) + 28800 ))
failures=0
page_failures=0

while [ "\$(date +%s)" -lt "\$deadline" ]; do
    sleep 10

    if curl -sf -m 8 "http://127.0.0.1:\$PORT" >/dev/null 2>&1; then
        failures=0
    else
        failures=\$((failures + 1))
        if [ "\$failures" -ge 3 ]; then
            ( cd "\$PROJECT" && "\$OPENCODE" service restart ) >> "\$LOG" 2>&1
            echo "\$(date -u +%Y-%m-%dT%H:%M:%SZ) watchdog restarted the classroom service" >> "\$LOG"
            failures=0
        fi
    fi

    if curl -sf -m 8 "http://127.0.0.1:\$PAGE_PORT" >/dev/null 2>&1; then
        page_failures=0
    else
        page_failures=\$((page_failures + 1))
        if [ "\$page_failures" -ge 3 ]; then
            ( cd "\$PROJECT" && nohup "\$PYTHON" serve_workshop.py --port "\$PAGE_PORT" --no-browser >> "\$LOG" 2>&1 & )
            echo "\$(date -u +%Y-%m-%dT%H:%M:%SZ) watchdog restarted the workshop page" >> "\$LOG"
            page_failures=0
        fi
    fi
done
WATCHDOG

    chmod +x "$watchdog_script"

    # Only one watchdog: replace any leftover from an earlier run.
    if [ -f "$WATCHDOG_PID_FILE" ]; then
        old_watchdog="$(cat "$WATCHDOG_PID_FILE" 2>/dev/null)"
        if [ -n "$old_watchdog" ] && kill -0 "$old_watchdog" 2>/dev/null; then
            kill "$old_watchdog" 2>/dev/null || true
        fi
    fi

    nohup "$watchdog_script" >> "$LATEST_LOG" 2>&1 &
    echo "$!" > "$WATCHDOG_PID_FILE"

    ok "Watchdog running (keeps both classroom pages alive for the next 8 hours)"
}

# ============================================================
# Main flow
# ============================================================

ensure_credential
ensure_python
ensure_node
ensure_opencode

write_classroom_config
cd "$PROJECT_ROOT" || die "The workshop folder could not be accessed: $PROJECT_ROOT"

test_provider

get_web_password
OPENCODE_PORT="$(find_free_port "$PREFERRED_OPENCODE_PORT" "$LAST_OPENCODE_PORT")" \
    || die "No free port for the OpenCode Web UI."

start_service "$OPENCODE_PORT" "$WEB_PASSWORD"

OPENCODE_URL="http://127.0.0.1:$OPENCODE_PORT"
PAIRED=0
open_pairing "$OPENCODE_URL"

section "Starting the workshop web page (React UI + workshop server)"
PAGE_PORT="$(find_free_port "$PREFERRED_PAGE_PORT" "$LAST_PAGE_PORT")" \
    || die "No free port for the workshop page."

if [ ! -f "$PROJECT_ROOT/serve_workshop.py" ]; then
    die "serve_workshop.py is missing from the workshop folder."
fi

if ! ( cd "$PROJECT_ROOT" && "$CLASS_PYTHON" serve_workshop.py --port "$PAGE_PORT" --no-browser ); then
    die "serve_workshop.py could not start the workshop page."
fi

PAGE_OK=0
for _ in $(seq 1 10); do
    if [ "$(curl -s -o /dev/null -w '%{http_code}' -m 5 "http://127.0.0.1:$PAGE_PORT/api/health" 2>/dev/null)" = "200" ]; then
        PAGE_OK=1
        break
    fi
    sleep 1
done

if [ "$PAGE_OK" -eq 1 ]; then
    ok "Workshop page ready at http://127.0.0.1:$PAGE_PORT"
    open "http://127.0.0.1:$PAGE_PORT" 2>/dev/null || true
else
    warn "Workshop page did not answer on port $PAGE_PORT."
fi

printf '\n%s==============================================%s\n' "$C_GREEN" "$C_RESET"
printf '%s              READY TO VIBE CODE              %s\n' "$C_GREEN" "$C_RESET"
printf '%s==============================================%s\n\n' "$C_GREEN" "$C_RESET"
printf 'OpenCode:      %s\n' "$OPENCODE_URL"
[ "$PAGE_OK" -eq 1 ] && printf 'Workshop page: http://127.0.0.1:%s\n' "$PAGE_PORT"
printf 'Model:         %s\n' "$OPENROUTER_MODEL_REF"
printf 'Python:        %s\n' "$("$CLASS_PYTHON" --version)"
printf 'Node:          %s\n\n' "$("$NODE_BIN" --version)"

if [ "$PAIRED" -eq 1 ]; then
    printf '%sThe browser should already be signed in.%s\n' "$C_GREEN" "$C_RESET"
else
    printf '%sBrowser pairing could not be automated -- sign in with:%s\n' "$C_YELLOW" "$C_RESET"
    printf '  Username: %s\n' "$OPENCODE_USERNAME"
    printf '  Password: %s\n' "$WEB_PASSWORD"
fi

printf '\nIf a page keeps loading:\n'
printf '  1. Refresh the browser, or open: %s\n' "$OPENCODE_URL"
printf '  2. Username: %s   Password: %s\n' "$OPENCODE_USERNAME" "$WEB_PASSWORD"
printf '  3. A hidden watchdog restarts both servers automatically if they stop answering.\n'

start_watchdog "$OPENCODE_BIN" "$OPENCODE_PORT" "$CLASS_PYTHON" "$PAGE_PORT" \
    "$PROJECT_ROOT" "$LATEST_LOG"

cp -f "$LOG_FILE" "$LATEST_LOG" 2>/dev/null || true

printf '\nSupport log:\n  %s\n\n' "$LOG_FILE"
printf 'It is safe to close this window.\n'
printf 'Press ENTER to close this window (read the notes above first).\n'
tty_read ""

exit 0

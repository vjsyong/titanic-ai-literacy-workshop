#!/usr/bin/env python3
"""serve_workshop.py -- Start (or reopen) the workshop's Gradio web page.

WHAT IT DOES
    1. Finds a Python interpreter that has the workshop packages
       (gradio) available.
    2. Reuses an already-running workshop page if one is answering.
    3. Otherwise starts `gradio 04_classroom.py` on the first free port
       in the classroom range (4097-4197).
    4. Waits until the page really answers, opens the browser, and
       exits. The server keeps running in the background.

WHY THE `gradio` CLI
    `gradio 04_classroom.py` runs the page with hot reload: every time
    the AI Teaching Assistant saves a workshop file, the already-open
    page refreshes by itself. That is the classroom magic -- never
    replace it with a plain `python 04_classroom.py` in the launcher.

USAGE
    python serve_workshop.py [--port N] [--no-browser] [--foreground]
                             [--python PATH]

    deployment/START WORKSHOP PAGE.bat calls this script for students:
    double-click it and the page opens in the browser.

    Students use Windows; the script also runs on macOS/Linux so the
    instructor can test outside the classroom deployment.
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLASSROOM = HERE / "04_classroom.py"
LOG_DIR = HERE / ".gradio"
LOG_FILE = LOG_DIR / "workshop-page.log"

# The classroom deployment reserves this range for the workshop page
# (the OpenCode Web UI uses 4096).
PREFERRED_PORT = 4097
LAST_PORT = 4197

# A cold start imports pandas + matplotlib + scikit-learn + gradio,
# which can be slow on classroom machines.
READY_TIMEOUT = 120.0
READY_POLL = 1.0

# A live workshop page always contains this in its root HTML.
PAGE_MARKER = "gradio"

# Proxy-free opener: a campus proxy must never intercept localhost.
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

# Keep detached server log handles alive for the lifetime of this process.
_OPEN_HANDLES = []


def _say(message=""):
    print(message, flush=True)


def _candidate_pythons(explicit):
    if explicit:
        return [Path(explicit)]

    candidates = []

    # The classroom environment created by deployment/START VIBE CODING.bat.
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            candidates.append(
                Path(local_app_data) / "VibeCoding" / "python" / "Scripts" / "python.exe"
            )

    # A project virtual environment (used for instructor testing).
    candidates.append(HERE / ".venv" / "Scripts" / "python.exe")
    candidates.append(HERE / ".venv" / "bin" / "python")

    # Whatever launched this script (e.g. the classroom venv via the .bat).
    candidates.append(Path(sys.executable))

    unique = []
    for candidate in candidates:
        if candidate.exists() and candidate not in unique:
            unique.append(candidate)
    return unique


def _port_is_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def _page_is_live(port, timeout=1.5):
    try:
        with _OPENER.open(f"http://127.0.0.1:{port}/", timeout=timeout) as response:
            if response.status != 200:
                return False
            body = response.read(65536).decode("utf-8", "replace").lower()
            return PAGE_MARKER in body
    except OSError:
        return False


def _ensure_loopback_no_proxy(environment):
    required = ["localhost", "127.0.0.1", "::1"]
    current = [
        item.strip()
        for item in environment.get("NO_PROXY", "").split(",")
        if item.strip()
    ]
    for item in required:
        if item not in current:
            current.append(item)
    environment["NO_PROXY"] = ",".join(current)
    environment["no_proxy"] = environment["NO_PROXY"]


def _log_tail(line_count=15):
    try:
        lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    return "\n".join(lines[-line_count:])


def _server_environment(port):
    environment = os.environ.copy()
    environment["GRADIO_SERVER_PORT"] = str(port)
    environment["GRADIO_SERVER_NAME"] = "127.0.0.1"
    environment["GRADIO_ANALYTICS_ENABLED"] = "False"
    environment["PYTHONUNBUFFERED"] = "1"
    _ensure_loopback_no_proxy(environment)
    return environment


def _server_command(python):
    return [str(python), "-m", "gradio", str(CLASSROOM)]


def _start_server(python, port):
    environment = _server_environment(port)
    command = _server_command(python)

    LOG_DIR.mkdir(exist_ok=True)
    log_handle = open(LOG_FILE, "a", encoding="utf-8", errors="replace")
    _OPEN_HANDLES.append(log_handle)
    log_handle.write(
        f"\n===== {time.strftime('%Y-%m-%d %H:%M:%S')} "
        f"starting workshop page on port {port} =====\n"
    )
    log_handle.flush()

    creation_flags = 0
    if os.name == "nt":
        creation_flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0
        )

    return subprocess.Popen(
        command,
        cwd=str(HERE),
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        creationflags=creation_flags,
        start_new_session=(os.name != "nt"),
    )


def _run_foreground(python, port, open_browser):
    environment = _server_environment(port)
    command = _server_command(python)
    _say(f"Running (Ctrl+C stops the page): {' '.join(command)}")

    process = subprocess.Popen(command, cwd=str(HERE), env=environment)

    def announce_when_ready():
        deadline = time.monotonic() + READY_TIMEOUT
        while time.monotonic() < deadline and process.poll() is None:
            if _page_is_live(port):
                url = f"http://127.0.0.1:{port}"
                if open_browser:
                    webbrowser.open(url)
                _announce(url, python, already_running=False)
                return
            time.sleep(READY_POLL)

    threading.Thread(target=announce_when_ready, daemon=True).start()

    try:
        return process.wait()
    except KeyboardInterrupt:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        return 0


def _wait_for_page(process, port, timeout=READY_TIMEOUT):
    deadline = time.monotonic() + timeout
    announced = False

    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False, "exited"
        if _page_is_live(port):
            return True, "ready"
        if not announced:
            _say("Waiting for the workshop page to come up...")
            announced = True
        time.sleep(READY_POLL)

    return False, "timeout"


def _print_server_failure():
    tail = _log_tail()
    if tail:
        _say("Last server log lines:")
        _say(tail)


def _announce(url, python, already_running):
    _say()
    _say("Titanic AI Literacy Workshop web page is running:")
    _say(f"    {url}")
    _say(f"    (served by {python})")
    _say()
    _say("The page hot-reloads: every time a workshop file is saved, the")
    _say("already-open page refreshes by itself.")
    if not already_running:
        _say()
        _say(f"Server log: {LOG_FILE}")


def _choose_port(requested):
    if requested is not None:
        if _port_is_free(requested):
            return requested
        _say(f"ERROR: port {requested} is already in use by another program.")
        _say(f"Try another one, for example:  --port {requested + 1}")
        return None

    for port in range(PREFERRED_PORT, LAST_PORT + 1):
        if _port_is_free(port):
            return port

    _say(f"ERROR: no free port between {PREFERRED_PORT} and {LAST_PORT}.")
    return None


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Start (or reopen) the workshop's Gradio web page."
    )
    parser.add_argument("--port", type=int, help="port for the page (default 4097)")
    parser.add_argument(
        "--no-browser", action="store_true", help="do not open the browser"
    )
    parser.add_argument(
        "--foreground",
        action="store_true",
        help="keep the server attached to this terminal (Ctrl+C stops it)",
    )
    parser.add_argument(
        "--python",
        help="Python interpreter to use (skips automatic discovery)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)

    if not CLASSROOM.exists():
        _say(f"ERROR: {CLASSROOM.name} was not found next to this script.")
        _say("Run this script from inside the workshop folder.")
        return 1

    requested_port = args.port
    if requested_port is None:
        environment_port = os.environ.get("GRADIO_SERVER_PORT", "").strip()
        if environment_port:
            try:
                requested_port = int(environment_port)
            except ValueError:
                pass

    # 1. Reuse a page that is already answering (launcher-started or ours).
    ports_to_probe = (
        [requested_port]
        if requested_port is not None
        else range(PREFERRED_PORT, LAST_PORT + 1)
    )
    for port in ports_to_probe:
        if _page_is_live(port):
            url = f"http://127.0.0.1:{port}"
            if not args.no_browser:
                webbrowser.open(url)
            _announce(url, "an already-running server", already_running=True)
            return 0

    # 2. Choose a port for a fresh server.
    port = _choose_port(requested_port)
    if port is None:
        return 1

    # 3. Try each known interpreter until one can actually serve.
    pythons = _candidate_pythons(args.python)
    if not pythons:
        _say("ERROR: no Python interpreter was found for the workshop page.")
        return 1

    for python in pythons:
        if args.foreground:
            return _run_foreground(python, port, not args.no_browser)

        _say(f"Starting the workshop page on port {port} with {python} ...")
        try:
            process = _start_server(python, port)
        except OSError as error:
            _say(f"Could not run that interpreter: {error}")
            continue

        ready, reason = _wait_for_page(process, port)

        if ready:
            url = f"http://127.0.0.1:{port}"
            if not args.no_browser:
                webbrowser.open(url)
            _announce(url, python, already_running=False)
            return 0

        if reason == "timeout":
            process.terminate()
            _say(f"ERROR: the page did not answer within {int(READY_TIMEOUT)}s.")
            _print_server_failure()
            _say()
            _say("Run deployment/REPAIR VIBE CODING.bat, then try again.")
            return 1

        # The interpreter exited: usually a missing package. Try the next.
        _say("That interpreter could not serve the page; trying the next one...")

    _say("ERROR: could not start the workshop page.")
    _print_server_failure()
    _say()
    _say("Run deployment/START VIBE CODING.bat (first time) or")
    _say("deployment/REPAIR VIBE CODING.bat, then try again.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

"""workshop_server.py -- Workshop web page server (INSTRUCTOR MANAGED)

WHAT THIS FILE IS
    A small FastAPI server that:

        1. imports the three workshop scripts (01_eda.py, 02_train.py,
           03_dashboard.py),
        2. describes their checkpoint state (which gates are done and
           what each finished gate produced),
        3. serves the React web page built in web/dist,
        4. watches the workshop files and pushes fresh state to every
           open browser the moment a gate is saved -- the classroom magic.

    The page runs at http://127.0.0.1:4097 (classroom default).

HOW THE AUTO-REFRESH WORKS
    Every half second the server compares workshop file timestamps. When
    the AI Teaching Assistant implements a gate and bumps
    STEPS_COMPLETED, the server re-imports the scripts, recomputes the
    finished gates and sends a Server-Sent Event with the new state. If a
    script has a syntax error mid-edit, the last good page stays up and
    an error banner explains what happened.

WHO MAY EDIT THIS FILE
    Instructors only -- students and their AI assistants never touch it.

HOW TO RUN
    python serve_workshop.py     classroom launcher (free port, opens the
                                 browser, keeps the server in the
                                 background)
    python workshop_server.py    plain foreground server (instructor/dev)
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import importlib.util
import inspect
import json
import math
import threading
import time
import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

import workshop_steps

HERE = Path(__file__).resolve().parent
WEB_DIST = HERE / "web" / "dist"
PERSONAS_JSON = HERE / "personas.json"
PERSONAS_DIR = HERE / "personas"

# How often the watcher checks for saved workshop files.
REFRESH_INTERVAL = 0.5

# Hardening guards for student-written gate code. A runaway checkpoint must
# never freeze the shared classroom page or the watcher loop.
GATE_TIMEOUT_SECONDS = 20.0
PREDICT_TIMEOUT_SECONDS = 10.0
MAX_RESULT_BYTES = 1_500_000
MAX_PREDICT_BODY_BYTES = 64 * 1024

SCRIPTS = [
    {"id": "eda", "file": "01_eda.py", "module_name": "workshop_step_01_eda", "connect": True},
    {"id": "train", "file": "02_train.py", "module_name": "workshop_step_02_train"},
    {"id": "dashboard", "file": "03_dashboard.py", "module_name": "workshop_step_03_dashboard"},
]

# The three step scripts plus the shared machinery they import.
WATCHED_FILES = [HERE / script["file"] for script in SCRIPTS] + [HERE / "workshop_steps.py"]

_NO_BUILD_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>Workshop page not built</title></head>
<body style="font-family: system-ui; max-width: 40rem; margin: 4rem auto; color: #1e293b">
<h1>Workshop page is not built yet</h1>
<p>The server is running, but <code>web/dist</code> is missing.</p>
<p>Instructor: build it once with</p>
<pre style="background:#f1f5f9; padding:1rem; border-radius:.75rem">cd web
npm install
npm run build</pre>
<p>then refresh this page.</p>
</body></html>"""

_lock = threading.Lock()
_condition = threading.Condition()
_state = {
    "version": "starting",
    "all_complete": False,
    "scripts": [],
    "dashboard": {"input_spec": None, "predict_ready": False, "complete": False},
    "import_errors": {},
}
_modules = {}
_signature = None


class _Timeout(Exception):
    """Raised when a student-written gate function runs too long."""


_running_lock = threading.Lock()
_running = {}


def _run_with_timeout(key, fn, timeout):
    """Run fn with a hard time budget so infinite loops cannot hang the page.

    The worker runs in a daemon thread; if it is still alive after timeout we
    report a friendly error and remember it, so later refreshes do not pile
    up more threads while the old one is still stuck.
    """
    with _running_lock:
        active = _running.get(key)
        if active is not None and active.is_alive():
            raise _Timeout(
                "a previous run of this checkpoint is still stuck -- "
                "simplify the code (look for an infinite loop)"
            )

    box = {}

    def runner():
        try:
            box["value"] = fn()
        except BaseException as exc:  # noqa: BLE001 - re-raised by the caller
            box["error"] = exc

    thread = threading.Thread(target=runner, daemon=True, name=f"gate:{key}")
    with _running_lock:
        _running[key] = thread

    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        raise _Timeout(
            f"took longer than {int(timeout)} seconds and was stopped -- "
            "look for an infinite loop or very heavy work"
        )

    with _running_lock:
        _running.pop(key, None)

    if "error" in box:
        error = box["error"]
        if isinstance(error, Exception):
            raise error
        # SystemExit / KeyboardInterrupt from student code must not kill
        # the watcher thread -- report it like any other gate error.
        raise RuntimeError(
            f"checkpoint code tried to exit ({type(error).__name__})"
        )
    return box.get("value")


def _safe_result(fn, key):
    """Run a gate function and keep the serialized result classroom-sized."""
    result = workshop_steps.serialize_result(
        _run_with_timeout(key, fn, GATE_TIMEOUT_SECONDS)
    )
    if result is None:
        return None
    try:
        encoded = json.dumps(result, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return {
            "blocks": [
                {
                    "type": "markdown",
                    "text": "This checkpoint produced output that could not be displayed.",
                }
            ]
        }
    if len(encoded) > MAX_RESULT_BYTES:
        return {
            "blocks": [
                {
                    "type": "markdown",
                    "text": (
                        "This checkpoint produced far too much output for the "
                        "classroom page. Ask your AI Teaching Assistant to show "
                        "a smaller summary instead."
                    ),
                }
            ]
        }
    return result


def _sanitize_values(values):
    """Only plain scalar form values may reach student-written predict code."""
    if not isinstance(values, dict) or len(values) > 30:
        return None
    clean = {}
    for key, value in values.items():
        if not isinstance(key, str) or len(key) > 80:
            return None
        if value is None or isinstance(value, bool):
            clean[key] = value
        elif isinstance(value, (int, float)):
            if isinstance(value, float) and not math.isfinite(value):
                return None
            clean[key] = value
        elif isinstance(value, str):
            if len(value) > 200:
                return None
            clean[key] = value
        else:
            return None
    return clean


# ---------------------------------------------------------------------------
# Script importing / state building
# ---------------------------------------------------------------------------

def _import_script(script):
    path = HERE / script["file"]
    spec = importlib.util.spec_from_file_location(script["module_name"], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _empty_script_state(script):
    return {
        "id": script["id"],
        "title": script["id"],
        "intro": "",
        "completed": 0,
        "total": 0,
        "steps": [],
    }


# Cap for the gate source shown in the "See the code" panel.
MAX_CODE_CHARS = 8000


def _without_docstring(source):
    """Drop a leading function docstring so students see only real code."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    if not tree.body or not isinstance(
        tree.body[0], (ast.FunctionDef, ast.AsyncFunctionDef)
    ):
        return source
    body = getattr(tree.body[0], "body", [])
    first = body[0] if body else None
    if not (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    ):
        return source
    lines = source.splitlines(keepends=True)
    start = first.lineno - 1
    end = first.end_lineno or first.lineno
    return "".join(lines[:start] + lines[end:])


def _step_code(module, step):
    """Source of a gate function, or None while it is still a stub."""
    fn = getattr(module, str(step.get("fn", "")), None)
    if fn is None or not callable(fn):
        return None
    try:
        source = inspect.getsource(fn).rstrip()
    except (OSError, TypeError):
        return None
    if not source or "raise NotImplementedError" in source:
        return None
    source = _without_docstring(source)
    if len(source) > MAX_CODE_CHARS:
        source = source[:MAX_CODE_CHARS] + "\n# ... (trimmed for the classroom page)"
    return source


def _describe_script(script, module):
    page = getattr(module, "PAGE", None) or {}
    steps = list(getattr(module, "STEPS", None) or [])
    completed = int(getattr(module, "STEPS_COMPLETED", 0) or 0)

    # Step 0 handshake: only scripts flagged `connect` get it. It is driven
    # by a module flag the AI assistant sets when it first reaches the
    # project, so Checkpoint 1 stays locked until the handshake is proven.
    connect_spec = None
    connected = True
    if script.get("connect"):
        connect_spec = getattr(workshop_steps, "CONNECT_STEP", None)
        flag = getattr(workshop_steps, "CONNECT_FLAG", "")
        if connect_spec is not None and flag:
            connected = bool(getattr(module, flag, False))

    described = []

    if connect_spec is not None:
        described.append(
            {
                "number": int(connect_spec.get("number", 0)),
                "title": str(connect_spec.get("title", "Connect your assistant")),
                "story": str(connect_spec.get("story", "")),
                "prompt": str(connect_spec.get("prompt", "")),
                "hints": [str(hint) for hint in (connect_spec.get("hints") or [])],
                "placeholder": str(connect_spec.get("placeholder", "")),
                "guide": str(connect_spec.get("guide", "")),
                "experiment": str(connect_spec.get("experiment", "")),
                "context": workshop_steps.serialize_result(connect_spec.get("context")),
                "reference": str(connect_spec.get("reference", "")),
                "reference_alt": str(connect_spec.get("reference_alt", "")),
                "status": "done" if connected else "current",
                "result": (
                    workshop_steps.serialize_result(connect_spec.get("guide", ""))
                    if connected
                    else None
                ),
                "error": None,
                "code": None,
            }
        )

    for index, step in enumerate(steps):
        number = int(step.get("number", index + 1))
        entry = {
            "number": number,
            "title": str(step.get("title", f"Step {number}")),
            "story": str(step.get("story", "")),
            "prompt": str(step.get("prompt", "")),
            "hints": [str(hint) for hint in (step.get("hints") or [])],
            "placeholder": str(step.get("placeholder", "")),
            "guide": str(step.get("guide", "")),
            "experiment": str(step.get("experiment", "")),
            "context": workshop_steps.serialize_result(step.get("context")),
            "reference": str(step.get("reference", "")),
            "reference_alt": str(step.get("reference_alt", "")),
            "status": "locked",
            "result": None,
            "error": None,
            "code": _step_code(module, step),
        }
        if connect_spec is not None and not connected:
            entry["status"] = "locked"
        elif number <= completed:
            entry["status"] = "done"
            fn = getattr(module, str(step.get("fn", "")), None)
            if fn is None:
                entry["error"] = f"step function {step.get('fn')!r} is missing"
            else:
                try:
                    entry["result"] = _safe_result(
                        fn, f"{script['id']}:{number}"
                    )
                except NotImplementedError as exc:
                    entry["error"] = f"not ready: {exc}"
                except _Timeout as exc:
                    entry["error"] = (
                        f"checkpoint stopped: {exc}. Ask the AI Teaching "
                        "Assistant to simplify this gate's code."
                    )
                except Exception as exc:
                    entry["error"] = f"{type(exc).__name__}: {exc}"
        elif number == completed + 1:
            entry["status"] = "current"
        described.append(entry)

    if connect_spec is None:
        shown_completed = completed
    elif connected:
        shown_completed = completed + 1
    else:
        shown_completed = 0

    return {
        "id": script["id"],
        "title": str(page.get("title", script["id"])),
        "intro": str(page.get("intro", "")),
        "completed": shown_completed,
        "total": len(described),
        "steps": described,
    }


def _describe_dashboard(module):
    info = {"input_spec": None, "predict_ready": False, "complete": False}
    if module is None:
        return info

    artifacts = getattr(module, "ARTIFACTS", None) or {}
    spec = artifacts.get("input_spec")
    if spec is not None:
        info["input_spec"] = workshop_steps.json_ready(spec)
    info["predict_ready"] = callable(artifacts.get("predict"))

    steps = getattr(module, "STEPS", None) or []
    completed = int(getattr(module, "STEPS_COMPLETED", 0) or 0)
    info["complete"] = bool(steps) and completed >= len(steps)
    return info


def _compute_signature():
    parts = []
    for path in WATCHED_FILES:
        try:
            stat = path.stat()
            parts.append(f"{path.name}:{stat.st_mtime_ns}:{stat.st_size}")
        except OSError:
            parts.append(f"{path.name}:missing")
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]


def _refresh(signature, notify=True):
    global _state, _modules, _signature

    # The shared helpers may have changed too (instructor edits).
    try:
        importlib.reload(workshop_steps)
    except Exception:
        traceback.print_exc()

    with _lock:
        previous = {entry["id"]: entry for entry in _state.get("scripts", [])}

    script_states = []
    modules = {}
    import_errors = {}

    for script in SCRIPTS:
        try:
            module = _import_script(script)
        except Exception:
            error = traceback.format_exc(limit=8)
            import_errors[script["id"]] = error
            modules[script["id"]] = None
            script_states.append(previous.get(script["id"]) or _empty_script_state(script))
            print(f"[workshop] {script['file']} could not be loaded:")
            print(error)
            continue

        modules[script["id"]] = module
        import_errors[script["id"]] = None
        script_states.append(_describe_script(script, module))

    dashboard = _describe_dashboard(modules.get("dashboard"))
    all_complete = all(
        state["total"] > 0 and state["completed"] >= state["total"]
        for state in script_states
    )

    new_state = {
        "version": signature,
        "all_complete": all_complete,
        "scripts": script_states,
        "dashboard": dashboard,
        "import_errors": import_errors,
    }

    with _lock:
        _state = new_state
        _modules = modules
        _signature = signature

    if notify:
        with _condition:
            _condition.notify_all()

    if notify:
        print(f"[workshop] page updated (version {signature})")


def _watch_loop():
    while True:
        time.sleep(REFRESH_INTERVAL)
        signature = _compute_signature()
        with _lock:
            current = _signature
        if signature == current:
            continue
        try:
            _refresh(signature)
        except Exception:
            traceback.print_exc()


# ---------------------------------------------------------------------------
# HTTP API
# ---------------------------------------------------------------------------

app = FastAPI(title="Titanic AI Literacy Workshop", docs_url=None, redoc_url=None)


@app.middleware("http")
async def limit_request_body(request, call_next):
    """Refuse oversized POSTs before they reach any student-written code."""
    if request.method == "POST":
        raw_length = request.headers.get("content-length")
        if raw_length is not None:
            try:
                if int(raw_length) > MAX_PREDICT_BODY_BYTES:
                    return JSONResponse(
                        {"ok": False, "error": "Request too large."},
                        status_code=413,
                    )
            except ValueError:
                return JSONResponse(
                    {"ok": False, "error": "Invalid Content-Length."},
                    status_code=400,
                )
    return await call_next(request)


@app.get("/api/health")
def health():
    with _lock:
        version = _state.get("version")
    return {"app": "titanic-workshop", "ok": True, "version": version}


@app.get("/api/state")
def get_state():
    with _lock:
        return _state


@app.get("/api/events")
def events():
    def stream():
        last_version = None
        while True:
            with _lock:
                state = _state
            if state["version"] != last_version:
                last_version = state["version"]
                yield f"data: {json.dumps(state, ensure_ascii=False)}\n\n"
            with _condition:
                changed = _condition.wait(timeout=15)
            if not changed:
                yield ": keep-alive\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/predict")
def predict(payload: dict):
    values = _sanitize_values((payload or {}).get("values"))

    if values is None:
        return {
            "ok": False,
            "error": "Those form values did not look right. Please reset the form and try again.",
        }

    with _lock:
        module = _modules.get("dashboard")

    if module is None:
        return {"ok": False, "error": "Step 3 is not available right now."}

    predict_fn = (getattr(module, "ARTIFACTS", None) or {}).get("predict")
    if not callable(predict_fn):
        return {
            "ok": False,
            "error": (
                "The prediction form is not wired yet -- "
                "finish Step 3, checkpoint 3 first."
            ),
        }

    try:
        raw = _run_with_timeout(
            "predict", lambda: predict_fn(values), PREDICT_TIMEOUT_SECONDS
        )
    except _Timeout as exc:
        return {
            "ok": False,
            "error": (
                f"The prediction code was stopped: {exc}. "
                "Ask your AI Teaching Assistant to simplify it."
            ),
        }
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    if isinstance(raw, dict):
        text = str(raw.get("text") or raw.get("verdict") or "")
        return {
            "ok": True,
            "text": text[:2000],
            "probability": workshop_steps.json_ready(raw.get("probability")),
            "band": workshop_steps.json_ready(raw.get("band")),
        }
    return {"ok": True, "text": str(raw)[:2000], "probability": None, "band": None}


@app.get("/api/personas")
def get_personas():
    """Serve the quiz roster (personas.json) for the front-page game."""
    try:
        return json.loads(PERSONAS_JSON.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"personas": [], "error": "personas.json is missing or invalid"}


# The portrait images live in the repo-root `personas/` folder so instructors
# keep a single editable copy. Mounted before the web-dist catch-all so
# `/personas/M1.jpg` resolves to the image, not the React app.
if PERSONAS_DIR.is_dir():
    app.mount("/personas", StaticFiles(directory=str(PERSONAS_DIR)), name="personas")


# The API routes are registered above; the static mount catches the rest.
if WEB_DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(WEB_DIST), html=True), name="web")
else:

    @app.get("/")
    def missing_build():
        return HTMLResponse(_NO_BUILD_HTML, status_code=503)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description="Serve the workshop web page.")
    parser.add_argument("--port", type=int, default=4097, help="port (default 4097)")
    parser.add_argument("--host", default="127.0.0.1", help="bind address")
    args = parser.parse_args(argv)

    signature = _compute_signature()
    _refresh(signature, notify=False)

    if not WEB_DIST.is_dir():
        print("[workshop] WARNING: web/dist is missing -- build it with:")
        print("           cd web && npm install && npm run build")

    print(f"[workshop] page:  http://{args.host}:{args.port}")
    print("[workshop] watch: workshop files reload automatically")

    thread = threading.Thread(target=_watch_loop, daemon=True)
    thread.start()

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()

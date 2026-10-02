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
import hashlib
import importlib
import importlib.util
import json
import threading
import time
import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

import workshop_steps

HERE = Path(__file__).resolve().parent
WEB_DIST = HERE / "web" / "dist"

# How often the watcher checks for saved workshop files.
REFRESH_INTERVAL = 0.5

SCRIPTS = [
    {"id": "eda", "file": "01_eda.py", "module_name": "workshop_step_01_eda"},
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


def _describe_script(script, module):
    page = getattr(module, "PAGE", None) or {}
    steps = list(getattr(module, "STEPS", None) or [])
    completed = int(getattr(module, "STEPS_COMPLETED", 0) or 0)

    described = []
    for index, step in enumerate(steps):
        number = int(step.get("number", index + 1))
        entry = {
            "number": number,
            "title": str(step.get("title", f"Step {number}")),
            "story": str(step.get("story", "")),
            "prompt": str(step.get("prompt", "")),
            "reference": str(step.get("reference", "")),
            "status": "locked",
            "result": None,
            "error": None,
        }
        if number <= completed:
            entry["status"] = "done"
            fn = getattr(module, str(step.get("fn", "")), None)
            if fn is None:
                entry["error"] = f"step function {step.get('fn')!r} is missing"
            else:
                try:
                    entry["result"] = workshop_steps.serialize_result(fn())
                except NotImplementedError as exc:
                    entry["error"] = f"not ready: {exc}"
                except Exception as exc:
                    entry["error"] = f"{type(exc).__name__}: {exc}"
        elif number == completed + 1:
            entry["status"] = "current"
        described.append(entry)

    return {
        "id": script["id"],
        "title": str(page.get("title", script["id"])),
        "intro": str(page.get("intro", "")),
        "completed": completed,
        "total": len(steps),
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
    values = (payload or {}).get("values") or {}

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
        raw = predict_fn(values)
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    if isinstance(raw, dict):
        return {
            "ok": True,
            "text": str(raw.get("text") or raw.get("verdict") or ""),
            "probability": workshop_steps.json_ready(raw.get("probability")),
            "band": workshop_steps.json_ready(raw.get("band")),
        }
    return {"ok": True, "text": str(raw), "probability": None, "band": None}


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

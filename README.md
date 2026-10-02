# Titanic AI Literacy Workshop

A 75-minute Year 1 AI workshop for students with zero programming experience,
bundled with a one-click OpenCode classroom environment. **Everything happens
in the browser**: the workshop scripts feed a custom React UI (Vite + ECharts)
served by a small FastAPI process, in one classroom page.

## What's in this repo

| Path | Purpose |
|---|---|
| `01_eda.py` | Step 1 - Meet the Data: **6 checkpoint gates** (list, holes, survival, sex/class charts, age) |
| `02_train.py` | Step 2 - Train the Model: **7 checkpoint gates** (encode -> save model) |
| `03_dashboard.py` | Step 3 - Survival Explorer: **5 checkpoint gates**, live form appears at gate 3 |
| `workshop_server.py` | Instructor-managed FastAPI server: checkpoint state, SSE auto-refresh, prediction endpoint, serves `web/dist` |
| `serve_workshop.py` | Instructor-managed launcher: free port, background server, browser, reuse of a running page |
| `workshop_steps.py` | Instructor-managed shared machinery: result serialization + `chart()` / `metric()` / `verdict()` helpers |
| `web/` | The React + TypeScript + Tailwind UI (ECharts charts); `web/dist` is committed so students never need Node. Styled on the mail-triage design system (self-hosted Geist fonts in `web/public/fonts`) |
| `data/titanic.csv` | The cleaned 1912 passenger list students use |
| `AGENTS.md` | Persistent system prompt for the students' AI Teaching Assistant |
| `deployment/` | One-click OpenCode classroom environment (OpenCode 2.0.20, OpenRouter xiaomi/mimo-v2.6-flash only) |

## How the class works (checkpoint flow)

1. **Once**: the launcher serves the workshop page automatically
   (`deployment/START VIBE CODING.bat` starts it on port 4097 and a hidden
   watchdog keeps it alive). To (re)start it by hand:
   `python serve_workshop.py`.
   Students see one page, three tabs; each tab shows its next checkpoint as a
   prompt-hint card, locked steps stay greyed out.
2. **Loop (the magic)**: each checkpoint card shows a *mission* (direction and
   goal, not a ready-made prompt) plus a box for the student's own request.
   Once they write a meaningful attempt (6+ words), the reference prompt
   unlocks so they can compare it with theirs or copy it. The AI Teaching
   Assistant implements **exactly one gate**, verifies it in the terminal,
   bumps the script's `STEPS_COMPLETED`, saves the file. The server notices
   within a second: the open page refreshes itself, the finished checkpoint
   becomes an animated result card (tables, interactive charts, gauges), and
   the NEXT mission appears. Repeat until all 18 checkpoints are done.

## Instructor development

Backend and UI are separate for a fast dev loop:

```
python workshop_server.py          # API + state on 127.0.0.1:4097
cd web && npm install && npm run dev   # Vite on :5173 with HMR, proxies /api
```

Production-like run (serves the built UI from `web/dist`):

```
python serve_workshop.py --no-browser
```

**After changing the UI, rebuild the committed bundle:** `cd web && npm run build`.

The `demo` branch holds the full reference implementation (all 18 gates
implemented with the fancy payloads) matching the student scaffolds.

## Instructor testing / student quick start (Windows)

1. Get the workshop folder (ZIP from the instructor).
2. Double-click:
   ```
   deployment/START VIBE CODING.bat
   ```
   First run only: private Python 3.12 + Node.js + OpenCode 2.0.20 are
   installed under `%LOCALAPPDATA%\VibeCoding` and workshop packages
   (pandas / scikit-learn / fastapi / uvicorn) are pip-installed.
3. The browser opens the OpenCode Web UI pointed at the workshop folder,
   and the workshop web page itself (http://127.0.0.1:4097).
4. Simply talk to the AI Teaching Assistant and watch the page evolve.
   If the workshop page ever stops, double-click:
   ```
   deployment/START WORKSHOP PAGE.bat
   ```

If the Web UI ever shows no project, use File -> Open Project and pick the
extracted workshop folder once.

Other launchers:

- `START WORKSHOP PAGE.bat` — (re)starts the workshop web page and opens it
  in the browser. Safe to run any time; it reuses a page that is already up.
- `REPAIR VIBE CODING.bat` — revalidates/rebuilds the classroom runtimes
  without touching student project files.
- `RESET WORKSHOP.bat` — restores the three workshop scripts to their
  original scaffolds and deletes generated artifacts, so the 18 checkpoints
  lock again. The classroom runtime, API key, and `data/titanic.csv` stay.
- `RESET VIBE CODING.bat` — removes only `%LOCALAPPDATA%\VibeCoding`
  and `%USERPROFILE%\.vibecoding`; system installs and student projects stay.

## Instructor checklist before class

1. Copy `deployment/KEY.txt.TEMPLATE` to `deployment/key.txt` and paste
   the OpenRouter API key (key only, no quotes, no "Bearer ";
   OpenRouter keys start with "sk-or-").
   - `key.txt` is gitignored so a real key can never be committed.
   - The launcher refuses to run with the placeholder still in place.
   - When distributing a ZIP, include `key.txt` — it is inside the zip,
     never in the git history.
2. Build the UI once (`cd web && npm run build`) so `web/dist` is current.
3. Optional: pre-bake big downloads into `deployment/payload/`
   (python-3.12.10 installer, node-v24.21.0 zip, SHASUMS256.txt) to reduce
   classroom Wi-Fi traffic — see `deployment/README-FIRST.txt`.
4. Keep the deployment folder next to the workshop files when zipping.

## Updating launcher files

`deployment/MANIFEST-SHA256.json` records SHA-256 + size for every
launcher file. If you modify a launcher (e.g. `oneclick.ps1`), regenerate
the manifest before creating a classroom ZIP.

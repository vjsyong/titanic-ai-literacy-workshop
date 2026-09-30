# Titanic AI Literacy Workshop

A 75-minute Year 1 AI workshop for students with zero programming experience,
bundled with a one-click OpenCode classroom environment. **Everything happens
in the browser**: the workshop scripts are paired with Gradio web interfaces,
combined into one classroom page.

## What's in this repo

| Path | Purpose |
|---|---|
| `01_eda.py` | Step 1 - Meet the Data: **6 checkpoint gates** (list, holes, survival, sex/class charts, age) |
| `02_train.py` | Step 2 - Train the Model: **7 checkpoint gates** (encode -> save model) |
| `03_dashboard.py` | Step 3 - Survival Explorer: **5 checkpoint gates**, live form appears at gate 3 |
| `04_classroom.py` | Instructor-managed one-page launcher: all three steps as browser tabs |
| `serve_workshop.py` | Instructor-managed helper that starts/reopens the workshop page (free port, browser, background) |
| `workshop_steps.py` | Instructor-managed shared checkpoint machinery (progress bar, locked steps, prompt hints) |
| `data/titanic.csv` | The cleaned 1912 passenger list students use |
| `AGENTS.md` | Persistent system prompt for the students' AI Teaching Assistant |
| `deployment/` | One-click OpenCode classroom environment (OpenCode 2.0.20, Tencent glm-5.3-flash only) |

## How the class works (checkpoint flow)

1. **Once**: the launcher serves the workshop page automatically
   (`deployment/START VIBE CODING.bat` starts it on port 4097 and a hidden
   watchdog keeps it alive). To (re)start it by hand:
   `python serve_workshop.py` or `gradio 04_classroom.py`.
   Students see one page, three tabs; each tab shows its next checkpoint as a
   prompt-hint card, locked steps stay greyed out.
2. **Loop (the magic)**: a student writes their intent (or copies the hint
   shown on the page, e.g. *"Check data/titanic.csv for missing values and
   show me a table of how many holes each column has"*). The AI Teaching
   Assistant implements **exactly one gate**, verifies it in the terminal,
   bumps the script's `STEPS_COMPLETED`, saves the file. Gradio hot-reloads:
   the page refreshes itself, the finished checkpoint becomes a result card,
   and the NEXT prompt hint appears. Repeat until all 18 checkpoints are done.

Instructor testing without OpenCode (must have Python packages installed):

```
python serve_workshop.py --no-browser
```

(or run the hot-reload server in the foreground: `gradio 04_classroom.py`)

The `demo` branch holds the full reference implementation (all gates
implemented end to end) matching the `main` scaffold's contracts.

## Instructor testing / student quick start (Windows)

1. Get the workshop folder (ZIP from the instructor).
2. Double-click:
   ```
   deployment/START VIBE CODING.bat
   ```
   First run only: private Python 3.12 + Node.js + OpenCode 2.0.20 are
   installed under `%LOCALAPPDATA%\VibeCoding` and workshop packages
   (pandas / matplotlib / scikit-learn / gradio) are pip-installed.
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
- `RESET VIBE CODING.bat` — removes only `%LOCALAPPDATA%\VibeCoding`
  and `%USERPROFILE%\.vibecoding`; system installs and student projects stay.

## Instructor checklist before class

1. Copy `deployment/KEY.txt.TEMPLATE` to `deployment/key.txt` and paste
   the Tencent Cloud MaaS key (key only, no quotes, no "Bearer ").
   - `key.txt` is gitignored so a real key can never be committed.
   - The launcher refuses to run with the placeholder still in place.
   - When distributing a ZIP, include `key.txt` — it is inside the zip,
     never in the git history.
2. Optional: pre-bake big downloads into `deployment/payload/`
   (python-3.12.10 installer, node-v24.21.0 zip, SHASUMS256.txt) to reduce
   classroom Wi-Fi traffic — see `deployment/README-FIRST.txt`.
3. Keep the deployment folder next to the workshop files when zipping.

## Updating launcher files

`deployment/MANIFEST-SHA256.json` records SHA-256 + size for every
launcher file. If you modify a launcher (e.g. `oneclick.ps1`), regenerate
the manifest before creating a classroom ZIP.

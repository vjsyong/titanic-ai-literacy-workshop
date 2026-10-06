# Titanic AI Literacy Workshop

A 75-minute Year 1 AI workshop for students with zero programming experience,
bundled with a one-click OpenCode classroom environment. **Everything happens
in the browser**: the workshop scripts feed a custom React UI (Vite + ECharts)
served by a small FastAPI process, in one classroom page.

## What's in this repo

| Path | Purpose |
|---|---|
| `01_eda.py` | Step 1 - Meet the Data: **3 checkpoint gates** (load + holes, survival + sex, class + age) |
| `02_train.py` | Step 2 - Train the Model: **4 checkpoint gates** (encode + features -> split + scale -> train -> explain + save) |
| `03_dashboard.py` | Step 3 - Survival Explorer: **3 checkpoint gates**, live form appears after gate 1, prediction after gate 2 |
| `workshop_server.py` | Instructor-managed FastAPI server: checkpoint state, SSE auto-refresh, prediction endpoint, serves `web/dist` |
| `serve_workshop.py` | Instructor-managed launcher: free port, background server, browser, reuse of a running page |
| `workshop_steps.py` | Instructor-managed shared machinery: result serialization + `chart()` / `metric()` / `verdict()` helpers |
| `web/` | The React + TypeScript + Tailwind UI (ECharts charts); `web/dist` is committed so students never need Node. Styled on the mail-triage design system (self-hosted Geist fonts in `web/public/fonts`) |
| `data/titanic.csv` | The original 1912 passenger list (holes and all, which is the point) |
| `personas.json` / `personas/` | The 10-persona survival-quiz roster and its Edwardian portrait images, served to the front page |
| `AGENTS.md` | Persistent system prompt for the students' AI Teaching Assistant |
| `deployment/windows/` | Windows one-click OpenCode classroom environment (PowerShell + `.bat` launchers) |
| `deployment/macos/` | macOS one-click classroom environment (`.command` launchers + shell launcher) |
| `deployment/baseline/` | Pristine scaffold scripts + passenger data restored by both platforms' RESET WORKSHOP |

## How the class works (checkpoint flow)

0. **Front page**: the page opens on a short guide: what students will
   build and why, a side-by-side setup screenshot
   (`web/public/onboarding/setup.png`, drop-in), a "what happens under the
   hood" diagram, and an interactive **survival challenge** (10 real
   passenger personas with portraits and a countdown timer), plus a live
   **playground predictor**: every dataset field, instant feedback as the
   controls move, and a "load a random real passenger" button that tests the
   built-in model against the real outcome. A "Start the workshop" button
   enters the three tabs.
1. **Once**: the launcher serves the workshop page automatically
   (`deployment/windows/START VIBE CODING.bat` or
   `deployment/macos/START VIBE CODING.command` starts it on port 4097; a
   watchdog restarts either service if it crashes, and either launcher
   tears both down when its window closes). To (re)start it by hand:
   `python serve_workshop.py`.
   Students see one page, three tabs; each tab shows its next checkpoint as a
   prompt-hint card, locked steps stay greyed out. Tab 1 opens with **Step 0**:
   the AI Teaching Assistant has to prove it can reach the project (it sets
   `PAIRED = True` in `01_eda.py`) before Checkpoint 1 unlocks.
2. **Loop (the magic)**: each checkpoint card shows a *mission* (direction and
   goal, not a ready-made prompt) plus a button that opens the reference
   prompt with one click so students can copy it. The AI Teaching
   Assistant implements **exactly one gate**, verifies it in the terminal,
   bumps the script's `STEPS_COMPLETED`, saves the file. The server notices
   within a second: the open page refreshes itself, the finished checkpoint
   becomes an animated result card (tables, interactive charts, gauges), and
   the NEXT mission appears. Repeat until all 10 checkpoints are done.

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

The `demo` branch holds the full reference implementation (all 10 gates
implemented with the fancy payloads) matching the student scaffolds.

## Instructor testing / student quick start (Windows)

1. Get the workshop folder (ZIP from the instructor).
2. Double-click:
   ```
   deployment/windows/START VIBE CODING.bat
   ```
   First run only: private Python 3.12 + Node.js + OpenCode 2.0.20 are
   installed under `%LOCALAPPDATA%\VibeCoding` and workshop packages
   (pandas / scikit-learn / fastapi / uvicorn) are pip-installed.
3. The browser opens the OpenCode Web UI pointed at the workshop folder,
   and the workshop web page itself (http://127.0.0.1:4097).
4. Simply talk to the AI Teaching Assistant and watch the page evolve.
   If the workshop page ever stops, double-click:
   ```
   deployment/windows/START WORKSHOP PAGE.bat
   ```

If Vibe Coding is already running and a student starts the launcher again,
it politely says so and offers to stop the other session and start fresh,
or they can simply keep the existing one.

If the Web UI ever shows no project, use File -> Open Project and pick the
extracted workshop folder once.

Other launchers (Windows in `deployment/windows/`, macOS in
`deployment/macos/`):

- `START WORKSHOP PAGE.bat`: (re)starts the workshop web page and opens it
  in the browser. Safe to run any time; it reuses a page that is already up.
- `REPAIR VIBE CODING.bat`: revalidates/rebuilds the classroom runtimes
  without touching student project files.
- `RESET WORKSHOP.bat`: restores the three workshop scripts and
  `data/titanic.csv` to their originals and deletes generated artifacts, so
  the 10 checkpoints lock again. The classroom runtime and API key stay.
- `RESET VIBE CODING.bat`: removes only `%LOCALAPPDATA%\VibeCoding`
  and `%USERPROFILE%\.vibecoding`; system installs and student projects stay.

The macOS folder has `.command` equivalents of everything above.

## Student quick start (macOS)

The macOS launchers live in `deployment/macos/` (double-clickable `.command`
files mirroring the Windows `.bat` files). First time only, in Terminal:

```
cd deployment/macos
chmod +x *.command vibe-macos.sh
xattr -dr com.apple.quarantine .
```

Then double-click `START VIBE CODING.command`, or use
`REPAIR VIBE CODING.command`, `START WORKSHOP PAGE.command`,
`RESET WORKSHOP.command`, `RESET VIBE CODING.command` exactly like on
Windows. The private runtime is installed under
`~/Library/Application Support/VibeCoding`, and the API key is read from
`~/.vibecoding/openrouter-key.txt` (written from `deployment/macos/key.txt`;
the Windows launcher uses `deployment/windows/key.txt`).
See `deployment/macos/MAC-README-FIRST.txt` for details and troubleshooting.

## Classroom hardening

The launcher bakes guardrails into the generated OpenCode config, so the AI
Teaching Assistant and student-written code are fenced by more than
instructions:

- The OpenRouter key is read from `%USERPROFILE%\.vibecoding\openrouter-key.txt`
  at request time and is **never exported** into the service or shell
  environment, so generated code cannot read it from the environment.
- Shell access is limited to `python 01_eda.py` / `02_train.py` /
  `03_dashboard.py`; edits are limited to those three scripts; `deployment/`
  is read-blocked; grep, webfetch, subagents, skills, and external
  directories are denied.
- Extended model thinking is off by default (OpenRouter `reasoning.enabled=false`).
- The workshop server stops runaway gate code after 20 seconds, caps result
  sizes, paginates tables, validates prediction input, and rejects oversized
  request bodies.
- `RESET WORKSHOP` (Windows `.bat` / macOS `.command`) restores the three
  scripts **and** `data/titanic.csv` from `deployment/baseline/`.
- `AGENTS.md` carries the assistant's workshop instructions, with secrets
  kept off-limits.

## Instructor checklist before class

1. Copy `deployment/windows/KEY.txt.TEMPLATE` to
   `deployment/windows/key.txt` (and/or the same in `deployment/macos/`
   for Macs) and paste the OpenRouter API key (key only, no quotes, no
   "Bearer "; OpenRouter keys start with "sk-or-").
   - `key.txt` is gitignored so a real key can never be committed.
   - The launcher refuses to run with the placeholder still in place.
   - When distributing a ZIP, include `key.txt`. It is inside the zip,
     never in the git history.
2. Build the UI once (`cd web && npm run build`) so `web/dist` is current.
3. Put the 10 quiz portraits in `personas/` (named `M1.jpg` … `F5.jpg`) and,
   optionally, a side-by-side OpenCode + workshop-page screenshot at
   `web/public/onboarding/setup.png` (both are drop-in; placeholders show
   until they exist).
4. Optional: pre-bake big downloads into `deployment/windows/payload/`
   (python-3.12.10 installer, node-v24.21.0 zip, SHASUMS256.txt) to reduce
   classroom Wi-Fi traffic. See `deployment/windows/README-FIRST.txt`.
5. Keep the whole `deployment/` folder (both platform folders and the
   shared `baseline/`) next to the workshop files when zipping.

## Updating launcher files

`deployment/MANIFEST-SHA256.json` records SHA-256 + size for every
launcher file. If you modify a launcher (e.g. `oneclick.ps1`), regenerate
the manifest before creating a classroom ZIP.

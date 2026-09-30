# Titanic AI Literacy Workshop

A 75-minute Year 1 AI workshop for students with zero programming experience,
bundled with a one-click OpenCode classroom environment. **Everything happens
in the browser**: the workshop scripts are paired with Gradio web interfaces,
combined into one classroom page.

## What's in this repo

| Path | Purpose |
|---|---|
| `01_eda.py` | Step 1 - Meet the Data: charts + summary (CLI and web both work) |
| `02_train.py` | Step 2: train the survival model, report test accuracy (CLI and web) |
| `03_dashboard.py` | Step 3: Gradio survival web app (Gradio hot reload) |
| `04_classroom.py` | Instructor-managed one-page launcher: all three steps as browser tabs |
| `data/titanic.csv` | The cleaned 1912 passenger list students use |
| `AGENTS.md` | Persistent system prompt for the students' AI Teaching Assistant |
| `deployment/` | Launcher scripts + hardened bootstrap for the OpenCode Web UI environment (OpenCode 2.0.20 pinned, Tencent glm-5.3-flash as the only provider) |

## Student quick start (Windows)

1. Get the workshop folder (ZIP from the instructor).
2. Double-click:
   ```
   deployment/START VIBE CODING.bat
   ```
   First run only: private Python 3.12 + Node.js + OpenCode 2.0.20 are
   installed under `%LOCALAPPDATA%\VibeCoding` and workshop packages
   (pandas / matplotlib / scikit-learn / gradio) are pip-installed.
3. The browser opens the OpenCode Web UI pointed at the workshop folder.
4. Ask the AI Teaching Assistant to run the workshop web page:
   ```
   gradio 04_classroom.py
   ```
   (or a single step: `gradio 01_eda.py`)
   The Teaching Assistent opens the link in your browser; the class then
   works tab by tab: explore -> train -> predict.

Instructor testing without OpenCode (must have Python packages installed):

```
gradio 04_classroom.py
```

If the Web UI ever shows no project, use File -> Open Project and pick the
extracted workshop folder once.

Other launchers:

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

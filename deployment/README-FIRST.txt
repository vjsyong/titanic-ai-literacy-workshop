VIBE CODING CLASSROOM DEPLOYMENT
================================

IMPORTANT: THIS COLLECTION OF FILES IS MEANT TO SIT INSIDE THE WORKSHOP
REPOSITORY (the parent folder of this "deployment" folder), NOT IN
ISOLATION.

The README-first instructions from the standalone bundle apply, with these
repository integration notes:

WHAT THE STUDENT DOES
---------------------
1. Keep the deployment folder next to the workshop files (01_eda.py,
   02_train.py, 03_dashboard.py, AGENTS.md).
2. Double-click:
        START VIBE CODING.bat
3. The browser opens OpenCode pointed at the workshop folder, and the
   workshop web page comes up automatically at http://127.0.0.1:4097.
   If the workshop page ever stops, double-click:
        START WORKSHOP PAGE.bat
   (it reopens a page that is already running, otherwise it starts one).

INSTRUCTOR CHECKLIST BEFORE DISTRIBUTION
----------------------------------------
1. Copy KEY.txt.TEMPLATE to key.txt and paste the OpenRouter API key
   (key only, no quotes, no "Bearer "; OpenRouter keys start with "sk-or-").
   key.txt is gitignored, so a real key can never be committed.
   If you distribute the package as a ZIP of this repository, MAKE SURE
   key.txt is inside it before zipping; the placeholder is deliberately
   refused by the launcher.
2. Optional: put python-3.12.10 / node-v24.21.0 installers into
   payload\ to pre-bake the big downloads (see below), and optionally
   pre-download the workshop wheels so classroom machines need no PyPI:

       python -m pip download --only-binary=:all: ^
           -d deployment\payload\wheels ^
           pandas scikit-learn fastapi uvicorn

   The launcher detects payload\wheels\*.whl and installs with
   --no-index --find-links, skipping classroom Wi-Fi entirely.
   Large packages: pandas/numpy/scipy/sklearn are the bulk of the
   install (the React UI is prebuilt in web\dist, no Node needed) --
   the first run can still take a few minutes on slow links (progress
   streams live in the console).
3. The launcher pins OpenCode 2.0.20 and provides xiaomi/mimo-v2.6-flash by
   OpenRouter - that is the default and only permitted provider.

MANIFEST
--------
MANIFEST-SHA256.json (in this folder) records the SHA-256 and size of every
launcher file as integrated into this repository:

- START, REPAIR and RESET now `pushd` into the workshop project directory
  (the parent of this folder) instead of staying in the deployment folder,
  so the OpenCode Web UI opens the workshop project by default.
- oneclick.ps1 was extended to pip-install the workshop packages
  (pandas / scikit-learn / fastapi / uvicorn) into the isolated
  classroom Python environment. The package list is part of the
  install cache signature, so old installs re-check automatically.
- key.txt is gitignored; KEY.txt.TEMPLATE carries the placeholder.
- START WORKSHOP PAGE.bat is the student-facing "start/reopen the workshop
  web page" launcher; it calls the repository-level serve_workshop.py,
  which starts workshop_server.py (the FastAPI server that serves the
  prebuilt React UI in web/dist).
- The launcher and its watchdog start/restart the workshop page through
  serve_workshop.py; no Gradio anywhere.
- RESET WORKSHOP.bat + reset_workshop.ps1 + baseline\ restore the three
  workshop scripts to their pristine scaffolds (baseline\01_eda.py,
  baseline\02_train.py, baseline\03_dashboard.py) and delete generated
  artifacts, without touching the classroom runtime, the API key, or
  data\titanic.csv. If you ever change the workshop scaffolds, refresh
  the matching files in baseline\ before distributing.

If you change any of these files later, regenerate the manifest before
distributing a classroom ZIP.

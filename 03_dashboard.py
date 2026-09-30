"""03_dashboard.py -- Step 3 "Survival Explorer" (AI Literacy Workshop)

THE STEP-BY-STEP EXPERIENCE
    Five progressive checkpoints (gates). The page starts as an empty
    explorer; each student prompt to the AI Teaching Assistant unlocks
    one gate: load the trained brain, design the passenger form, wire
    the prediction, make the verdicts kind, then black-box test it.

    The interactive part of the web page fills in as gates unlock:

        Gate 1  -> "the brain woke up" card
        Gate 2  -> the form plan (sliders/radios ranges) card
        Gate 3  -> LIVE passenger form + working prediction button
        Gate 4  -> kinder verdict wording
        Gate 5  -> black-box test bench + graduation message

    The workshop page (served by workshop_server.py) notices the saved
    file within a second and reveals the next checkpoint.

HOW TO RUN
    python 03_dashboard.py    (terminal checklist view)
    python serve_workshop.py  (the web page -- all three steps at once)
"""

import os
import pickle

import pandas as pd

# Shared gate helpers (charts, metrics, structured verdicts).
import workshop_steps

# ----------------------------------------------------------------------------
# PATH -- never change or move this
# ----------------------------------------------------------------------------
MODEL_PATH = "titanic_model.pkl"

# ----------------------------------------------------------------------------
# SHARED STATE between gates (same contract as 02_train.py) -- the AI
# assistant may read/write entries while building a gate; never rename.
# ----------------------------------------------------------------------------
ARTIFACTS = {}

STEPS_COMPLETED = 0

# The canonical live form, in order. Gate 2 stores its own version here;
# the page renders whatever the gates produced (the workshop plumbing).
DEFAULT_INPUT_SPEC = [
    {"label": "Ticket class", "kind": "radio", "choices": [1, 2, 3], "value": 3},
    {"label": "Sex", "kind": "radio", "choices": ["male", "female"], "value": "female"},
    {"label": "Age", "kind": "slider", "min": 0, "max": 80, "step": 1, "value": 25},
    {"label": "Siblings/spouses aboard", "kind": "slider", "min": 0, "max": 8, "step": 1, "value": 0},
    {"label": "Parents/children aboard", "kind": "slider", "min": 0, "max": 9, "step": 1, "value": 0},
    {"label": "Ticket fare (pounds, 1912)", "kind": "slider", "min": 0, "max": 500, "step": 1, "value": 30},
]


# ============================================================================
# CHECKPOINT GATES -- student + AI edit zone
# ============================================================================
# Rules for the AI assistant:
#   * Implement ONE gate per student request, strictly inside the gate.
#   * Gate 3 must expose the prediction function as:
#         ARTIFACTS["predict"](values_dict) -> dict
#     where values_dict maps each form label -> its chosen value, and the
#     returned dict is built with:
#         workshop_steps.verdict(text, probability, band)
#     "probability" is 0.0-1.0 (drives the animated gauge) and "band" is
#     the kinder wording label (e.g. "likely", "close call", "unlikely").
#   * Gate 2 must store the form definition as ARTIFACTS["input_spec"] =
#     a list of dicts like DEFAULT_INPUT_SPEC above.
#   * If a gate needs a missing prerequisite (e.g. no titanic_model.pkl),
#     its function may return a friendly text card telling the student
#     which earlier step to finish -- do NOT raise on missing files.
#   * Bump STEPS_COMPLETED (one at a time) after the web page shows the
#     gate working.
# ============================================================================


# === GATE 1 -- "Wake the brain" ==============================================
def step_1_wake_the_brain():
    """Load titanic_model.pkl (trained in Step 2) and prove it works.

    LOOK LIKE: a friendly 'the trained brain is awake' card, including
    one example prediction on a fixed test passenger. If the trained
    brain is missing, return a kind note telling the student to finish
    Step 2 -- checkpoint 7 first (no crash!).
    """
    raise NotImplementedError("Gate 1 is not built yet")


# === GATE 2 -- "Design the passenger form" ===================================
def step_2_design_the_form():
    """Decide which passenger attributes the web form should offer.

    LOOK LIKE: a small table describing each control (name, type,
    sensible range/choices, default). Store the definition in
    ARTIFACTS["input_spec"] (same shape as DEFAULT_INPUT_SPEC).
    """
    raise NotImplementedError("Gate 2 is not built yet")


# === GATE 3 -- "Wire the prediction" =========================================
def step_3_wire_prediction():
    """Make the form actually predict.

    MUST (per the gate contract):
      * read and use ARTIFACTS["input_spec"] labels,
      * encode 'Sex' back to numbers exactly like the model was trained
        (word plain-fare floats are NOT welcome here),
      * scale the numbers with the stored scaler BEFORE predicting,
      * store `ARTIFACTS["predict"] = my_predict_function`, where the
        function takes values_dict and returns
        workshop_steps.verdict(text, probability, band) -- the page then
        draws the animated survival gauge and the kinder wording itself,
      * confirm with one live example on REAL model output (not mock
        text); a text sentence plus a gauge is perfect.
    """
    raise NotImplementedError("Gate 3 is not built yet")


# === GATE 4 -- "Kind verdicts" ===============================================
def step_4_kind_verdicts():
    """Reword the verdict so it is never scary: 3 probability bands.

    LOOK LIKE: a small table bands -> wording tone. Re-place
    ARTIFACTS["predict"] with a version that uses the kinder wording,
    then re-run one example on the real model to show the new text.
    The gauge color follows the band, so label them clearly.
    """
    raise NotImplementedError("Gate 4 is not built yet")


# === GATE 5 -- "Black-box the brain" =========================================
def step_5_black_box_tests():
    """Probe the model with imaginary passengers and discuss unfairness.

    LOOK LIKE: a table of at least 6 imaginary passengers, each with the
    live verdict, PLUS an interactive bar chart comparing their survival
    probabilities (0-100), plus 2-3 plain-English questions for class
    discussion (is any pattern unfair? what does the model NOT see?).
    """
    raise NotImplementedError("Gate 5 is not built yet")


# ============================================================================
# STEP DESCRIPTIONS (web page reads this).
# ============================================================================
STEPS = [
    {
        "number": 1,
        "title": "Wake the brain",
        "story": (
            "Your Step 2 work saved a trained brain on disk. Wake it up "
            "here and check that it gives sensible guesses."
        ),
        "prompt": (
            "Step 3 of the workshop, checkpoint 1: load the saved model "
            "titanic_model.pkl and prove it is alive by predicting one "
            "fixed test passenger. If the file is missing, tell me kindly "
            "which Step 2 checkpoint to finish first instead of crashing."
        ),
        "fn": "step_1_wake_the_brain",
    },
    {
        "number": 2,
        "title": "Design the passenger form",
        "story": (
            "Before wiring anything: decide which controls the imaginary "
            "passenger form gets (radios for ticket class and sex, sliders "
            "for the numbers) with human-friendly ranges."
        ),
        "prompt": (
            "Step 3, checkpoint 2: propose the passenger web form -- for "
            "each attribute tell me if it should be a dropdown/slider and "
            "what sensible range or choices to give it, and store this "
            "plan where the page can find it."
        ),
        "fn": "step_2_design_the_form",
    },
    {
        "number": 3,
        "title": "Wire the prediction",
        "story": (
            "Time to connect the form to the brain: press predict, and "
            "the model's guess appears as an animated gauge. Remember the "
            "model was trained on numbers, so 'female' must turn back into "
            "its coded digit before reaching the model."
        ),
        "prompt": (
            "Step 3, checkpoint 3: connect the form to the model so the "
            "prediction button works. Encode the Sex choices back to "
            "numbers exactly like Step 2 did, use the stored scaler, and "
            "show the survival probability as a gauge with a human "
            "sentence. Show me one live example straight from the model."
        ),
        "fn": "step_3_wire_prediction",
    },
    {
        "number": 4,
        "title": "Kind verdicts",
        "story": (
            "Nobody dies twice -- the passengers in the data are already "
            "history. Trainings models must speak gently: soft wording "
            "for low, medium and high probabilities."
        ),
        "prompt": (
            "Step 3, checkpoint 4: make the browser wording gentler -- "
            "define three probability bands (e.g. unlikely, close call, "
            "likely) and reword the verdicts. Re-run one example on the "
            "live model to show the friendlier message."
        ),
        "fn": "step_4_kind_verdicts",
    },
    {
        "number": 5,
        "title": "Black-box the brain",
        "story": (
            "Final curiosity run: feed the brain imaginary passengers and "
            "discuss whether the patterns are FAIR. A model is a mirror "
            "of its data, nothing more."
        ),
        "prompt": (
            "Step 3, checkpoint 5 (final!): test the live model with at "
            "least six imaginary passengers (young/old, women/men, 1st/3rd "
            "class), show their verdicts in a table AND as a bar chart of "
            "their survival chances, and give me two or three discussion "
            "questions about fairness and what the data cannot tell us."
        ),
        "fn": "step_5_black_box_tests",
    },
]


# ============================================================================
# ORCHESTRATION -- function name and behavior contract (do not rename).
# ============================================================================
def launch_dashboard():
    """Runs every completed checkpoint in order (terminal-friendly view).

    The web page renders the checkpoints itself; this function exists so
    `python 03_dashboard.py` can prove the gates work in a terminal.
    """
    for step in STEPS:
        if step["number"] > STEPS_COMPLETED:
            break
        fn = globals().get(step["fn"])
        if fn is None:
            continue
        try:
            result = fn()
        except Exception as exc:
            print(f"Gate {step['number']} hit a problem: {exc}")
            raise
        print(f"Gate {step['number']} OK -- {step['title']}")
    return ARTIFACTS


if __name__ == "__main__":
    print(
        "Terminal mode: running the completed checkpoints in order.\n"
        "For the step-by-step web page:  python serve_workshop.py"
    )
    launch_dashboard()


# ============================================================================
# PAGE METADATA -- the tab title and intro the workshop page shows.
# ============================================================================
PAGE = {
    "id": "dashboard",
    "title": "3 - Survival Explorer",
    "intro": (
        "The trained brain from Step 2 is loaded here. Build the form "
        "checkpoint by checkpoint with your AI Teaching Assistant, then "
        "test it with imaginary passengers."
    ),
}

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
#   * The LOOK LIKE notes are the MINIMUM, not a blueprint. Compose each
#     card your own way -- chart kind, text and metric mix are yours to
#     choose, and two good assistants should NOT produce identical
#     cards. Only the MUST/contract items (input_spec, predict, pkl)
#     are rigid: the page plumbing depends on them.
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

    MUST: re-place ARTIFACTS["predict"] with a version using the kinder
    wording, and re-run one example on the real model to show the new
    voice. The gauge color follows the band, so label the bands clearly.
    CHOOSE freely: how you present the three bands (a bands->tone
    table, before/after verdicts at different probabilities, live
    examples) -- your call.
    """
    raise NotImplementedError("Gate 4 is not built yet")


# === GATE 5 -- "Black-box the brain" =========================================
def step_5_black_box_tests():
    """Probe the model with imaginary passengers and discuss unfairness.

    MUST: at least 6 imaginary passengers who differ sharply, each with
    their live verdict, plus 2-3 plain-English questions for class
    discussion (is any pattern unfair? what does the model NOT see?).
    CHOOSE freely: table + bar chart of survival probabilities is one
    strong shape; a "case files" style card, a comparison matrix, or
    provocative pairs (same person, one attribute flipped) also work --
    pick the staging that sparks the argument.
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
            "Bring one passenger to life in your head (their age, class, sex) and describe them to "
            "the AI. Ask it to wake the frozen brain from titanic_model.pkl and predict YOUR "
            "passenger - and if the file is missing, have it explain kindly which Step 2 checkpoint "
            "must come first instead of crashing."
        ),
        "hints": [
            "The file only exists once Stage 2's last checkpoint is done.",
            "If it's missing, the page should say something kind — not "
            "crash. Ask for that explicitly.",
            "One fixed test passenger is enough proof of life.",
        ],
        "guide": (
            "**Reusing a saved model is the industry norm: train once, "
            "predict everywhere.** The brain on disk is exactly the one "
            "that scored ~80% on its hidden exam.\n\n"
            "*Discuss:* what should an app do when a dependency is "
            "missing? Crashing is easy; a kind message is design.\n\n"
            "*Next up:* design the form classmates will play with."
        ),
        "reference": (
            "Step 3 of the workshop, checkpoint 1: load the saved model "
            "titanic_model.pkl and prove it is alive by predicting one "
            "fixed test passenger. If the file is missing, tell me kindly "
            "which Step 2 checkpoint to finish first instead of crashing."
        ),
        "reference_alt": (
            "Load titanic_model.pkl and predict one fixed passenger "
            "with it; if the file is missing, show a kind message "
            "pointing to Stage 2's last checkpoint."
        ),
        "experiment": (
            "Ask the AI to wake the brain twice and predict the same "
            "passenger both times — are the answers identical? Why "
            "should they be?"
        ),
        "context": (
            "**Where the brain has been:**\n\n"
            "`titanic_model.pkl` was frozen at the end of Stage 2. A "
            "saved brain is: train once → save to disk → wake it "
            "anywhere, forever. Waking it = loading the file and "
            "calling its predict on a passenger."
        ),
        "fn": "step_1_wake_the_brain",
        "placeholder": (
            "e.g. “Wake up the model we trained earlier and prove it "
            "still guesses sensibly…”"
        ),
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
            "Sketch the form like a designer: which control suits ticket class and sex, what "
            "sensible range suits age and fare - and pick ONE field you would drop to keep the form "
            "friendly. Ask the AI to build the form to your design and store the plan where the "
            "page can find it."
        ),
        "hints": [
            "Ticket class and sex suit dropdowns/radios — age and fare "
            "suit sliders.",
            "Think about sensible ranges: ages 0–80? classes 1/2/3?",
            "The plan must be stored where the page can find it — say so "
            "in your request.",
        ],
        "context": pd.DataFrame(
            [
                {"Field": "Pclass", "Example value": "1, 2 or 3"},
                {"Field": "Sex", "Example value": "male / female"},
                {"Field": "Age", "Example value": "22.0 (babies to 80)"},
                {"Field": "SibSp", "Example value": "0–8"},
                {"Field": "Parch", "Example value": "0–6"},
                {"Field": "Fare", "Example value": "7.25–512.33"},
                {"Field": "Embarked", "Example value": "S / C / Q"},
            ]
        ),
        "guide": (
            "**A good form hides the machinery: classmates will use it "
            "without ever seeing a number pipeline.** Designing sensible "
            "defaults (not ages 0–500!) is real product thinking.\n\n"
            "*Discuss:* which attribute would you REMOVE from the form to "
            "keep it friendly? Fewer, well-chosen inputs often beat "
            "complete ones.\n\n"
            "*Next up:* wire the form to the brain so Predict actually "
            "predicts."
        ),
        "reference": (
            "Step 3, checkpoint 2: propose the passenger web form -- for "
            "each attribute tell me if it should be a dropdown/slider and "
            "what sensible range or choices to give it, and store this "
            "plan where the page can find it."
        ),
        "reference_alt": (
            "Propose the passenger form: for each field pick a dropdown "
            "or a slider with sensible ranges, and store the plan where "
            "the page can use it."
        ),
        "experiment": (
            "Ask the AI what happens if a user drags the age slider to "
            "110 — should the form allow impossible values? Decide a "
            "rule together."
        ),
        "fn": "step_2_design_the_form",
        "placeholder": (
            "e.g. “Plan the passenger form: which fields and which "
            "controls for each…”"
        ),
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
            "First say what could go WRONG if the form hands 'female' straight to a model that "
            "expects Stage 2's digits. Then ask the AI to wire the form to the brain - encode "
            "exactly like Stage 2, apply the stored scaler - so Predict produces a live survival "
            "gauge, and have it prove the pipeline with one live example."
        ),
        "hints": [
            "The form's words (female/male) must become numbers EXACTLY "
            "the way Stage 2 chose.",
            "The stored scaler must be applied before predicting — same "
            "rule as training time.",
            "Ask for one live example straight from the model to prove "
            "it's real.",
        ],
        "guide": (
            "**The full pipeline runs on every click: translate words → "
            "scale → predict.** It's the exact journey of Stage 2, now "
            "invisible and instant.\n\n"
            "*Discuss:* what happens if the form's encoding drifts even "
            "slightly from training-time encoding? (Garbage in, garbage "
            "out — quietly.)\n\n"
            "*Next up:* the raw probability can sting — time to choose "
            "kinder words."
        ),
        "reference": (
            "Step 3, checkpoint 3: connect the form to the model so the "
            "prediction button works. Encode the Sex choices back to "
            "numbers exactly like Step 2 did, use the stored scaler, and "
            "show the survival probability as a gauge with a human "
            "sentence. Show me one live example straight from the model."
        ),
        "reference_alt": (
            "Connect the form to the saved model: encode sex exactly as "
            "trained, apply the scaler, and show each prediction as a "
            "gauge with one human sentence."
        ),
        "experiment": (
            "Predict the same passenger twice through the form — "
            "identical gauge both times? If not, ask the AI what's "
            "leaking."
        ),
        "context": (
            "**The pipeline that will run on every click (same three "
            "moves as Stage 2, now automatic):**\n\n"
            "1. **encode** — form words → the exact digits Stage 2 "
            "chose\n"
            "2. **scale** — squeeze the numbers with the SAME scaler "
            "from the freezer\n"
            "3. **predict** — the model answers with a probability\n\n"
            "One mismatched digit or unscaled number = quietly wrong "
            "answers."
        ),
        "fn": "step_3_wire_prediction",
        "placeholder": (
            "e.g. “Connect the form to the model so the Predict button "
            "really predicts…”"
        ),
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
            "Choose the wording first: what should the three bands be called, and where should "
            "'close call' begin and end? Ask the AI to reword the verdicts into YOUR bands and "
            "demonstrate one on the live model."
        ),
        "hints": [
            "A cold '0.34' can sting — these were real people.",
            "Unlikely / close call / likely is one set of bands; make "
            "them your own.",
            "Demonstrate on the live model so the class hears the "
            "gentler voice.",
        ],
        "guide": (
            "**Machine-learning output is a number; how you present it is "
            "a human decision.** Same probability, very different "
            "feel — wording is part of the interface, not decoration.\n\n"
            "*Discuss:* could kinder wording mislead someone? Where's "
            "the line between gentle and sugar-coated?\n\n"
            "*Next up:* the final checkpoint — stress-test the whole "
            "system like a scientist."
        ),
        "reference": (
            "Step 3, checkpoint 4: make the browser wording gentler -- "
            "define three probability bands (e.g. unlikely, close call, "
            "likely) and reword the verdicts. Re-run one example on the "
            "live model to show the friendlier message."
        ),
        "reference_alt": (
            "Sort the survival chances into three friendly bands (e.g. "
            "unlikely, close call, likely), reword the verdicts, and "
            "demo one on the live model."
        ),
        "experiment": (
            "Ask the AI to show the SAME probability worded in all three "
            "bands — where does 'close call' start and end? Are the "
            "band edges honest?"
        ),
        "context": (
            "**Translating a probability into human words — worked "
            "example:**\n\n"
            "0.34 → 34% → roughly **1 passenger in 3** with those facts "
            "made it.\n\n"
            "Same number, three voices: a decimal for the machine, a "
            "percent for the math-minded, a 'one in three' for humans. "
            "Your checkpoint adds the fourth voice: friendly wording."
        ),
        "fn": "step_4_kind_verdicts",
        "placeholder": (
            "e.g. “Soften the model's verdicts into three friendly "
            "wordings…”"
        ),
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
            "Pick the unfairness you most want the class to SEE (a 1912 pattern that rings wrong "
            "today). Design six imaginary passengers around it - which attributes to vary, which to "
            "hold still - then ask the AI to run them through the live model as a table plus a bar "
            "chart of survival chances, ending with fairness questions to argue about."
        ),
        "hints": [
            "Make them differ sharply: young/old, women/men, 1st/3rd "
            "class.",
            "Ask for the verdicts as a table AND a chart of survival "
            "chances.",
            "Finish with 2–3 fairness questions the class can argue "
            "about.",
        ],
        "guide": (
            "**The model is a mirror of its data, nothing more.** It "
            "rewarded the patterns of 1912 — including the unfair ones. "
            "It cannot see courage, luck, or the lifeboat queue.\n\n"
            "*Discuss:* is it fair to predict someone's survival from "
            "their sex or ticket class? What does the model NOT know? "
            "And where else in today's world do models quietly inherit "
            "yesterday's biases?\n\n"
            "**That's the whole workshop** — you met data, trained a "
            "model, and interrogated it. This discussion is the real "
            "graduation."
        ),
        "reference": (
            "Step 3, checkpoint 5 (final!): test the live model with at "
            "least six imaginary passengers (young/old, women/men, 1st/3rd "
            "class), show their verdicts in a table AND as a bar chart of "
            "their survival chances, and give me two or three discussion "
            "questions about fairness and what the data cannot tell us."
        ),
        "reference_alt": (
            "Test the model with six or more very different imaginary "
            "passengers, chart their survival odds, and give the class "
            "2–3 fairness questions to argue about."
        ),
        "experiment": (
            "Flip ONE attribute at a time (same person, female→male, "
            "then 1st→3rd class) — how far does the verdict move? Which "
            "single attribute moves it most?"
        ),
        "context": (
            "**Scientist's trick for this checkpoint — change ONE thing "
            "at a time.** The dials your imaginary passengers can "
            "vary:\n\n"
            "- sex · ticket class · age (young/old) · fare "
            "(cheap/expensive) · family aboard (yes/no)\n\n"
            "If you change two things at once and the verdict moves, "
            "you can't tell which one did it. Fairness arguments need "
            "clean comparisons."
        ),
        "fn": "step_5_black_box_tests",
        "placeholder": (
            "e.g. “Test the model with very different imaginary "
            "passengers and help us judge it fairly…”"
        ),
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

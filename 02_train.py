"""02_train.py -- Step 2 "Train the Model" (First-year AI Literacy Workshop)

THE STEP-BY-STEP EXPERIENCE
    Seven progressive checkpoints (gates). Class starts with
    STEPS_COMPLETED = 0 and expects the student to unlock one gate per
    prompt to their AI Teaching Assistant. Each unlocked gate:

        1. gets implemented ONLY inside its `# === GATE n ===` markers,
        2. is proved with `python 02_train.py`,
        3. bumps STEPS_COMPLETED to that gate's number.

    Shared "artifacts" learned along the way are stored in the ARTIFACTS
    dict below (the classroom plumbing around the gates, not the gates
    themselves), so later gates and the Step 3 dashboard can use them.

HOW TO RUN
    python 02_train.py       (terminal checklist view)
    gradio 02_train.py       (single-page web view)
"""

import os
import pickle

import pandas as pd

# ----------------------------------------------------------------------------
# PATHS -- never change or move these
# ----------------------------------------------------------------------------
DATA_PATH = os.path.join("data", "titanic.csv")
MODEL_PATH = "titanic_model.pkl"

# ----------------------------------------------------------------------------
# SHARED ARTIFACTS -- plumbing between gates (AI assistant may READ and
# WRITE entries here while building a gate; never rename the dict).
# ----------------------------------------------------------------------------
ARTIFACTS = {}

# ----------------------------------------------------------------------------
# PROGRESS COUNTER -- bumped strictly one gate at a time.
# ----------------------------------------------------------------------------
STEPS_COMPLETED = 0


# ============================================================================
# CHECKPOINT GATES -- student + AI edit zone
# ============================================================================
# Rules for the AI assistant:
#   * Implement ONE gate per student request, strictly inside the gate.
#   * Return web-ready content (text / DataFrame / dict {"text", "dataframe"}).
#   * Store anything later gates need in ARTIFACTS (e.g. ARTIFACTS["model"]).
#   * When python 02_train.py runs cleanly, bump STEPS_COMPLETED to n.
#   * NEVER touch a future gate (STOP-FIRST RULE applies).
# ============================================================================


# === GATE 1 -- "Secret language: sex becomes numbers" ========================
def step_1_encode_sex():
    """Turn the Sex column into numbers the model can digest.

    LOOK LIKE (web): a small preview table with both original Sex and the
    new Sex column, plus one sentence about why numbers help a model.
    TIP for the AI: keep it humble -- mapping 0/1 is arbitrary ordering,
    which is exactly the discussion this gate is for.
    """
    raise NotImplementedError("Gate 1 is not built yet")


# === GATE 2 -- "Choose what the model may look at" ===========================
def step_2_pick_features():
    """Decide the feature columns X and the target y (Survived).

    LOOK LIKE (web): the final feature list (Pclass, Sex-out, Age,
    SibSp, Parch, Fare), a small preview table, and a friendly line about
    'what we let the model see vs what we ask it to predict'.
    Store: ARTIFACTS["feature_columns"], ARTIFACTS["X"] and ARTIFACTS["y"].
    """
    raise NotImplementedError("Gate 2 is not built yet")


# === GATE 3 -- "Save some passengers for the final exam" =====================
def step_3_split_data():
    """Split into train and test (80/20, stratify=y, random_state=42).

    LOOK LIKE (web): how many passengers the model studies vs gets
    quizzed on, plus why (fair test = no peeking).
    Store: ARTIFACTS["x_train"], ARTIFACTS["x_test"], ARTIFACTS["y_train"],
    ARTIFACTS["y_test"].
    """
    raise NotImplementedError("Gate 3 is not built yet")


# === GATE 4 -- "Same tube size for every feature" ============================
def step_4_scale_features():
    """Scale numeric features (StandardScaler: fit on train only; transform both).

    LOOK LIKE (web): mean/mean-std style before-vs-after illustration
    for at least one numeric column, and a plain-English line about why
    huge fares should not crowd out small ages.
    Store: ARTIFACTS["scaler"], the scaled arrays, and any helper info
    that the dashboard needs (ARTIFACTS["scaler"] is used later).
    """
    raise NotImplementedError("Gate 4 is not built yet")


# === GATE 5 -- "Learn the patterns and self-check" ===========================
def step_5_train():
    """Train LogisticRegression(max_iter=1000) on the scaled train set.

    LOOK LIKE (web): the headline the class earned: Test accuracy: X.X%,
    with one line reminding accuracy is out-of-sample.
    Store: ARTIFACTS["model"].
    """
    raise NotImplementedError("Gate 5 is not built yet")


# === GATE 6 -- "What did the model care about?" ==============================
def step_6_explain_model():
    """Rank feature importance via LogisticRegression coefficients.

    LOOK LIKE (web): a table number-per-feature; explain in plain words
    (e.g. 'Sex' row pushes women toward surviving; 'Pclass' row pushes
    cheaper classes toward perishing). No jargon like log-odds.
    """
    raise NotImplementedError("Gate 6 is not built yet")


# === GATE 7 -- "Freeze the brain for the dashboard" ==========================
def step_7_save_model():
    """Pickle the trained model, its scaler, and feature_columns together.

    LOOK LIKE (web): a friendly confirmation that titanic_model.pkl is
    ready for Step 3, plus ONE sample passenger verdict (e.g. first-class
    woman) as proof the brain works.
    MUST pickle a dict {"model": ..., "scaler": ..., "feature_columns": ...}
    to MODEL_PATH -- the Step 3 dashboard (03_dashboard.py) expects exactly
    that structure (this is the cross-script contract).
    """
    raise NotImplementedError("Gate 7 is not built yet")


# ============================================================================
# STEP DESCRIPTIONS (web page reads this).
# ============================================================================
STEPS = [
    {
        "number": 1,
        "title": "Secret language: sex becomes numbers",
        "story": (
            "A model is a giant pattern-spotter for numbers. Our data "
            "contains words like 'female' -- make the model's life easy "
            "and translate that into digits. (Warning: the digit order is "
            "arbitrary, and that's OK -- tell your assistant to only use "
            "it for encoding)."
        ),
        "prompt": (
            "Step 2 of the workshop, checkpoint 1: take the Sex column from "
            "data/titanic.csv, replace female/male with numbers (your "
            "choice of scheme -- explain it), and show me a preview of the "
            "new column side by side with the original words. Store the "
            "results so the next checkpoints can use them."
        ),
        "fn": "step_1_encode_sex",
    },
    {
        "number": 2,
        "title": "Choose what the model may look at",
        "story": (
            "EVERY model answers ONE question. We ask: 'survived or not?' "
            "The model may look at several clues (ticket class, sex, age, "
            "family aboard, fare) but NOT at Name or PassengerId -- those "
            "are person IDs, not survival clues."
        ),
        "prompt": (
            "Step 2, checkpoint 2: choose which columns the model may look "
            "at (features) and which column it must predict. Show me the "
            "chosen feature columns and why we ignored things like Name. "
            "Remember to use the sex column you encoded in checkpoint 1, "
            "not the word version."
        ),
        "fn": "step_2_pick_features",
    },
    {
        "number": 3,
        "title": "Save some passengers for the final exam",
        "story": (
            "A model that memorizes its homework looks smart but is a "
            "cheat. Keep about a fifth of the passengers aside as secret "
            "test material the model never sees during learning."
        ),
        "prompt": (
            "Step 2, checkpoint 3: split the data into a training set and "
            "a test set (about 80/20). Show me how many passengers are in "
            "each, and explain in one friendly line why we hide the test "
            "set from training."
        ),
        "fn": "step_3_split_data",
    },
    {
        "number": 4,
        "title": "Same tube size for every feature",
        "story": (
            "Fare ranges from tiny to absurd; Age quietly sits between 0 "
            "and 80. A model that mixes such different scales can mistake "
            "bigness for importance. Fix the tube sizes with standardization."
        ),
        "prompt": (
            "Step 2, checkpoint 4: scale the numeric features for training "
            "(fit on the train set only -- no peeking). Show me one "
            "numeric column before and after scaling so I can feel the "
            "difference (mean ~ 0). Keep the scaler handy for later."
        ),
        "fn": "step_4_scale_features",
    },
    {
        "number": 5,
        "title": "Learn the patterns and self-check",
        "story": (
            "Time to actually train! The model will read the training set "
            "of survivors and non-survivors, learn its pattern, then face "
            "the secret test passengers it was never shown."
        ),
        "prompt": (
            "Step 2, checkpoint 5: train a Logistic Regression model on "
            "the scaled training data (this is a fine first model -- keep "
            "it simple and explainable). Then tell me how accurate its "
            "guesses were on the test set it never saw."
        ),
        "fn": "step_5_train",
    },
    {
        "number": 6,
        "title": "What did the model care about?",
        "story": (
            "A model need not be a black box. We can ask it: which clues "
            "did you actually use? Watch the answer confirm what WE saw "
            "by eye in Step 1 with our own charts."
        ),
        "prompt": (
            "Step 2, checkpoint 6: rank the features by how much the model "
            "used them (for a Logistic Regression, the coefficient sizes "
            "tell us that). Explain each row in plain English -- no "
            "statistics jargon."
        ),
        "fn": "step_6_explain_model",
    },
    {
        "number": 7,
        "title": "Freeze the brain for the dashboard",
        "story": (
            "Save the finished brain to disk so the Step 3 web form can "
            "load it whenever a new imaginary passenger walks in. Brains "
            "on disk is what makes predictions reusable!"
        ),
        "prompt": (
            "Step 2, checkpoint 7 (last one!): save everything needed for "
            "predictions to titanic_model.pkl (model, scaler, and the "
            "feature list in that order/shape). Prove it works by "
            "predicting one fresh passenger, e.g. a 30-year-old woman in "
            "1st class. Make the message friendly and clear."
        ),
        "fn": "step_7_save_model",
    },
]


# ============================================================================
# ORCHESTRATION -- function name and behavior contract (do not rename).
# ============================================================================
def train_model():
    """Runs every completed gate in order; returns the test accuracy
    (or None until Gate 5 exists). Prints a terminal checklist."""
    accuracy = None

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
        if step["number"] == 5:
            accuracy = result if isinstance(result, float) else accuracy

    if accuracy is None and 5 <= STEPS_COMPLETED < len(STEPS):
        accuracy = ARTIFACTS.get("test_accuracy")
    return accuracy


if __name__ == "__main__":
    print(
        "Terminal mode: running the completed checkpoints in order.\n"
        "For the step-by-step magic, serve with:  gradio 02_train.py\n"
        "Or serve every workshop step at once:    gradio 04_classroom.py"
    )
    # Graceful hint when the student runs ahead of the gates. (Keep this
    # run guard exactly as-is; the AI assistant also gets terminal access
    # and will run this file after each gate.)
    train_model()


# ============================================================================
# WEB INTERFACE -- pairs this script with a web page (Gradio).
# ============================================================================
import gradio as gr  # noqa: E402  (web layer after data layer by design)
import workshop_steps  # noqa: E402


def build_training_app():
    """Step 2 web page built entirely from the checkpoint scaffold."""
    return workshop_steps.make_app(
        title="2 - Train the Model",
        intro=(
            "Let's turn the Titanic patterns into a model that guesses by "
            "itself. Unlock the checkpoints one at a time -- your assistant "
            "does the typing, you supply the intent."
        ),
        steps=STEPS,
        module_globals=globals(),
    )


demo = build_training_app()

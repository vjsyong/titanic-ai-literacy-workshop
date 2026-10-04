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

    The workshop page (served by workshop_server.py) notices the saved
    file within a second and reveals the next checkpoint.

HOW TO RUN
    python 02_train.py        (terminal checklist view)
    python serve_workshop.py  (the web page -- all three steps at once)
"""

import os
import pickle

import pandas as pd

# Shared gate helpers: workshop_steps.chart(...) draws interactive charts
# on the page, workshop_steps.metric(...) shows headline numbers.
import workshop_steps

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
#   * Return web-ready content: text, a DataFrame (table), or a dict
#     {"text": ..., "dataframe": ..., "chart": ..., "metric": ...}.
#     Charts: workshop_steps.chart(kind=..., data=..., x=..., y=...).
#     Headline numbers: workshop_steps.metric(value, "Test accuracy").
#   * Store anything later gates need in ARTIFACTS (e.g. ARTIFACTS["model"]).
#   * When python 02_train.py runs cleanly, bump STEPS_COMPLETED to n.
#   * NEVER touch a future gate (STOP-FIRST RULE applies).
#   * The LOOK LIKE notes are the MINIMUM, not a blueprint. Compose each
#     card your own way -- chart kind, text, metric mix are yours to
#     choose, and two good assistants should NOT produce identical
#     cards. Only MUST/Store items are rigid (later gates and the
#     dashboard depend on them).
# ============================================================================


# === GATE 1 -- "Secret language: sex becomes numbers" ========================
def step_1_encode_sex():
    """Turn the Sex column into numbers the model can digest.

    MUST land: the translation must be visible and checkable (old words
    next to new numbers, or equivalent), and the result stored for
    later gates.
    CHOOSE freely: preview table, value-counts table, before/after
    chart -- your call. TIP: keep it humble -- mapping 0/1 is arbitrary
    ordering, which is exactly the discussion this gate is for.
    Store: the encoded data so later checkpoints can use it
    (e.g. ARTIFACTS).
    """
    raise NotImplementedError("Gate 1 is not built yet")


# === GATE 2 -- "Choose what the model may look at" ===========================
def step_2_pick_features():
    """Decide the feature columns X and the target y (Survived).

    MUST land: which columns feed the model, which column is the
    answer, and a friendly line on 'what we let the model see vs what
    we ask it to predict'. The reasoning matters more than the list
    format.
    CHOOSE freely: feature list, table, "allowed vs forbidden" split --
    any presentation that makes the exclusions discussable.
    Store: ARTIFACTS["feature_columns"], ARTIFACTS["X"] and ARTIFACTS["y"].
    """
    raise NotImplementedError("Gate 2 is not built yet")


# === GATE 3 -- "Save some passengers for the final exam" =====================
def step_3_split_data():
    """Split into train and test (80/20, stratify=y, random_state=42).

    MUST land: how many passengers the model studies vs gets quizzed
    on, and why the test group stays hidden (fair test = no peeking).
    CHOOSE freely: numbers, a visual split, a proportion gauge --
    whatever sells the 80/20 idea.
    Store: ARTIFACTS["x_train"], ARTIFACTS["x_test"], ARTIFACTS["y_train"],
    ARTIFACTS["y_test"].
    """
    raise NotImplementedError("Gate 3 is not built yet")


# === GATE 4 -- "Same tube size for every feature" ============================
def step_4_scale_features():
    """Scale numeric features (StandardScaler: fit on train only; transform both).

    MUST land: a before-vs-after illustration for at least one numeric
    column (the "same tube size" feeling), and a plain-English line
    about why huge fares should not crowd out small ages.
    CHOOSE freely: mean/std table, before/after mini-chart, a "both
    columns whisper now" framing -- your call.
    Store: ARTIFACTS["scaler"], the scaled arrays, and any helper info
    that the dashboard needs (ARTIFACTS["scaler"] is used later).
    """
    raise NotImplementedError("Gate 4 is not built yet")


# === GATE 5 -- "Learn the patterns and self-check" ===========================
def step_5_train():
    """Train LogisticRegression(max_iter=1000) on the scaled train set.

    MUST land: the test-set accuracy as the headline, rendered so the
    whole class can cheer. workshop_steps.metric (animated ring) is the
    natural hero -- but compose the card your way (add context, a
    comparison, whatever earns the moment).
    Store: ARTIFACTS["model"] (and ARTIFACTS["test_accuracy"] if handy).
    """
    raise NotImplementedError("Gate 5 is not built yet")


# === GATE 6 -- "What did the model care about?" ==============================
def step_6_explain_model():
    """Rank feature importance via LogisticRegression coefficients.

    MUST land: how much the model leaned on each feature, which way
    each pushed (toward/away from survival), explained in plain words
    (e.g. 'Sex' pushes women toward surviving; 'Pclass' pushes cheaper
    classes toward perishing). No jargon like log-odds.
    CHOOSE freely: diverging bar chart, sorted table, "hero and
    villain" framing -- pick the telling that lands. (A diverging
    horizontal bar: workshop_steps.chart(kind="bar", ..., diverging=True,
    horizontal=True) handles the colored sides for you.)
    """
    raise NotImplementedError("Gate 6 is not built yet")


# === GATE 7 -- "Freeze the brain for the dashboard" ==========================
def step_7_save_model():
    """Pickle the trained model, its scaler, and feature_columns together.

    MUST pickle a dict {"model": ..., "scaler": ..., "feature_columns": ...}
    to MODEL_PATH -- the Step 3 dashboard (03_dashboard.py) expects exactly
    that structure (this is the cross-script contract).

    MUST land on the page: a friendly confirmation that titanic_model.pkl
    is ready for Step 3, plus ONE sample passenger verdict. An animated
    gauge (workshop_steps.chart(kind="gauge", value=probability*100, ...))
    is the natural reveal -- the surrounding composition is yours.
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
            "Ask the AI to turn the Sex column's words (female/male) into "
            "numbers, and show the translation side by side with the "
            "original."
        ),
        "hints": [
            "Any consistent numbering scheme is fine — 0/1, 1/2, whatever "
            "you can explain.",
            "Ask to see the old words and new numbers together so you can "
            "check the translation.",
            "The result must be kept for the checkpoints ahead — mention "
            "that.",
        ],
        "context": pd.DataFrame(
            {"Sex": ["female", "male"], "Passengers": [314, 577]}
        ),
        "guide": (
            "**Models only do arithmetic, so words must become numbers.** "
            "Which number means which is arbitrary — 0 = female and 1 = "
            "male works just as well as the reverse, as long as it's "
            "consistent.\n\n"
            "*Discuss:* what could go wrong if you translated female/male "
            "differently on different days?\n\n"
            "*Next up:* the model can't look at everything — you decide "
            "what it may see."
        ),
        "reference": (
            "Step 2 of the workshop, checkpoint 1: take the Sex column from "
            "data/titanic.csv, replace female/male with numbers (your "
            "choice of scheme -- explain it), and show me a preview of the "
            "new column side by side with the original words. Store the "
            "results so the next checkpoints can use them."
        ),
        "reference_alt": (
            "Create a numeric version of the Sex column in "
            "data/titanic.csv (0 and 1), explain your mapping, and "
            "preview it next to the original words."
        ),
        "experiment": (
            "Ask the AI what would happen if you flipped the mapping "
            "(male=0, female=1) — does the model actually care which "
            "digit means which?"
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
            "Ask the AI to pick which columns the model may look at, and "
            "which column it must predict."
        ),
        "hints": [
            "The prediction target is always Survived (1 = made it).",
            "Good clues: ticket class, sex (numeric!), age, family aboard, "
            "fare.",
            "Why are Name and PassengerId useless? Ask the AI to explain.",
        ],
        "context": pd.DataFrame(
            [
                {"Column": "PassengerId", "Example": "1",
                 "What it holds": "just a row number"},
                {"Column": "Survived", "Example": "0 or 1",
                 "What it holds": "the answer: did they make it?"},
                {"Column": "Pclass", "Example": "1, 2 or 3",
                 "What it holds": "ticket class (wealth proxy)"},
                {"Column": "Name", "Example": "Braund, Mr. Owen Harris",
                 "What it holds": "full name, with title"},
                {"Column": "Sex", "Example": "male / female",
                 "What it holds": "words — now numeric (checkpoint 1)"},
                {"Column": "Age", "Example": "22.0 (some missing)",
                 "What it holds": "age in years, babies included"},
                {"Column": "SibSp", "Example": "0–8",
                 "What it holds": "siblings/spouses aboard"},
                {"Column": "Parch", "Example": "0–6",
                 "What it holds": "parents/children aboard"},
                {"Column": "Ticket", "Example": "A/5 21171",
                 "What it holds": "free-text ticket code"},
                {"Column": "Fare", "Example": "7.25 (up to 512)",
                 "What it holds": "ticket price in pounds"},
                {"Column": "Cabin", "Example": "C85 (mostly missing)",
                 "What it holds": "cabin code"},
                {"Column": "Embarked", "Example": "S / C / Q",
                 "What it holds": "port of embarkation"},
            ]
        ),
        "guide": (
            "**Garbage in, garbage out: you just made the model's first "
            "big quality decision.** Name and PassengerId are labels, not "
            "clues — every passenger has a unique one, so there's no "
            "pattern to learn.\n\n"
            "*Discuss:* is there any column you're UNSURE about? Dropping "
            "a useful clue weakens the model; keeping noise confuses it.\n\n"
            "*Next up:* a fair exam — hiding some passengers from the "
            "model."
        ),
        "reference": (
            "Step 2, checkpoint 2: choose which columns the model may look "
            "at (features) and which column it must predict. Show me the "
            "chosen feature columns and why we ignored things like Name. "
            "Remember to use the sex column you encoded in checkpoint 1, "
            "not the word version."
        ),
        "reference_alt": (
            "Which columns from data/titanic.csv should the model use as "
            "inputs, which column is the target, and why should Name and "
            "PassengerId be left out?"
        ),
        "experiment": (
            "Challenge the AI: could the title hidden in Name (Mr, Mrs, "
            "Master) actually be a clue? Ask it — then judge its answer. "
            "Was it a good reason to drop Name or not?"
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
            "Ask the AI to split the passengers into a training group and "
            "a hidden test group (about 80/20)."
        ),
        "hints": [
            "Roughly 80% to learn from, 20% kept secret for the final "
            "exam.",
            "Ask how many passengers ended up in each group.",
            "The test group must stay hidden until the very end — no "
            "peeking.",
        ],
        "guide": (
            "**A model tested on data it already saw is like a student "
            "graded on the exact homework answers — the score is fake.** "
            "The hidden 20% is the only honest measure.\n\n"
            "*Discuss:* what would happen to the accuracy number if we "
            "accidentally let the model peek?\n\n"
            "*Next up:* the features live on wildly different scales — "
            "that needs fixing before training."
        ),
        "reference": (
            "Step 2, checkpoint 3: split the data into a training set and "
            "a test set (about 80/20). Show me how many passengers are in "
            "each, and explain in one friendly line why we hide the test "
            "set from training."
        ),
        "reference_alt": (
            "Split the passengers 80/20 into training and test groups, "
            "tell me the sizes, and explain why the test set stays "
            "sealed until the end."
        ),
        "experiment": (
            "Ask the AI to show how many Survived=1 vs Survived=0 "
            "passengers landed in each group — roughly equal? Why would "
            "a lopsided exam be unfair?"
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
            "Ask the AI to put every numeric feature on the same scale — "
            "learning the scale from the training group only."
        ),
        "hints": [
            "Fare reaches ~500; Age sits between 0 and 80. Bigness must "
            "not look like importance.",
            "Golden rule: the scale is learned from the training group "
            "only — no peeking at the test group.",
            "Ask to see one column before and after, so you can feel the "
            "change (mean near 0).",
        ],
        "context": pd.DataFrame(
            [
                {"Feature": "Age", "Smallest value": 0.42, "Largest value": 80.0},
                {"Feature": "Fare", "Smallest value": 0.0, "Largest value": 512.33},
                {"Feature": "SibSp", "Smallest value": 0, "Largest value": 8},
                {"Feature": "Parch", "Smallest value": 0, "Largest value": 6},
                {"Feature": "Pclass", "Smallest value": 1, "Largest value": 3},
            ]
        ),
        "guide": (
            "**After scaling, every feature speaks at the same volume — "
            "mean ≈ 0, spread ≈ 1.** Without it, a model can mistake big "
            "numbers (fare!) for important numbers.\n\n"
            "*Discuss:* why is it cheating to learn the scale from the "
            "test group too? (It leaks exam answers into study time.)\n\n"
            "*Next up:* the main event — train the model and see its real "
            "exam score."
        ),
        "reference": (
            "Step 2, checkpoint 4: scale the numeric features for training "
            "(fit on the train set only -- no peeking). Show me one "
            "numeric column before and after scaling so I can feel the "
            "difference (mean ~ 0). Keep the scaler handy for later."
        ),
        "reference_alt": (
            "Scale the numeric features with the scaler fitted on the "
            "training group only, show me one column before and after, "
            "and keep the scaler safe for the dashboard."
        ),
        "experiment": (
            "Ask the AI to prove the scaling worked: what is the MEAN of "
            "a scaled column? (Spoiler: about 0.) Why is that number the "
            "receipt that it worked?"
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
            "Ask the AI to train a simple model (logistic regression is a "
            "great first pick) and show its accuracy on the hidden test "
            "group as a big animated number."
        ),
        "hints": [
            "Logistic regression = a simple, explainable pattern-spotter. "
            "Perfect for a first model.",
            "The model learns from the scaled training group, then sits "
            "the hidden exam.",
            "Ask for the accuracy as a big ring/number the whole class "
            "can cheer at.",
        ],
        "guide": (
            "**Expect roughly 78–82% accuracy.** Sounds great — but a "
            "model that always guessed 'perished' would score ~62% "
            "(remember the split from Stage 1?). Accuracy alone can "
            "flatter.\n\n"
            "*Discuss:* is ~80% good enough to trust with someone's life "
            "in 1912? Where do you think it gets things wrong?\n\n"
            "*Next up:* open the box — ask the model WHICH clues it "
            "actually used."
        ),
        "reference": (
            "Step 2, checkpoint 5: train a Logistic Regression model on "
            "the scaled training data (this is a fine first model -- keep "
            "it simple and explainable). Then show me how accurate its "
            "guesses were on the test set -- display the score as a big "
            "animated number/ring so the class can cheer."
        ),
        "reference_alt": (
            "Train a logistic regression model on the prepared data and "
            "show me its accuracy on the unseen test passengers as a "
            "big animated score."
        ),
        "experiment": (
            "Ask the AI: what accuracy would a LAZY model get by always "
            "guessing 'perished'? Compare it with your ring — how much "
            "better is your model, really?"
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
            "Ask the AI to rank the model's features by how much it "
            "leaned on each one, as a chart where positive and negative "
            "pull in opposite directions."
        ),
        "hints": [
            "Each feature gets a coefficient: size = how much the model "
            "used it, sign = which way it pushed.",
            "Positive should push toward survival, negative away — a "
            "diverging bar chart shows this well.",
            "Every row must be explainable in words a 12-year-old gets — "
            "no statistics jargon.",
        ],
        "guide": (
            "**The model confirms what WE saw by eye in Stage 1: sex "
            "dominates, class next — and it never saw our charts.** That "
            "is the magic: the same patterns, rediscovered by "
            "arithmetic.\n\n"
            "*Discuss:* did any coefficient surprise you? Anything you "
            "expected that the model ignored?\n\n"
            "*Next up:* freeze the finished brain so the dashboard can "
            "use it."
        ),
        "reference": (
            "Step 2, checkpoint 6: rank the features by how much the model "
            "used them (for a Logistic Regression, the coefficient sizes "
            "tell us that) and draw it as a colored bar chart where "
            "positive and negative pull in different directions. Explain "
            "each row in plain English -- no statistics jargon."
        ),
        "reference_alt": (
            "Show me which inputs the trained model leaned on most, in "
            "a chart where positive and negative pull apart, explained "
            "with zero jargon."
        ),
        "experiment": (
            "Ask the AI to re-explain ONE coefficient as a story (\"for "
            "every extra pound of fare, the model…\") — does the story "
            "match the chart's arrow direction?"
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
            "Ask the AI to save the trained brain to titanic_model.pkl, "
            "then prove it's alive by predicting one fresh imaginary "
            "passenger."
        ),
        "hints": [
            "Everything needed must go in the file: model, scaler, and "
            "the feature list.",
            "Invent a fresh passenger to test — e.g. a 30-year-old woman "
            "in 1st class.",
            "Ask for the survival chance shown as a gauge with a friendly "
            "sentence.",
        ],
        "guide": (
            "**A saved model is a reusable brain: the file outlives this "
            "notebook and can make predictions forever.** That's what "
            "turns a school exercise into an app.\n\n"
            "*Discuss:* your test passenger's odds — do they match your "
            "gut feeling from Stage 1's charts?\n\n"
            "*Next up:* Stage 3 — a web form anyone can use, no code "
            "needed."
        ),
        "reference": (
            "Step 2, checkpoint 7 (last one!): save everything needed for "
            "predictions to titanic_model.pkl (model, scaler, and the "
            "feature list in that order/shape). Prove it works by "
            "predicting one fresh passenger, e.g. a 30-year-old woman in "
            "1st class, and show me the survival chance as a gauge. Make "
            "the message friendly and clear."
        ),
        "reference_alt": (
            "Save the model, scaler and feature list to "
            "titanic_model.pkl, then prove it works by predicting a "
            "30-year-old woman in 1st class with a survival gauge."
        ),
        "experiment": (
            "Ask the AI to predict three very different imaginary "
            "passengers from the saved file — do the odds line up with "
            "what Stage 1's charts taught you?"
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
        "For the step-by-step web page:  python serve_workshop.py"
    )
    # Graceful hint when the student runs ahead of the gates. (Keep this
    # run guard exactly as-is; the AI assistant also gets terminal access
    # and will run this file after each gate.)
    train_model()


# ============================================================================
# PAGE METADATA -- the tab title and intro the workshop page shows.
# ============================================================================
PAGE = {
    "id": "train",
    "title": "2 - Train the Model",
    "intro": (
        "Let's turn the Titanic patterns into a model that guesses by "
        "itself. Unlock the checkpoints one at a time -- your assistant "
        "does the typing, you supply the intent."
    ),
}

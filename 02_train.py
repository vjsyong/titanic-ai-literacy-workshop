"""02_train.py -- Step 2 "Train the Model" (First-year AI Literacy Workshop)

THE STEP-BY-STEP EXPERIENCE
    Four progressive checkpoints (gates). Class starts with
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
#   * At most ONE "dataframe" and ONE "chart" per result.
#   * Store anything later gates need in ARTIFACTS (e.g. ARTIFACTS["model"]).
#   * Write clear comments that break the code into small steps and explain
#     each one in plain English: students read this code in the page's
#     "See the code" panel.
#   * When python 02_train.py runs cleanly, bump STEPS_COMPLETED to n.
#   * NEVER touch a future gate (STOP-FIRST RULE applies).
#   * The LOOK LIKE notes are the MINIMUM, not a blueprint. Compose each
#     card your own way -- chart kind, text, metric mix are yours to
#     choose, and two good assistants should NOT produce identical
#     cards. Only MUST/Store items are rigid (later gates and the
#     dashboard depend on them).
# ============================================================================


# === GATE 1 -- "Make words into numbers, choose the clues" ====================
def step_1_encode_and_choose_features():
    """Encode Sex as numbers AND decide which columns the model may use.

    MUST land: (a) the Sex translation visible and checkable (old words
    next to new numbers), (b) the feature columns X and the target y
    (Survived), with a friendly line on what the model may see vs what it
    must predict.
    CHOOSE freely: preview table, value-counts table, before/after chart
    -- your call.
    Store: the encoded data plus ARTIFACTS["feature_columns"],
    ARTIFACTS["X"] and ARTIFACTS["y"].
    TIP: keep the encoding humble -- mapping 0/1 is arbitrary ordering,
    which is exactly the discussion this gate is for. Remember to use the
    encoded Sex column, not the word version.
    """
    raise NotImplementedError("Gate 1 is not built yet")


# === GATE 2 -- "Prepare a fair exam" =========================================
def step_2_split_and_scale():
    """Split into train/test AND scale the numeric features.

    MUST land: (a) how many passengers the model studies vs gets quizzed
    on, and why the test group stays hidden (no peeking), and (b) a
    before-vs-after illustration for at least one numeric column (the
    'same tube size' feeling) with a plain-English line about why huge
    fares should not crowd out small ages.
    CHOOSE freely: numbers, a proportion gauge, a mean/std table, a
    before/after mini-chart.
    Store: ARTIFACTS["x_train"], ARTIFACTS["x_test"], ARTIFACTS["y_train"],
    ARTIFACTS["y_test"], ARTIFACTS["scaler"] and the scaled arrays.
    Golden rule: the scaler is fit on the training group ONLY.
    """
    raise NotImplementedError("Gate 2 is not built yet")


# === GATE 3 -- "Learn the patterns and self-check" ===========================
def step_3_train_model():
    """Train LogisticRegression(max_iter=1000) on the scaled train set.

    MUST land: the test-set accuracy as the headline, rendered so the
    whole class can cheer. workshop_steps.metric (animated ring) is the
    natural hero -- but compose the card your way (add context, a
    comparison, whatever earns the moment).
    Store: ARTIFACTS["model"] (and ARTIFACTS["test_accuracy"] if handy).
    """
    raise NotImplementedError("Gate 3 is not built yet")


# === GATE 4 -- "Open the box and save the brain" =============================
def step_4_explain_and_save():
    """Rank feature importance, then freeze the model for the dashboard.

    MUST land: (a) how much the model leaned on each feature and which way
    each pushed, in plain words (no log-odds jargon), and (b) a friendly
    confirmation that titanic_model.pkl is ready for Step 3, plus ONE
    sample passenger verdict with its probability.

    MUST pickle a dict {"model": ..., "scaler": ..., "feature_columns": ...}
    to MODEL_PATH -- the Step 3 dashboard (03_dashboard.py) expects exactly
    that structure (this is the cross-script contract).

    CHOOSE freely: a diverging horizontal bar chart for the coefficients
    is the natural visual
    (workshop_steps.chart(kind="bar", ..., diverging=True, horizontal=True));
    put the sample verdict in the text. (Only ONE chart per result.)
    """
    raise NotImplementedError("Gate 4 is not built yet")


# ============================================================================
# STEP DESCRIPTIONS (web page reads this).
# ============================================================================
STEPS = [
    {
        "number": 1,
        "title": "Make words into numbers, choose the clues",
        "story": (
            "Your model knows nothing about the Titanic except what you "
            "hand it. It cannot read words and it cannot ask its own "
            "questions. This checkpoint builds its whole world: the facts "
            "it may study, the answer it must produce, and the language it "
            "thinks in. Choose badly and it learns the wrong lesson; leave "
            "out a clue and it can never use it."
        ),
        "prompt": (
            "Choose the model's language first: which digit means female, and "
            "which means male? Ask the AI to translate the Sex column and "
            "show the old words beside the new numbers so you can check its "
            "work. Then choose the model's world: name the columns it may "
            "study and the one column it must predict. Explain why Name and "
            "PassengerId stay out, and say if anything useful is missing."
        ),
        "hints": [
            "Ask why a model cannot read words: it can only do arithmetic "
            "on numbers.",
            "Any consistent mapping works (0/1, 1/2, ...), but the model "
            "will trust it for every future passenger. Write it down.",
            "Name and PassengerId are unique labels. Keep them and the "
            "model memorizes people instead of learning patterns.",
            "The target is always Survived (1 = made it). Everything else "
            "the model may study is a feature.",
        ],
        "context": {
            "text": (
                "Here is the clue your digits must carry, straight from "
                "Stage 1: women were much likelier to survive than men. "
                "Whatever mapping you choose, the model will read this "
                "pattern through your numbers -- and these features become "
                "the controls on the Stage 3 form."
            ),
            "dataframe": pd.DataFrame(
                {"Sex": ["female", "male"], "Passengers": [314, 577]}
            ),
            "chart": workshop_steps.chart(
                kind="bar",
                title="The pattern your digits must carry",
                data=[
                    {"Sex": "Women", "Survived %": 74.2},
                    {"Sex": "Men", "Survived %": 18.9},
                ],
                x="Sex",
                y="Survived %",
            ),
        },
        "guide": (
            "**Models only do arithmetic, so words must become numbers.** "
            "Which number means which is arbitrary -- 0 = female and 1 = male "
            "works as well as the reverse, as long as you keep it consistent. "
            "The columns you choose are the model's entire view of a "
            "passenger: it can never use a fact you left out, and it cannot "
            "unsee a fact you included. Names and IDs are labels, not clues, "
            "so they stay out.\n\n"
            "*Discuss:* what could go wrong if you translated female/male "
            "differently on different days? Is there any column you're UNSURE "
            "about keeping?\n\n"
            "*Next up:* a fair exam -- hiding some passengers from the model."
        ),
        "reference": (
            "Step 2 of the workshop, checkpoint 1: take the Sex column from "
            "data/titanic.csv, replace female/male with numbers (your choice "
            "of scheme -- explain it), and show me a preview of the new column "
            "side by side with the original words. Then choose which columns "
            "the model may look at (features) and which column it must "
            "predict, and explain why we ignore things like Name and "
            "PassengerId (they are unique labels, not survival clues). Store "
            "the results so the next checkpoints can use them."
        ),
        "reference_alt": (
            "Create a numeric version of the Sex column in data/titanic.csv "
            "(0 and 1), explain your mapping, and preview it next to the "
            "original words. Then list the features the model should use and "
            "the target it predicts, and say why Name and PassengerId are left "
            "out (unique labels teach memorizing, not patterns)."
        ),
        "experiment": (
            "Ask the AI what would happen if you flipped the mapping "
            "(male=0, female=1) -- does the model actually care which digit "
            "means which? Then challenge it: could the title hidden in Name "
            "(Mr, Mrs, Master) actually be a clue?"
        ),
        "fn": "step_1_encode_and_choose_features",
        "placeholder": (
            "e.g. “Turn the female/male words into numbers, then tell me "
            "which columns the model may use…”"
        ),
    },
    {
        "number": 2,
        "title": "Prepare a fair exam",
        "story": (
            "A model that memorizes its homework looks smart but is a cheat. "
            "Keep about a fifth of the passengers aside as secret test "
            "material -- then fix the wildly different scales of the features."
        ),
        "prompt": (
            "Design the exam first: how big should the hidden test group be? "
            "Tell the AI your ratio and have it split the passengers your way. "
            "Then guess which feature would look loudest unscaled, and ask the "
            "AI to scale every numeric feature using the training group only, "
            "showing one column before and after."
        ),
        "hints": [
            "Roughly 80% to learn from, 20% kept secret for the final exam.",
            "Ask how many passengers ended up in each group; the test group "
            "must stay hidden until the very end.",
            "Fare reaches ~500; Age sits between 0 and 80 -- bigness must not "
            "look like importance.",
            "Golden rule: the scale is learned from the training group only "
            "-- no peeking at the test group.",
        ],
        "context": {
            "text": (
                "Two ideas in one checkpoint. (1) The exam: most passengers "
                "become the model's STUDY material; a sealed fifth stays "
                "hidden until the final test. (2) The ranges: features live on "
                "very different scales, and the scaler must learn its numbers "
                "from the study group alone."
            ),
            "dataframe": pd.DataFrame(
                [
                    {"Feature": "Age", "Smallest value": 0.42,
                     "Largest value": 80.0},
                    {"Feature": "Fare", "Smallest value": 0.0,
                     "Largest value": 512.33},
                    {"Feature": "SibSp", "Smallest value": 0,
                     "Largest value": 8},
                    {"Feature": "Parch", "Smallest value": 0,
                     "Largest value": 6},
                    {"Feature": "Pclass", "Smallest value": 1,
                     "Largest value": 3},
                ]
            ),
        },
        "guide": (
            "**A model tested on data it already saw is like a student graded "
            "on the exact homework answers -- the score is fake.** The hidden "
            "20% is the only honest measure. And after scaling, every feature "
            "speaks at the same volume: mean ~ 0, spread ~ 1.\n\n"
            "*Discuss:* what would happen to the accuracy number if we "
            "accidentally let the model peek? Why is it cheating to learn the "
            "scale from the test group too?\n\n"
            "*Next up:* the main event -- train the model and see its real "
            "exam score."
        ),
        "reference": (
            "Step 2, checkpoint 2: split the data into a training set and a "
            "test set (about 80/20, stratify on the outcome), show me how many "
            "passengers are in each, and explain in one friendly line why we "
            "hide the test set from training. Then scale the numeric features "
            "for training (fit on the train set only -- no peeking) and show "
            "me one numeric column before and after scaling so I can feel the "
            "difference (mean ~ 0). Keep the scaler handy for later."
        ),
        "reference_alt": (
            "Split the passengers 80/20 into training and test groups, tell me "
            "the sizes, and explain why the test set stays sealed until the "
            "end. Then scale the numeric features with a scaler fitted on the "
            "training group only, and show me one column before and after."
        ),
        "experiment": (
            "Ask the AI to show how many Survived=1 vs Survived=0 passengers "
            "landed in each group -- roughly equal? Why would a lopsided exam "
            "be unfair? Then ask it to prove the scaling worked: what is the "
            "MEAN of a scaled column?"
        ),
        "fn": "step_2_split_and_scale",
        "placeholder": (
            "e.g. “Hold back a secret test group, then put the features on the "
            "same scale…”"
        ),
    },
    {
        "number": 3,
        "title": "Learn the patterns and self-check",
        "story": (
            "Time to actually train! The model will read the training set of "
            "survivors and non-survivors, learn its pattern, then face the "
            "secret test passengers it was never shown."
        ),
        "prompt": (
            "Guess first: what accuracy do you expect on the hidden exam? Then "
            "ask the AI to train the model (logistic regression is a fine "
            "first pick) and show its test accuracy as a big animated score."
        ),
        "hints": [
            "Logistic regression = a simple, explainable pattern-spotter. "
            "Perfect for a first model.",
            "The model learns from the scaled training group, then sits the "
            "hidden exam.",
            "Ask for the accuracy as a big ring/number the whole class can "
            "cheer at.",
        ],
        "context": (
            "**The journey your data takes in this gate:**\n\n"
            "passenger facts -> *the pattern the model learned* -> a yes/no "
            "survival guess\n\n"
            "The ring that appears is what the class EARNED: how many of the "
            "sealed exam passengers it judged correctly."
        ),
        "guide": (
            "**Expect roughly 78-82% accuracy.** Sounds great -- but a model "
            "that always guessed 'perished' would score ~62% (remember the "
            "split from Stage 1?). Accuracy alone can flatter.\n\n"
            "*Discuss:* is ~80% good enough to trust with someone's life in "
            "1912? Where do you think it gets things wrong?\n\n"
            "*Next up:* open the box -- ask the model WHICH clues it actually "
            "used."
        ),
        "reference": (
            "Step 2, checkpoint 3: train a Logistic Regression model on the "
            "scaled training data (this is a fine first model -- keep it "
            "simple and explainable). Then show me how accurate its guesses "
            "were on the test set -- display the score as a big animated "
            "number/ring so the class can cheer."
        ),
        "reference_alt": (
            "Train a logistic regression model on the prepared data and show "
            "me its accuracy on the unseen test passengers as a big animated "
            "score."
        ),
        "experiment": (
            "Ask the AI: what accuracy would a LAZY model get by always "
            "guessing 'perished'? Compare it with your ring -- how much better "
            "is your model, really?"
        ),
        "fn": "step_3_train_model",
        "placeholder": (
            "e.g. “Train a simple model and show me how it does on its secret "
            "exam…”"
        ),
    },
    {
        "number": 4,
        "title": "Open the box and save the brain",
        "story": (
            "A model need not be a black box: ask it which clues it actually "
            "used, then freeze the finished brain to disk so the Step 3 web "
            "form can load it whenever a new passenger walks in."
        ),
        "prompt": (
            "Rank the clues first: which one did the model lean on most, and "
            "which least? Then ask the AI to draw the feature-importance chart "
            "with plain-English labels. Finish by saving the model to "
            "titanic_model.pkl and predicting an imaginary passenger you "
            "invent (age, class, sex)."
        ),
        "hints": [
            "Each feature gets a coefficient: size = how much the model used "
            "it, sign = which way it pushed.",
            "Positive should push toward survival, negative away -- a "
            "diverging bar chart shows this well.",
            "Everything needed must go in the file: model, scaler, and the "
            "feature list.",
            "Invent a fresh passenger to test -- e.g. a 30-year-old woman in "
            "1st class.",
        ],
        "context": (
            "**How to READ a coefficient -- worked example with a toy model** "
            "(it predicts *will cheer at a football match*, not survival):\n\n"
            "| Clue | Coefficient | Plain English |\n"
            "|---|---|---|\n"
            "| home team winning | +2.1 | positive, strong -> pushes toward "
            "cheering |\n"
            "| price of tickets | -1.4 | negative, strong -> pushes away from "
            "cheering |\n"
            "| day of week | +0.1 | positive but tiny -> barely matters |\n\n"
            "Size = how much the model leans on it. Sign = which way it "
            "pushes. Then the recipe card for the freezer: pack the **model**, "
            "the **scaler** and the **feature list** into `titanic_model.pkl`. "
            "Forget one and whoever wakes it later gets nonsense."
        ),
        "guide": (
            "**The model confirms what WE saw by eye in Stage 1: sex "
            "dominates, class next -- and it never saw our charts.** That is "
            "the magic: the same patterns, rediscovered by arithmetic. A saved "
            "model is a reusable brain: the file outlives this notebook and "
            "can make predictions forever.\n\n"
            "*Discuss:* did any coefficient surprise you? And does your test "
            "passenger's odds match your gut feeling from Stage 1's charts?\n\n"
            "*Next up:* Stage 3 -- a web form anyone can use, no code needed."
        ),
        "reference": (
            "Step 2, checkpoint 4 (last one!): rank the features by how much "
            "the model used them (for a Logistic Regression, the coefficient "
            "sizes tell us that) and draw it as a colored bar chart where "
            "positive and negative pull in different directions, explaining "
            "each row in plain English with no statistics jargon. Then save "
            "everything needed for predictions to titanic_model.pkl (model, "
            "scaler, and the feature list in that order/shape) and prove it "
            "works by predicting one fresh passenger, e.g. a 30-year-old woman "
            "in 1st class. Make the message friendly and clear."
        ),
        "reference_alt": (
            "Show me which inputs the trained model leaned on most, in a chart "
            "where positive and negative pull apart, explained with zero "
            "jargon. Then save the model, scaler and feature list to "
            "titanic_model.pkl and predict a 30-year-old woman in 1st class to "
            "prove it works."
        ),
        "experiment": (
            "Ask the AI to re-explain ONE coefficient as a story (\"for every "
            "extra pound of fare, the model...\") -- does the story match the "
            "chart's arrow direction? Then predict three very different "
            "imaginary passengers from the saved file."
        ),
        "fn": "step_4_explain_and_save",
        "placeholder": (
            "e.g. “Show me which clues the model leaned on, then save it and "
            "predict a new passenger…”"
        ),
    },
]


# ============================================================================
# ORCHESTRATION -- function name and behavior contract (do not rename).
# ============================================================================
def train_model():
    """Runs every completed gate in order; returns the test accuracy
    (or None until Gate 3 exists). Prints a terminal checklist."""
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

    return ARTIFACTS.get("test_accuracy")


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

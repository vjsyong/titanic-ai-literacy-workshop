"""03_dashboard.py -- Step 3 "Survival Explorer" (AI Literacy Workshop)

THE STEP-BY-STEP EXPERIENCE
    Three progressive checkpoints (gates). The page starts as an empty
    explorer; each student prompt to the AI Teaching Assistant unlocks
    one gate: wake the trained brain and design the form, wire the
    prediction with kind verdicts, then black-box test it.

    The interactive part of the web page fills in as gates unlock:

        Gate 1  -> the form plan (sliders/radios ranges) card + a "brain is
                   awake" sample prediction
        Gate 2  -> LIVE passenger form + working prediction button + kinder
                   verdict wording
        Gate 3  -> black-box test bench + graduation message

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

STEPS_COMPLETED = 3

# The canonical live form, in order. Gate 1 stores its own version here;
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
#   * Gate 2 must expose the prediction function as:
#         ARTIFACTS["predict"](values_dict) -> dict
#     where values_dict maps each form label -> its chosen value, and the
#     returned dict is built with:
#         workshop_steps.verdict(text, probability, band)
#     "probability" is 0.0-1.0 (drives the animated gauge) and "band" is
#     the kinder wording label (e.g. "likely", "close call", "unlikely").
#   * Gate 1 must store the form definition as ARTIFACTS["input_spec"] =
#     a list of dicts like DEFAULT_INPUT_SPEC above.
#   * If a gate needs a missing prerequisite (e.g. no titanic_model.pkl),
#     its function may return a friendly text card telling the student
#     which earlier step to finish -- do NOT raise on missing files.
#   * At most ONE "dataframe" and ONE "chart" per result.
#   * Bump STEPS_COMPLETED (one at a time) after the web page shows the
#     gate working.
#   * The LOOK LIKE notes are the MINIMUM, not a blueprint. Compose each
#     card your own way -- chart kind, text and metric mix are yours to
#     choose, and two good assistants should NOT produce identical
#     cards. Only the MUST/contract items (input_spec, predict, pkl)
#     are rigid: the page plumbing depends on them.
# ============================================================================


# === GATE 1 -- "Wake the brain and design the form" ==========================
def step_1_wake_and_design():
    """Load titanic_model.pkl AND decide which attributes the form offers.

    MUST land: (a) a friendly 'the trained brain is awake' card including
    one example prediction on a fixed test passenger (a gauge is the
    natural reveal), and (b) the form plan -- for each attribute whether
    it is a radio/dropdown or slider, with sensible range/choices and a
    default -- shown as a table.
    Store: ARTIFACTS["input_spec"] (same shape as DEFAULT_INPUT_SPEC).
    If the trained brain is missing, return a kind note telling the
    student to finish Step 2 -- checkpoint 4 first (no crash!).
    """
    if not os.path.exists(MODEL_PATH):
        return (
            "The trained brain is not on disk yet. Finish **Step 2, "
            "checkpoint 4** (save titanic_model.pkl) first, then come back!"
        )
    with open(MODEL_PATH, "rb") as handle:
        artifact = pickle.load(handle)
    ARTIFACTS["artifact"] = artifact

    spec = [dict(item) for item in DEFAULT_INPUT_SPEC]
    ARTIFACTS["input_spec"] = spec
    form_table = pd.DataFrame(
        [
            {
                "Control": item["label"],
                "Type": item["kind"],
                "Range / choices": (
                    ", ".join(map(str, item["choices"]))
                    if item.get("choices")
                    else f"{item['min']} - {item['max']}"
                ),
                "Default": item["value"],
            }
            for item in spec
        ]
    )

    sample = pd.DataFrame(
        [[1, 1, 30, 0, 0, 100.0]], columns=artifact["feature_columns"]
    )
    probability = float(
        artifact["model"].predict_proba(artifact["scaler"].transform(sample))[0][1]
    )
    return {
        "text": (
            "The brain is awake -- a 30-year-old woman in first class would "
            f"have had a **{probability:.0%}** chance of surviving. The form "
            "asks six questions, all about things the model actually learned "
            "from -- nothing it never saw."
        ),
        "dataframe": form_table,
        "chart": workshop_steps.chart(
            kind="gauge",
            value=round(probability * 100, 1),
            title="Sample passenger: survival chance",
        ),
    }


# === GATE 2 -- "Wire the prediction, kindly" =================================
def step_2_wire_and_kinder_verdicts():
    """Make the form actually predict, with gentle wording.

    MUST (per the gate contract):
      * read and use ARTIFACTS["input_spec"] labels,
      * encode 'Sex' back to numbers exactly like the model was trained,
      * scale the numbers with the stored scaler BEFORE predicting,
      * define three probability bands (e.g. unlikely / close call /
        likely) and show them as a table,
      * store `ARTIFACTS["predict"] = my_predict_function`, where the
        function takes values_dict and returns
        workshop_steps.verdict(text, probability, band) -- the page then
        draws the animated survival gauge and the kinder wording itself,
      * confirm with one live example on REAL model output (not mock
        text); a text sentence plus a gauge is perfect.
    """
    artifact = ARTIFACTS.get("artifact")
    if artifact is None:
        return "Wake the brain first (checkpoint 1)."

    model = artifact["model"]
    scaler = artifact["scaler"]
    features = artifact["feature_columns"]
    spec = ARTIFACTS.get("input_spec", DEFAULT_INPUT_SPEC)

    label_to_feature = {
        "Ticket class": "Pclass",
        "Sex": "Sex",
        "Age": "Age",
        "Siblings/spouses aboard": "SibSp",
        "Parents/children aboard": "Parch",
        "Ticket fare (pounds, 1912)": "Fare",
    }

    def _score(values_dict):
        row = {"Pclass": 3, "Sex": 0, "Age": 25.0, "SibSp": 0, "Parch": 0, "Fare": 30.0}
        for label, value in values_dict.items():
            feature = label_to_feature.get(label, label)
            if feature == "Sex":
                value = 1 if str(value).lower() == "female" else 0
            if feature in row:
                row[feature] = value
        frame = pd.DataFrame([[row[name] for name in features]], columns=features)
        return float(model.predict_proba(scaler.transform(frame))[0][1])

    bands = pd.DataFrame(
        [
            {"Chance": "below 35%", "Band": "unlikely",
             "Wording": "the odds were against this passenger"},
            {"Chance": "35-65%", "Band": "close call",
             "Wording": "this one is too close to call"},
            {"Chance": "above 65%", "Band": "likely",
             "Wording": "this passenger had a real chance"},
        ]
    )

    def _predict(values_dict):
        probability = _score(values_dict)
        if probability < 0.35:
            band = "unlikely"
        elif probability < 0.65:
            band = "close call"
        else:
            band = "likely"
        tone = bands.loc[bands["Band"] == band, "Wording"].iloc[0]
        return workshop_steps.verdict(
            f"Model estimate: {probability:.0%} chance of surviving -- {tone}.",
            probability,
            band,
        )

    ARTIFACTS["score"] = _score
    ARTIFACTS["predict"] = _predict

    example = _predict({item["label"]: item["value"] for item in spec})
    return {
        "text": (
            example["text"]
            + " The pipeline on every click: encode the form words exactly as "
            "Stage 2 did, scale with the stored scaler, then predict."
        ),
        "dataframe": bands,
        "chart": workshop_steps.chart(
            kind="gauge",
            value=round(example["probability"] * 100, 1),
            title="Live example with the kinder wording",
        ),
    }


# === GATE 3 -- "Black-box the brain" =========================================
def step_3_black_box_tests():
    """Probe the model with imaginary passengers and discuss unfairness.

    MUST: at least 6 imaginary passengers who differ sharply, each with
    their live verdict, plus 2-3 plain-English questions for class
    discussion (is any pattern unfair? what does the model NOT see?).
    CHOOSE freely: table + bar chart of survival probabilities is one
    strong shape; a "case files" style card, a comparison matrix, or
    provocative pairs (same person, one attribute flipped) also work --
    pick the staging that sparks the argument.
    """
    if "predict" not in ARTIFACTS:
        return "Wire the prediction first (checkpoint 2)."

    spec = ARTIFACTS.get("input_spec", DEFAULT_INPUT_SPEC)
    base = {item["label"]: item["value"] for item in spec}
    passengers = [
        ("Girl, 5, 1st class", {**base, "Sex": "female", "Age": 5, "Ticket class": 1}),
        ("Boy, 5, 3rd class", {**base, "Sex": "male", "Age": 5, "Ticket class": 3}),
        ("Woman, 30, 3rd class", {**base, "Sex": "female", "Age": 30, "Ticket class": 3}),
        ("Man, 30, 1st class", {**base, "Sex": "male", "Age": 30, "Ticket class": 1}),
        ("Man, 60, 1st class", {**base, "Sex": "male", "Age": 60, "Ticket class": 1}),
        ("Woman, 60, 3rd class", {**base, "Sex": "female", "Age": 60, "Ticket class": 3}),
    ]

    results = [(name, ARTIFACTS["predict"](values)) for name, values in passengers]

    table = pd.DataFrame(
        [
            {
                "Imaginary passenger": name,
                "Survival chance": f"{verdict['probability']:.0%}",
                "Band": verdict.get("band") or "-",
            }
            for name, verdict in results
        ]
    )
    chart_data = pd.DataFrame(
        {
            "Passenger": [name for name, _ in results],
            "Survival chance": [
                round(verdict["probability"] * 100, 1) for _, verdict in results
            ],
        }
    )
    return {
        "text": (
            "**Discussion:** is it fair that the model leans on sex and class? "
            "The model never saw fairness -- it only mirrored 1912. What could "
            "it NOT know (health, deck location, luck)?"
        ),
        "dataframe": table,
        "chart": workshop_steps.chart(
            kind="bar",
            data=chart_data,
            x="Passenger",
            y="Survival chance",
            horizontal=True,
            y_label="Chance (%)",
            title="Survival chances of imaginary passengers",
        ),
    }


# ============================================================================
# STEP DESCRIPTIONS (web page reads this).
# ============================================================================
STEPS = [
    {
        "number": 1,
        "title": "Wake the brain and design the form",
        "story": (
            "Your Step 2 work saved a trained brain on disk. Wake it up and "
            "check it gives sensible guesses -- then design the passenger "
            "form classmates will play with: radios for ticket class and sex, "
            "sliders for the numbers, all with human-friendly ranges."
        ),
        "prompt": (
            "Bring one passenger to life in your head (their age, class, sex) "
            "and describe them to the AI. Ask it to wake the frozen brain from "
            "titanic_model.pkl, predict YOUR passenger, and show the chance as "
            "a gauge -- and if the file is missing, have it explain kindly "
            "which Step 2 checkpoint must come first instead of crashing. Then "
            "sketch the form like a designer: which control suits each "
            "attribute, and what sensible range? Ask the AI to build the form "
            "to your design and store the plan where the page can find it."
        ),
        "hints": [
            "The file only exists once Stage 2's last checkpoint is done -- "
            "the page should say so kindly, not crash.",
            "Ticket class and sex suit dropdowns/radios; age and fare suit "
            "sliders.",
            "Think about sensible ranges: ages 0-80? classes 1/2/3?",
            "The plan must be stored where the page can find it -- say so in "
            "your request.",
        ],
        "context": pd.DataFrame(
            [
                {"Field": "Pclass", "Example value": "1, 2 or 3"},
                {"Field": "Sex", "Example value": "male / female"},
                {"Field": "Age", "Example value": "22.0 (babies to 80)"},
                {"Field": "SibSp", "Example value": "0-8"},
                {"Field": "Parch", "Example value": "0-6"},
                {"Field": "Fare", "Example value": "7.25-512.33"},
                {"Field": "Embarked", "Example value": "S / C / Q"},
            ]
        ),
        "guide": (
            "**Reusing a saved model is the industry norm: train once, predict "
            "everywhere.** The brain on disk is exactly the one that scored "
            "~80% on its hidden exam. And a good form hides the machinery: "
            "classmates will use it without ever seeing a number pipeline.\n\n"
            "*Discuss:* what should an app do when a dependency is missing? "
            "Crashing is easy; a kind message is design. And which attribute "
            "would you REMOVE from the form to keep it friendly?\n\n"
            "*Next up:* wire the form to the brain so Predict actually "
            "predicts."
        ),
        "reference": (
            "Step 3 of the workshop, checkpoint 1: load the saved model "
            "titanic_model.pkl and prove it is alive by predicting one fixed "
            "test passenger, showing the survival chance as a gauge; if the "
            "file is missing, tell me kindly which Step 2 checkpoint to finish "
            "first instead of crashing. Then propose the passenger web form -- "
            "for each attribute tell me if it should be a dropdown/radio or a "
            "slider and what sensible range or choices to give it -- and store "
            "this plan where the page can find it."
        ),
        "reference_alt": (
            "Load titanic_model.pkl and predict one fixed passenger with it, "
            "showing a gauge; if the file is missing, show a kind message "
            "pointing to Stage 2's last checkpoint. Then propose the passenger "
            "form: for each field pick a dropdown/radio or slider with "
            "sensible ranges, and store the plan where the page can use it."
        ),
        "experiment": (
            "Ask the AI to wake the brain twice and predict the same passenger "
            "both times -- are the answers identical? Then ask what happens if "
            "a user drags the age slider to 110. Should the form allow "
            "impossible values?"
        ),
        "fn": "step_1_wake_and_design",
        "placeholder": (
            "e.g. “Wake the trained model and design the passenger form…”"
        ),
    },
    {
        "number": 2,
        "title": "Wire the prediction, kindly",
        "story": (
            "Time to connect the form to the brain: press predict, and the "
            "model's guess appears as an animated gauge. Remember the model "
            "was trained on numbers, so 'female' must turn back into its coded "
            "digit before reaching the model. Then choose gentle wording for "
            "the verdict."
        ),
        "prompt": (
            "First say what could go WRONG if the form hands 'female' straight "
            "to a model that expects Stage 2's digits. Then ask the AI to wire "
            "the form to the brain -- encode exactly like Stage 2, apply the "
            "stored scaler -- so Predict produces a live survival gauge, and "
            "have it prove the pipeline with one live example. Finally, choose "
            "three friendly bands (what should they be called, and where does "
            "'close call' begin and end?) and have it reword the verdicts to "
            "your bands."
        ),
        "hints": [
            "The form's words (female/male) must become numbers EXACTLY the "
            "way Stage 2 chose.",
            "The stored scaler must be applied before predicting -- same rule "
            "as training time.",
            "A cold '0.34' can sting -- these were real people. Unlikely / "
            "close call / likely is one set; make them your own.",
            "Ask for one live example straight from the model to prove it's "
            "real.",
        ],
        "context": (
            "**The pipeline that will run on every click (same three moves as "
            "Stage 2, now automatic):**\n\n"
            "1. **encode** -- form words -> the exact digits Stage 2 chose\n"
            "2. **scale** -- squeeze the numbers with the SAME scaler from the "
            "freezer\n"
            "3. **predict** -- the model answers with a probability\n\n"
            "One mismatched digit or unscaled number = quietly wrong answers. "
            "Then translate that probability into human words: 0.34 -> 34% -> "
            "roughly one passenger in three."
        ),
        "guide": (
            "**The full pipeline runs on every click: translate words -> scale "
            "-> predict.** It's the exact journey of Stage 2, now invisible "
            "and instant. Machine-learning output is a number; how you present "
            "it is a human decision -- wording is part of the interface, not "
            "decoration.\n\n"
            "*Discuss:* what happens if the form's encoding drifts even "
            "slightly from training-time encoding? Could kinder wording ever "
            "mislead someone?\n\n"
            "*Next up:* the final checkpoint -- stress-test the whole system "
            "like a scientist."
        ),
        "reference": (
            "Step 3, checkpoint 2: connect the form to the model so the "
            "prediction button works. Encode the Sex choices back to numbers "
            "exactly like Step 2 did, use the stored scaler, and show the "
            "survival probability as a gauge with a human sentence. Show me "
            "one live example straight from the model. Then make the wording "
            "gentler -- define three probability bands (e.g. unlikely, close "
            "call, likely) and reword the verdicts, re-running one example to "
            "show the friendlier message."
        ),
        "reference_alt": (
            "Connect the form to the saved model: encode sex exactly as "
            "trained, apply the scaler, and show each prediction as a gauge "
            "with one human sentence. Then sort the chances into three "
            "friendly bands, reword the verdicts, and demo one on the live "
            "model."
        ),
        "experiment": (
            "Predict the same passenger twice through the form -- identical "
            "gauge both times? If not, ask the AI what's leaking. Then ask it "
            "to show the SAME probability worded in all three bands -- where "
            "does 'close call' start and end?"
        ),
        "fn": "step_2_wire_and_kinder_verdicts",
        "placeholder": (
            "e.g. “Wire the form to the model, then soften the verdict "
            "wording…”"
        ),
    },
    {
        "number": 3,
        "title": "Black-box the brain",
        "story": (
            "Final curiosity run: feed the brain imaginary passengers and "
            "discuss whether the patterns are FAIR. A model is a mirror of its "
            "data, nothing more."
        ),
        "prompt": (
            "Pick the unfairness you most want the class to SEE (a 1912 "
            "pattern that rings wrong today). Design six imaginary passengers "
            "around it -- which attributes to vary, which to hold still -- "
            "then ask the AI to run them through the live model as a table "
            "plus a bar chart of survival chances, ending with fairness "
            "questions to argue about."
        ),
        "hints": [
            "Make them differ sharply: young/old, women/men, 1st/3rd class.",
            "Change ONE thing at a time so a fairness argument stays clean.",
            "Ask for the verdicts as a table AND a chart of survival chances.",
            "Finish with 2-3 fairness questions the class can argue about.",
        ],
        "context": (
            "**Scientist's trick for this checkpoint -- change ONE thing at a "
            "time.** The dials your imaginary passengers can vary:\n\n"
            "- sex - ticket class - age (young/old) - fare (cheap/expensive) "
            "- family aboard (yes/no)\n\n"
            "If you change two things at once and the verdict moves, you can't "
            "tell which one did it. Fairness arguments need clean comparisons."
        ),
        "guide": (
            "**The model is a mirror of its data, nothing more.** It rewarded "
            "the patterns of 1912 -- including the unfair ones. It cannot see "
            "courage, luck, or the lifeboat queue.\n\n"
            "*Discuss:* is it fair to predict someone's survival from their "
            "sex or ticket class? What does the model NOT know? And where else "
            "in today's world do models quietly inherit yesterday's biases?\n\n"
            "**That's the whole workshop** -- you met data, trained a model, "
            "and interrogated it. This discussion is the real graduation."
        ),
        "reference": (
            "Step 3, checkpoint 3 (final!): test the live model with at least "
            "six imaginary passengers (young/old, women/men, 1st/3rd class), "
            "show their verdicts in a table AND as a bar chart of their "
            "survival chances, and give me two or three discussion questions "
            "about fairness and what the data cannot tell us."
        ),
        "reference_alt": (
            "Test the model with six or more very different imaginary "
            "passengers, chart their survival odds, and give the class 2-3 "
            "fairness questions to argue about."
        ),
        "experiment": (
            "Flip ONE attribute at a time (same person, female->male, then "
            "1st->3rd class) -- how far does the verdict move? Which single "
            "attribute moves it most?"
        ),
        "fn": "step_3_black_box_tests",
        "placeholder": (
            "e.g. “Test the model with very different imaginary passengers and "
            "help us judge it fairly…”"
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

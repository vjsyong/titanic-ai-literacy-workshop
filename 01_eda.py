"""01_eda.py -- Step 1 "Meet the Data" (First-year AI Literacy Workshop)

THE STEP-BY-STEP EXPERIENCE
    This script is a scaffold of six progressive checkpoints (gates).
    The class starts with STEPS_COMPLETED = 0: on the web page, students
    see the intro, the NEXT checkpoint's prompt hint, and locked slots
    for the rest. Each time a student asks their AI Teaching Assistant
    to unlock one step, the assistant:

        1. fills the step function's body -- ONLY inside that step's
           `# === GATE n ===` markers,
        2. runs `python 01_eda.py` in the terminal to prove it works,
        3. bumps STEPS_COMPLETED to that step's number -- nothing else.

    Because the page is served with `gradio 04_classroom.py`, the saved
    file hot-reloads and the page reveals the next magic sentence.

    Students never type code. The AI assistant never types more than
    one checkpoint at a time (see AGENTS.md STOP-FIRST RULE).

HOW TO RUN
    python 01_eda.py        (terminal checklist view)
    gradio 01_eda.py        (single-page web view)
"""

import os

import matplotlib

matplotlib.use("Agg")  # draw charts to files (no popup window)
import matplotlib.pyplot as plt
import pandas as pd

# ----------------------------------------------------------------------------
# DATA PATH -- never change or move this file
# ----------------------------------------------------------------------------
DATA_PATH = os.path.join("data", "titanic.csv")

# ----------------------------------------------------------------------------
# OUTPUT FOLDER for charts
# ----------------------------------------------------------------------------
OUTPUT_DIR = "eda_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------------------------------------------------
# PROGRESS COUNTER -- the ONLY number the AI assistant bumps in class,
# strictly one step at a time, AFTER it proved the step works.
# ----------------------------------------------------------------------------
STEPS_COMPLETED = 0


# ============================================================================
# CHECKPOINT GATES -- student + AI edit zone
# ============================================================================
# Rules for the AI assistant:
#   * Implement ONE gate per student request: fill the step function body
#     below its `# === GATE n ===` marker, never earlier, never later.
#   * Each function returns web-ready content: text, a DataFrame, a chart
#     path, or a dict like {"text": ..., "dataframe": ..., "image": ...}.
#   * Charts must be saved into OUTPUT_DIR (so the CLI keeps the history).
#   * When python 01_eda.py runs cleanly, bump STEPS_COMPLETED to n.
#   * NEVER touch a future gate. If the student asks, apply the workshop
#     STOP-FIRST RULE instead of implementing.
# ============================================================================


# === GATE 1 -- "Open the passenger list" ====================================
def step_1_open_the_list():
    """Load data/titanic.csv with pandas, count and peek.

    LOOK LIKE (web): a friendly sentence with the number of passengers and
    the details each row carries, plus a small preview table (head).
    """
    raise NotImplementedError("Gate 1 is not built yet")


# === GATE 2 -- "Where are the holes?" =======================================
def step_2_find_missing_values():
    """Show how many missing values each column has.

    LOOK LIKE (web): a small table of column -> number of holes.
    NOTE for the classroom: data/titanic.csv is pre-cleaned on purpose,
    so a nice discussion question is: 'if there are no holes, who filled
    them and why does that matter for a model?'
    """
    raise NotImplementedError("Gate 2 is not built yet")


# === GATE 3 -- "Did you survive?" ===========================================
def step_3_survival_overview():
    """Count survivors vs non-survivors and their shares.

    LOOK LIKE (web): a tiny table (Perished vs Survived, counts and %).
    TIP: the student should GUESS the split out loud first.
    """
    raise NotImplementedError("Gate 3 is not built yet")


# === GATE 4 -- "Survival by sex" ============================================
def step_4_survival_by_sex():
    """Bar chart: survival counts split by male/female.

    LOOK LIKE (web): the chart image plus one friendly caption sentence.
    MUST save the chart to OUTPUT_DIR/survival_chart.png exactly.
    """
    raise NotImplementedError("Gate 4 is not built yet")


# === GATE 5 -- "Survival by ticket class" ===================================
def step_5_survival_by_class():
    """Bar chart of survival counts split by Pclass 1/2/3.

    LOOK LIKE (web): another chart image plus a caption sentence.
    MUST save the chart to OUTPUT_DIR/class_chart.png exactly.
    """
    raise NotImplementedError("Gate 5 is not built yet")


# === GATE 6 -- "The age story" ==============================================
def step_6_age_patterns():
    """Explore age as a survival pattern (e.g. survival by age group).

    LOOK LIKE (web): one chart of your choice about age plus one
    plain-English takeaway sentence the class can discuss.
    Save the chart into OUTPUT_DIR/ with a clear file name you pick.
    """
    raise NotImplementedError("Gate 6 is not built yet")


# ============================================================================
# STEP DESCRIPTIONS -- the web page reads this list. Keep the wording
# friendly and classroom-facing.
# ============================================================================
STEPS = [
    {
        "number": 1,
        "title": "Open the passenger list",
        "story": (
            "Every row is a real person from 1912: their ticket class, sex, "
            "age, family aboard, fare, and where they embarked. Meet the "
            "data before you judge it!"
        ),
        "prompt": (
            "Please open the Titanic passenger list (data/titanic.csv), "
            "tell me how many passengers it holds and what details we know "
            "about each person, and show me the first few rows as a table."
        ),
        "fn": "step_1_open_the_list",
    },
    {
        "number": 2,
        "title": "Where are the holes?",
        "story": (
            "Real-world data is messy. If a table has holes (missing "
            "values), a learning model can stumble -- or worse, silently "
            "guess."
        ),
        "prompt": (
            "Check data/titanic.csv for missing values in every column and "
            "show me a table of how many holes each column has."
        ),
        "fn": "step_2_find_missing_values",
    },
    {
        "number": 3,
        "title": "Did you survive?",
        "story": (
            "One column decides everything: Survived (1 = made it, 0 = did "
            "not). Before seeing the answer, make a guess: did MORE or "
            "FEWER than half of the passengers survive?"
        ),
        "prompt": (
            "Count how many passengers perished and how many survived, and "
            "show me both numbers with their percentages."
        ),
        "fn": "step_3_survival_overview",
    },
    {
        "number": 4,
        "title": "Survival by sex",
        "story": (
            "Now we look for our FIRST pattern: did female passengers "
            "survive more often than male passengers?"
        ),
        "prompt": (
            "Draw a bar chart comparing survival for female and male "
            "passengers, save it as eda_output/survival_chart.png, and "
            "describe the pattern in one friendly sentence."
        ),
        "fn": "step_4_survival_by_sex",
    },
    {
        "number": 5,
        "title": "Survival by ticket class",
        "story": (
            "Ticket class was a proxy for wealth and cabin location on "
            "board. Did the deck you slept on decide your fate?"
        ),
        "prompt": (
            "Draw a bar chart of survival by ticket class (1, 2, 3), save "
            "it as eda_output/class_chart.png, and tell me what stands "
            "out."
        ),
        "fn": "step_5_survival_by_class",
    },
    {
        "number": 6,
        "title": "The age story",
        "story": (
            "Kids first? Older folks last? Build one more picture about "
            "AGE -- this is the pattern the Step 2 model will learn from."
        ),
        "prompt": (
            "Make one chart that shows whether age is connected to "
            "survival (for example survival by age group), save it in "
            "eda_output/, and give me one plain-English takeaway."
        ),
        "fn": "step_6_age_patterns",
    },
]


# ============================================================================
# ORCHESTRATION -- function name and behavior contract (do not rename).
# ============================================================================
def analyze_data():
    """Runs every completed checkpoint in order (terminal-friendly view).

    Returns the loaded DataFrame, or None until Gate 1 exists.
    """
    titanic = None

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
        if isinstance(result, dict) and result.get("dataframe") is not None:
            titanic = result["dataframe"]  # handy for later gates

    if titanic is None:
        try:
            titanic = pd.read_csv(DATA_PATH)
        except (FileNotFoundError, NameError):
            return None
    return titanic


if __name__ == "__main__":
    print(
        "Terminal mode: running the completed checkpoints in order.\n"
        "For the step-by-step magic, serve with:  gradio 01_eda.py\n"
        "Or serve every workshop step at once:    gradio 04_classroom.py"
    )
    analyze_data()


# ============================================================================
# WEB INTERFACE -- pairs this script with a web page (Gradio).
# The web layer imports after the data layer on purpose. Do not move it
# above the CHECKPOINT GATES.
# ============================================================================
import gradio as gr  # noqa: E402
import workshop_steps  # noqa: E402


def build_eda_app():
    """Step 1 web page built entirely from the checkpoint scaffold."""
    return workshop_steps.make_app(
        title="1 - Meet the Data",
        intro=(
            "You are holding the real passenger list of the Titanic. Work "
            "through the checkpoints one prompt at a time with your AI "
            "Teaching Assistant and watch the picture come into focus."
        ),
        steps=STEPS,
        module_globals=globals(),
    )


demo = build_eda_app()

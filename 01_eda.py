"""01_eda.py -- Step 1 "Meet the Data" (First-year AI Literacy Workshop)

THE STEP-BY-STEP EXPERIENCE
    This script is a scaffold of three progressive checkpoints (gates).
    The class starts with STEPS_COMPLETED = 0: on the web page, students
    see the intro, the NEXT checkpoint's prompt hint, and locked slots
    for the rest. Each time a student asks their AI Teaching Assistant
    to unlock one step, the assistant:

        1. fills the step function's body -- ONLY inside that step's
           `# === GATE n ===` markers,
        2. runs `python 01_eda.py` in the terminal to prove it works,
        3. bumps STEPS_COMPLETED to that step's number -- nothing else.

    The workshop page (served by workshop_server.py) notices the saved
    file within a second and reveals the next magic sentence.

    Students never type code. The AI assistant never types more than
    one checkpoint at a time (see AGENTS.md STOP-FIRST RULE).

HOW TO RUN
    python 01_eda.py          (terminal checklist view)
    python serve_workshop.py  (the web page -- all three steps at once)
"""

import os

import pandas as pd

# Shared gate helpers: workshop_steps.chart(...) draws interactive charts
# on the page, workshop_steps.metric(...) shows headline numbers.
import workshop_steps

# ----------------------------------------------------------------------------
# DATA PATH -- never change or move this file
# ----------------------------------------------------------------------------
DATA_PATH = os.path.join("data", "titanic.csv")

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
#   * Each function returns web-ready content: text, a DataFrame (shown as
#     a table), or a dict combining {"text": ..., "dataframe": ...,
#     "chart": ..., "metric": ...}. Build charts with the shared helper:
#         workshop_steps.chart(kind="bar", data=df, x="Sex", y="Count")
#     Kinds: bar, pictorial (person icons), line, area, scatter, pie,
#     donut, histogram, gauge, heatmap.
#   * At most ONE "dataframe" and ONE "chart" per result -- if a checkpoint
#     needs two visuals, make the less interactive one a table.
#   * Write clear comments that break the code into small steps and explain
#     each one in plain English: students read this code in the page's
#     "See the code" panel.
#   * When python 01_eda.py runs cleanly, bump STEPS_COMPLETED to n.
#   * NEVER touch a future gate. If the student asks, apply the workshop
#     STOP-FIRST RULE instead of implementing.
#   * The LOOK LIKE notes are the MINIMUM, not a blueprint. Compose each
#     card your own way -- pick the chart kind, text and metric mix that
#     tells the story best. Two good assistants should NOT produce
#     identical cards. Only the MUST/contract items are rigid.
# ============================================================================


# === GATE 0 -- "Connect your assistant" ====================================
# Step 0 is the connection handshake. The AI Teaching Assistant's FIRST job
# in a fresh session is to prove it can reach this project: set PAIRED to
# True below, run `python 01_eda.py`, and the workshop page unlocks
# Checkpoint 1. This is the ONE edit allowed before the student asks for
# anything (see AGENTS.md "Step 0").
PAIRED = False


# === GATE 1 -- "Meet the passenger list" ====================================
def step_1_load_and_inspect():
    """Open data/titanic.csv, count and peek at the rows, then check every
    column for holes.

    MUST land: (a) the number of passengers and the columns we know about,
    (b) a small preview of the first rows as a table, and (c) the
    per-column missing-value counts, with the emptiest column obvious.

    CHOOSE freely: present the holes as a sorted bar chart, a table, or a
    completeness meter -- whatever makes the gaps visceral. (Only ONE
    dataframe and ONE chart per result: pick which is the table and which
    is the visual.)

    NOTE for the classroom: data/titanic.csv is the ORIGINAL 1912
    passenger list, holes and all. Age, Cabin and Embarked all have gaps
    -- Cabin is mostly empty. A nice discussion question is: 'why would
    cabin records be missing for so many passengers, and what should we
    do about holes before training a model?'

    The page renders pandas DataFrames as tables automatically:

        df = pd.read_csv(DATA_PATH)
        return {
            "text": f"The list holds {len(df)} passengers ...",
            "dataframe": df.head(),
            "chart": workshop_steps.chart(
                kind="bar", data=holes_df, x="Column", y="Missing",
                title="Holes per column",
            ),
        }
    """
    raise NotImplementedError("Gate 1 is not built yet")


# === GATE 2 -- "Who survived?" ==============================================
def step_2_survival_by_sex():
    """Count survivors vs non-survivors, then break survival down by sex.

    MUST land: (a) the overall perished-vs-survived counts AND shares, and
    (b) the female-vs-male survival comparison, plus ONE plain-English
    takeaway sentence (the pattern itself, not a chart description).

    CHOOSE freely: a table or donut for the overall split; person-icon
    bars, grouped bars, or stacked bars for the sex comparison. (Only ONE
    dataframe and ONE chart per result -- the sex comparison is the
    interesting visual, so make that the chart and the overall split the
    table.)

    TIP: the student should GUESS the split out loud first ("more or
    fewer than half?"), so a reveal-style card works nicely.

    Data wrinkle if useful: Survived is 0/1, so a
    groupby(["Sex","Survived"]).size().unstack() + renaming 0/1 to
    Perished/Survived is the standard shape-up.
    """
    raise NotImplementedError("Gate 2 is not built yet")


# === GATE 3 -- "Wealth and age" =============================================
def step_3_class_and_age():
    """Compare survival across ticket class AND explore the age pattern.

    MUST land: (a) survival compared across all three classes (1/2/3) with
    a caption of what stands out, and (b) one chart relating age to
    survival with a plain-English takeaway.

    CHOOSE freely: stacked/grouped bars or a rate-per-class pictorial for
    class; a zoomable scatter (Age vs Fare, colored by survival),
    age-group bars, or overlaid age histograms for age. (Only ONE chart
    per result: make the age relationship the interactive chart and the
    class comparison a table.)

    IMPORTANT (data-literacy moment, keep whatever you build): the
    returned text MUST end by inviting the class to judge the age chart
    itself: ask whether that chart type is really the right picture for
    891 people, and suggest asking the AI to propose something easier to
    read if it feels hard to interpret. Changing the chart type afterwards
    is encouraged -- it teaches that a graph is a design choice, not a
    given.
    """
    raise NotImplementedError("Gate 3 is not built yet")


# ============================================================================
# STEP DESCRIPTIONS -- the web page reads this list. Keep the wording
# friendly and classroom-facing.
# ============================================================================
STEPS = [
    {
        "number": 1,
        "title": "Meet the passenger list",
        "story": (
            "Every row is a real person from 1912: their ticket class, sex, "
            "age, family aboard, fare, and where they embarked. Before you "
            "judge the data, meet it -- and check it for holes."
        ),
        "prompt": (
            "Guess first: how many people are on this 1912 passenger list? "
            "Then ask the AI to open data/titanic.csv, show the first few "
            "rows, and count the missing values in each column. Was your guess "
            "close, and which column has the most holes?"
        ),
        "hints": [
            "The whole list is too many rows to read at once -- ask for a "
            "peek at just the first few.",
            "A missing value is an empty cell. Ask the AI to count them per "
            "column.",
            "One column is almost entirely empty. Guess which before you "
            "look!",
        ],
        "context": {
            "text": (
                "First, three real passengers so 'a hole' is concrete -- the "
                "empty cells are blank slots in the record. Then the big "
                "picture: most records are NOT fully complete."
            ),
            "dataframe": pd.DataFrame(
                [
                    {"PassengerId": 1, "Name": "Braund, Mr. Owen Harris",
                     "Age": 22.0, "Cabin": None, "Embarked": "S"},
                    {"PassengerId": 3, "Name": "Heikkinen, Miss. Laina",
                     "Age": 26.0, "Cabin": None, "Embarked": "S"},
                    {"PassengerId": 6, "Name": "Moran, Mr. James",
                     "Age": None, "Cabin": None, "Embarked": "Q"},
                    {"PassengerId": 18, "Name": "Williams, Mr. Charles Eugene",
                     "Age": None, "Cabin": None, "Embarked": "S"},
                ]
            ),
        },
        "guide": (
            "**891 real people, 12 facts each -- and the list is not "
            "complete.** Age is missing for ~177 passengers and Cabin for "
            "~687; Embarked is missing 2. Holes happen: unfinished records, "
            "lost paperwork.\n\n"
            "*Discuss:* why would cabin records be missing for so many? And "
            "what should we do about holes before a model learns from them -- "
            "fill them in, or drop them?\n\n"
            "*Next up:* the column every prediction cares about -- Survived."
        ),
        "reference": (
            "Please open the Titanic passenger list (data/titanic.csv), tell "
            "me how many passengers it holds and what details we know about "
            "each person, and show me the first few rows as a table. Then "
            "check every column for missing values and show me how many holes "
            "each one has, with the emptiest column obvious."
        ),
        "reference_alt": (
            "Load data/titanic.csv with pandas and show me the number of "
            "passengers, the column names, and a preview of the first five "
            "rows. Then count the missing values in each column and show me "
            "which column has the most holes."
        ),
        "experiment": (
            "Ask the AI to double-check one column's hole count a second way "
            "(e.g. counting the cells that ARE filled, 891 minus that). Do "
            "both methods agree?"
        ),
        "fn": "step_1_load_and_inspect",
        "placeholder": (
            "e.g. “Open the passenger list, show me a preview, and tell me "
            "which columns have holes…”"
        ),
    },
    {
        "number": 2,
        "title": "Who survived?",
        "story": (
            "One column decides everything: Survived (1 = made it, 0 = did "
            "not). Before seeing the answer, make a guess: did MORE or FEWER "
            "than half of the passengers survive?"
        ),
        "prompt": (
            "Finish this sentence: 'I think about ___ % of passengers "
            "survived.' Then ask the AI to show the real counts and "
            "percentages, and to draw the survival comparison between women "
            "and men. Was your guess close?"
        ),
        "hints": [
            "First guess: did MORE or FEWER than half survive? No peeking!",
            "Ask for both the raw counts and the percentages.",
            "The page can draw eye-catching person-icon bars for the "
            "female-vs-male comparison -- try asking for those.",
            "Insist on one plain-English sentence saying what the pattern IS.",
        ],
        "context": None,
        "guide": (
            "**Only ~38% survived -- 342 of 891.** Most students guess 50/50, "
            "so the real split usually surprises the class. And the 38% hides "
            "the real story: **~74% of women survived vs ~19% of men**. "
            "'Women and children first' was real.\n\n"
            "*Discuss:* why might our gut guess be too optimistic? (Movies "
            "center on the survivors!) And if you had to bet on ONE passenger "
            "surviving with only one fact allowed, which fact would you pick?\n\n"
            "*Next up:* the split changes again with wealth -- and with age."
        ),
        "reference": (
            "Count how many passengers perished and how many survived in "
            "data/titanic.csv, and show me both numbers with their "
            "percentages. Then draw a chart comparing survival for female and "
            "male passengers -- make it fun to look at, the page can draw "
            "person-icon bars -- and describe the pattern in one friendly "
            "sentence."
        ),
        "reference_alt": (
            "What fraction of passengers survived, according to "
            "data/titanic.csv? Show survivors and victims in numbers and in "
            "percent, then compare survival rates for women and men in one "
            "visual with a single takeaway sentence."
        ),
        "experiment": (
            "Ask the AI to redraw the same female-vs-male comparison in a "
            "different style (bars instead of person icons, or the reverse). "
            "Which version tells the story better?"
        ),
        "fn": "step_2_survival_by_sex",
        "placeholder": (
            "e.g. “Count how many survived and how many didn't, then compare "
            "women and men…”"
        ),
    },
    {
        "number": 3,
        "title": "Wealth and age",
        "story": (
            "Ticket class was a proxy for wealth and cabin location on board; "
            "age added another clue. Build one picture of each -- then judge "
            "whether the pictures are actually easy to read."
        ),
        "prompt": (
            "Rank the three ticket classes first: which one survived best, and "
            "which worst? Then ask the AI to show survival by class and to "
            "build ONE chart linking age to survival. Compare both with your "
            "ranking, and judge the age chart: is it easy to read for 891 "
            "people? If not, ask for a clearer chart and give the takeaway in "
            "your own words."
        ),
        "hints": [
            "A stacked or grouped bar chart makes the three classes easy to "
            "compare.",
            "Age versus fare on a zoomable scatter, colored by survival, is "
            "one way to see the age story -- but ask whether it is the "
            "clearest choice for 891 people.",
            "If it looks messy, ask the AI for age-group bars or a histogram "
            "instead.",
        ],
        "context": {
            "text": (
                "Before relating AGE to anything, meet the age crowd itself -- "
                "KNOW YOUR VARIABLE first (a data-scientist habit). Passengers "
                "per decade of age: how does the ship lean? Then decide with "
                "the AI how to picture age vs survival."
            ),
            "chart": workshop_steps.chart(
                kind="bar",
                title="Know the variable: passengers per decade of age",
                data=[
                    {"Age group": "0–9", "Passengers": 62},
                    {"Age group": "10–19", "Passengers": 102},
                    {"Age group": "20–29", "Passengers": 220},
                    {"Age group": "30–39", "Passengers": 167},
                    {"Age group": "40–49", "Passengers": 89},
                    {"Age group": "50–59", "Passengers": 48},
                    {"Age group": "60–69", "Passengers": 19},
                    {"Age group": "70+", "Passengers": 7},
                ],
                x="Age group",
                y="Passengers",
            ),
        },
        "guide": (
            "**Wealth shows: ~63% of 1st class survived, ~47% of 2nd, ~24% "
            "of 3rd.** And on age: **children had better odds; elderly "
            "passengers the worst -- but age is a weaker pattern than sex or "
            "class.** Notice the age chart itself: with 891 people it gets "
            "crowded.\n\n"
            "*Discuss:* does the class chart alone PROVE wealth was the "
            "cause, or could something else explain it? (Careful: correlation "
            "isn't causation.) And is a scatter the right graph for age, or is "
            "changing the chart type a design choice, not cheating?\n\n"
            "*Next up:* Stage 2 -- a machine learns these patterns and turns "
            "them into predictions."
        ),
        "reference": (
            "Draw a chart of survival by ticket class (1, 2, 3) and tell me "
            "what stands out. Then make one chart that shows whether age is "
            "connected to survival (for example a zoomable scatter of age "
            "versus fare, colored by survival), give me one plain-English "
            "takeaway, and tell me whether that chart type was a good choice "
            "for this data or suggest an easier-to-read alternative."
        ),
        "reference_alt": (
            "Group data/titanic.csv by ticket class and show me the survival "
            "percentage for each of the three classes. Then show one clear "
            "chart linking age to survival and finish with a single takeaway "
            "sentence about the age pattern."
        ),
        "experiment": (
            "Ask the AI for an easier-to-read age chart (say, age-group bars "
            "instead of a scatter) -- did changing the design change what the "
            "class can actually see?"
        ),
        "fn": "step_3_class_and_age",
        "placeholder": (
            "e.g. “Show survival by ticket class, then one chart linking age "
            "to survival…”"
        ),
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
        "For the step-by-step web page:  python serve_workshop.py"
    )
    analyze_data()


# ============================================================================
# PAGE METADATA -- the tab title and intro the workshop page shows.
# ============================================================================
PAGE = {
    "id": "eda",
    "title": "1 - Meet the Data",
    "intro": (
        "You are holding the real passenger list of the Titanic. Work "
        "through the checkpoints one prompt at a time with your AI "
        "Teaching Assistant and watch the picture come into focus."
    ),
}

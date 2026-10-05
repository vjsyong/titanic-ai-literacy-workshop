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


# === GATE 1 -- "Open the passenger list" ====================================
def step_1_open_the_list():
    """Load data/titanic.csv with pandas, count and peek.

    LOOK LIKE (web): a friendly sentence with the number of passengers and
    the details each row carries, plus a small preview table (head).

    The page renders pandas DataFrames as tables automatically:

        df = pd.read_csv(DATA_PATH)
        return {
            "text": f"The list holds {len(df)} passengers ...",
            "dataframe": df.head(),
        }
    """
    raise NotImplementedError("Gate 1 is not built yet")


# === GATE 2 -- "Where are the holes?" =======================================
def step_2_find_missing_values():
    """Show how many missing values each column has.

    MUST land: the per-column hole counts, with the emptiest column
    impossible to miss.
    CHOOSE freely: a table, a sorted bar chart, a "completeness meter",
    whatever makes gaps visceral for a first-year audience.

    NOTE for the classroom: data/titanic.csv is the ORIGINAL 1912
    passenger list, holes and all (Age, Cabin and Embarked all have
    gaps -- Cabin is mostly empty). A nice discussion question is:
    'why would cabin records be missing for so many passengers, and
    what should we do about holes before training a model?'
    """
    raise NotImplementedError("Gate 2 is not built yet")


# === GATE 3 -- "Did you survive?" ===========================================
def step_3_survival_overview():
    """Count survivors vs non-survivors and their shares.

    MUST land: the perished-vs-survived counts AND percentages.
    CHOOSE freely: table, pie, donut, gauge, a metric ring pair --
    whatever dramatizes "fewer than half made it". (TIP: the student
    should GUESS the split out loud first, so a reveal-style card works
    nicely.)
    """
    raise NotImplementedError("Gate 3 is not built yet")


# === GATE 4 -- "Survival by sex" ============================================
def step_4_survival_by_sex():
    """Chart of survival counts split by male/female.

    MUST land: the female-vs-male survival comparison, plus ONE
    plain-English takeaway sentence (the pattern itself, not a chart
    description).
    CHOOSE freely: person-icon pictorial bars, side-by-side or stacked
    bars, percentages vs raw counts, a metric per group -- your call.
    Data wrinkle if useful: Survived is 0/1, so a
    groupby(["Sex","Survived"]).size().unstack() + renaming is the
    standard shape-up; how you present it is up to you.
    """
    raise NotImplementedError("Gate 4 is not built yet")


# === GATE 5 -- "Survival by ticket class" ===================================
def step_5_survival_by_class():
    """Chart of survival counts split by Pclass 1/2/3.

    MUST land: survival compared across all three classes, plus a
    caption of what stands out.
    CHOOSE freely: stacked bars, grouped bars, a survival-rate-per-class
    pictorial, percentages or counts. Data wrinkle: same 0/1 Survived
    shape-up as the previous gate; rename 0/1 to Perished/Survived.
    """
    raise NotImplementedError("Gate 5 is not built yet")


# === GATE 6 -- "The age story" ==============================================
def step_6_age_patterns():
    """Explore age as a survival pattern with one interactive chart.

    MUST land: one chart about age & survival, plus one plain-English
    takeaway sentence the class can discuss.
    CHOOSE freely: zoomable scatter (Age vs Fare, colored by survival),
    age-group bars, overlaid age histograms, a "children vs adults"
    pictorial -- pick what you think reads best for this crowd.

    IMPORTANT (data-literacy moment, keep whatever you build): the
    returned text MUST end by inviting the class to judge the chart
    itself: ask them whether that chart type is really the right
    picture for 891 people, and suggest asking the AI Teaching
    Assistant to propose something easier to read if it feels hard to
    interpret. Changing the chart type afterwards is encouraged -- it
    teaches that a graph is a design choice, not a given.
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
            "First write down a guess: how many people do you expect on a 1912 passenger list? Now "
            "have the AI open data/titanic.csv and show you a small preview - how close was your "
            "guess? Did the real list hold more or fewer?"
        ),
        "hints": [
            "All 891 rows is too many to read at once — how would you ask "
            "for just a peek at the first few?",
            "Ask how many passengers the list holds in total.",
            "Ask what details (columns) we know about each person.",
        ],
        "guide": (
            "**891 real people, 12 facts each.** Every row is one passenger "
            "who sailed in 1912; the columns (class, sex, age, fare…) are "
            "what a data scientist calls *features*.\n\n"
            "*Discuss:* which of these 12 facts do you think mattered most "
            "for surviving that night? Keep your bet — the coming "
            "checkpoints will test it.\n\n"
            "*Next up:* before trusting the table, we'll check it for holes."
        ),
        "reference": (
            "Please open the Titanic passenger list (data/titanic.csv), "
            "tell me how many passengers it holds and what details we know "
            "about each person, and show me the first few rows as a table."
        ),
        "reference_alt": (
            "Load data/titanic.csv with pandas and show me the number of "
            "passengers, the column names, and a preview of the first "
            "five rows."
        ),
        "experiment": (
            "Ask the AI to show the LAST few rows instead of the first "
            "few — does anything at the end of the list surprise you?"
        ),
        "context": {
            "text": (
                "A taster of what this table can answer: where the 891 "
                "passengers boarded. You can hover the slices."
            ),
            "chart": workshop_steps.chart(
                kind="donut",
                title="Where they boarded",
                data=[
                    {"Port": "Southampton (S)", "Passengers": 644},
                    {"Port": "Cherbourg (C)", "Passengers": 168},
                    {"Port": "Queenstown (Q)", "Passengers": 77},
                ],
                x="Port",
                y="Passengers",
            ),
        },
        "fn": "step_1_open_the_list",
        "placeholder": (
            "e.g. “Open the passenger list and give me a small preview of "
            "what's in it…”"
        ),
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
            "Which column do YOU suspect is almost completely empty? Say your suspect out loud, "
            "then ask the AI to count the holes in every column and reveal the emptiest. Was your "
            "hunch right - and either way, ask why those cells went missing."
        ),
        "hints": [
            "A missing value is an empty cell — the AI knows how to count "
            "them per column.",
            "One column is almost entirely empty. Guess which before you "
            "look!",
            "Ask for the emptiest column to jump out of the table.",
        ],
        "context": {
            "text": (
                "First, three real passengers so 'a hole' is concrete — "
                "the — cells are empty slots in the record. Then the big "
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
            "chart": workshop_steps.chart(
                kind="donut",
                title="Records in this table",
                data=[
                    {"Record": "filled in completely", "Count": 183},
                    {"Record": "has at least one hole", "Count": 708},
                ],
                x="Record",
                y="Count",
            ),
        },
        "guide": (
            "**Real data is messy: Age is missing for ~177 passengers and "
            "Cabin for ~687.** Holes happen — unfinished records, lost "
            "paperwork.\n\n"
            "*Discuss:* why would cabin records be missing for so many? "
            "And what should we do about holes before a model learns from "
            "them — fill them in, or drop them?\n\n"
            "*Next up:* the column every prediction cares about — Survived."
        ),
        "reference": (
            "Check data/titanic.csv for missing values in every column and "
            "show me a table of how many holes each column has."
        ),
        "reference_alt": (
            "Tell me which columns in data/titanic.csv have missing "
            "values and how many, ordered from most incomplete to least."
        ),
        "experiment": (
            "Ask the AI to double-check one column's hole count a second "
            "way (e.g. counting the cells that ARE filled, 891 minus "
            "that). Do both methods agree?"
        ),
        "fn": "step_2_find_missing_values",
        "placeholder": (
            "e.g. “Check the passenger list for holes in the data and "
            "show me where they are…”"
        ),
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
            "First finish this sentence out loud: 'I think about ___ % of the passengers made it.' "
            "Then ask the AI to check your guess with the real survival count, shown in people AND "
            "in percentages."
        ),
        "hints": [
            "First guess: did MORE or FEWER than half survive? No peeking!",
            "Ask for both the raw counts and the percentages.",
            "A donut chart of the two shares is a nice extra to request.",
        ],
        "guide": (
            "**Only ~38% survived — 342 of 891.** Most students guess "
            "50/50, so the real split usually surprises the class.\n\n"
            "*Discuss:* why might our gut guess be too optimistic? (Movies "
            "center on the survivors!)\n\n"
            "*Next up:* 38% overall hides the real story — the split gets "
            "dramatic when we break it down by sex."
        ),
        "reference": (
            "Count how many passengers perished and how many survived, and "
            "show me both numbers with their percentages."
        ),
        "reference_alt": (
            "What fraction of passengers survived, according to "
            "data/titanic.csv? Show me survivors and victims in numbers "
            "and in percent."
        ),
        "experiment": (
            "Ask the AI to show the same split as a donut instead of "
            "numbers — does a picture change how the room FEELS about "
            "38%?"
        ),
        "context": {
            "text": (
                "A worked example of how a column split READS — this is "
                "the ticket-class mix, NOT the survival split you'll ask "
                "for in a second. Notice: groups side by side, counts "
                "big to small. When you make your guess about survival, "
                "imagine which slice of THIS crowd you belong to."
            ),
            "chart": workshop_steps.chart(
                kind="bar",
                horizontal=True,
                title="The class mix (counts, not survival)",
                data=[
                    {"Class": "3rd class", "Passengers": 491},
                    {"Class": "2nd class", "Passengers": 184},
                    {"Class": "1st class", "Passengers": 216},
                ],
                x="Class",
                y="Passengers",
            ),
        },
        "fn": "step_3_survival_overview",
        "placeholder": (
            "e.g. “Count how many passengers survived and how many "
            "didn't…”"
        ),
    },
    {
        "number": 4,
        "title": "Survival by sex",
        "story": (
            "Now we look for our FIRST pattern: did female passengers "
            "survive more often than male passengers?"
        ),
                "prompt": (
            "You placed a bet in checkpoint 1 about which detail decided survival. Have the AI draw "
            "the female-vs-male survival comparison and see whether your bet would have paid off - "
            "then describe the pattern in ONE sentence in your own words, not the AI's."
        ),
        "hints": [
            "The page can draw eye-catching person-icon bars — try asking "
            "for those.",
            "Insist on one plain-English sentence saying what the pattern "
            "IS, not just the chart.",
            "Look at the two bars: roughly what share of each group made "
            "it?",
        ],
        "guide": (
            "**The single strongest pattern in the data: ~74% of women "
            "survived vs ~19% of men.** 'Women and children first' was "
            "real.\n\n"
            "*Discuss:* if you had to bet on one passenger surviving with "
            "only ONE fact allowed, which fact would you pick?\n\n"
            "*Next up:* sex wasn't the only thing that mattered — check "
            "the ticket classes."
        ),
        "reference": (
            "Draw a chart comparing survival for female and male "
            "passengers -- make it fun to look at, the page can draw "
            "person-icon bars -- and describe the pattern in one friendly "
            "sentence."
        ),
        "reference_alt": (
            "Compare survival rates for female and male passengers from "
            "data/titanic.csv in one visual the whole class can read "
            "from the back row, and state the pattern in one sentence."
        ),
        "experiment": (
            "Ask the AI to redraw the exact same comparison in a "
            "different style (person icons instead of bars, or bars "
            "instead of icons) — which version tells the story better?"
        ),
        "context": {
            "text": (
                "Worked example on a DIFFERENT question, so you can see "
                "the shape of a grouped survival comparison: survival by "
                "BOARDING PORT. Cherbourg passengers fared best, "
                "Southampton worst. Your checkpoint asks the same shape "
                "of question about sex — make the AI draw it and say "
                "what it shows."
            ),
            "chart": workshop_steps.chart(
                kind="bar",
                title="Worked example: survival by boarding port",
                data=[
                    {"Port": "Cherbourg", "Survived %": 55.4},
                    {"Port": "Queenstown", "Survived %": 39.0},
                    {"Port": "Southampton", "Survived %": 33.7},
                ],
                x="Port",
                y="Survived %",
            ),
        },
        "fn": "step_4_survival_by_sex",
        "placeholder": (
            "e.g. “Compare survival between women and men on board and "
            "show me the difference…”"
        ),
    },
    {
        "number": 5,
        "title": "Survival by ticket class",
        "story": (
            "Ticket class was a proxy for wealth and cabin location on "
            "board. Did the deck you slept on decide your fate?"
        ),
                "prompt": (
            "Rank the three ticket classes yourself first: which do you think survived best, and "
            "which worst? Then ask the AI to draw survival by class (1, 2, 3) and compare its "
            "picture with your ranking - what stands out to you first?"
        ),
        "hints": [
            "A stacked bar chart makes the three classes easy to compare.",
            "1st class was the priciest deck — 3rd class was near the "
            "bottom of the ship.",
            "Watch whether the survived share shrinks as class goes down.",
        ],
        "guide": (
            "**Wealth shows: ~63% of 1st class survived, ~47% of 2nd, "
            "~24% of 3rd.** The lifeboats weren't evenly used.\n\n"
            "*Discuss:* does the chart alone PROVE wealth was the cause, "
            "or could something else explain it? (Careful: correlation "
            "isn't causation — a big theme of this workshop.)\n\n"
            "*Next up:* one more clue — age — then we hand all of this to "
            "a model."
        ),
        "reference": (
            "Draw a chart of survival by ticket class (1, 2, 3) and tell "
            "me what stands out."
        ),
        "reference_alt": (
            "Group data/titanic.csv by ticket class and show me the "
            "survival percentage for each of the three classes in one "
            "chart."
        ),
        "experiment": (
            "Make the AI verify its own chart: ask it to print the exact "
            "survival percentage for each class — does the survived "
            "share really fall from 1st to 3rd?"
        ),
        "context": {
            "text": (
                "Another worked example of the same reading skill, on a "
                "different relationship: traveling WITH family vs "
                "ALONE. Family looks protective here — hold that "
                "thought, it returns in Stage 2. Then ask the AI for "
                "the ticket-class comparison yourself."
            ),
            "chart": workshop_steps.chart(
                kind="pictorial",
                title="Worked example: survival, family vs alone",
                data=[
                    {"Traveling": "With family aboard", "Survived %": 50.6},
                    {"Traveling": "Alone", "Survived %": 30.4},
                ],
                x="Traveling",
                y="Survived %",
            ),
        },
        "fn": "step_5_survival_by_class",
        "placeholder": (
            "e.g. “Show survival in each ticket class and tell me what "
            "stands out…”"
        ),
    },
    {
        "number": 6,
        "title": "The age story",
        "story": (
            "Kids first? Older folks last? Build one more picture about "
            "AGE -- this is the pattern the Step 2 model will learn from."
        ),
                "prompt": (
            "Decide what you most want to learn about age (kids first? the middle-aged crowd?). Ask "
            "the AI to build exactly ONE chart connecting age to survival, then judge it together: "
            "is it easy to read for 891 people? If it feels crowded, ask for an easier-to-read "
            "alternative - and end with the takeaway in YOUR words."
        ),
        "hints": [
            "Age versus fare on a zoomable scatter, colored by survival, "
            "is one way to see it.",
            "After you have the chart, judge it: is a scatter really the "
            "clearest choice for 891 people?",
            "If it looks messy, ask the AI to propose something easier to "
            "read — a histogram or age-group bars.",
        ],
        "guide": (
            "**Children had better odds; elderly passengers the worst — "
            "but age is a much weaker pattern than sex or class.** And "
            "notice the chart itself: with 891 dots it gets crowded.\n\n"
            "*Discuss:* is a scatter the right graph here? Changing chart "
            "type is a design choice, not cheating — ask the AI for an "
            "easier-to-read alternative if this one feels noisy.\n\n"
            "*Next up:* Stage 2 — a machine learns these patterns and "
            "turns them into predictions."
        ),
        "reference": (
            "Make one chart that shows whether age is connected to "
            "survival (for example a zoomable scatter of age versus fare, "
            "colored by survival), give me one plain-English takeaway, "
            "and tell me whether that chart type was a good choice for "
            "this data or suggest an easier-to-read alternative."
        ),
        "reference_alt": (
            "Is age related to survival in data/titanic.csv? Show me one "
            "clear chart and finish with a single takeaway sentence."
        ),
        "experiment": (
            "Ask the AI for an easier-to-read age chart (say, age-group "
            "bars instead of a scatter) — did changing the design change "
            "what the class can actually see?"
        ),
        "context": {
            "text": (
                "Before relating AGE to anything, meet the age crowd "
                "itself — KNOW YOUR VARIABLE first (data-scientist "
                "habit). Passengers per decade of age: how does the ship "
                "lean? Then decide with the AI how to picture age vs "
                "survival."
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
        "fn": "step_6_age_patterns",
        "placeholder": (
            "e.g. “Find out whether a passenger's age mattered for "
            "survival and show me one chart…”"
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


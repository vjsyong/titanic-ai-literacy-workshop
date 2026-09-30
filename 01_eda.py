"""01_eda.py -- Exploratory Data Analysis (First-year AI Literacy Workshop)

WHAT THIS SCRIPT DOES
    Loads the cleaned Titanic passenger list, prints a friendly summary of the
    numbers, and draws charts that help us spot patterns by eye.

WHAT YOU (THE STUDENT) DO
    Everything in the workshop happens inside the block marked:
        # TODO: PROMPT HERE  >>> BEGIN STUDENT EDIT ZONE
        ...
        # TODO: PROMPT HERE  <<< END STUDENT EDIT ZONE
    That is the ONLY part of the file you (or your AI assistant) should change.

HOW TO RUN
    python 01_eda.py
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


def analyze_data():
    """Load the Titanic data, explore it, and save chart images.

    This function runs when you type:  python 01_eda.py
    """
    titanic = pd.read_csv(DATA_PATH)

    # ------------------------------------------------------------------
    # A first look at the data -- these lines run automatically.
    # ------------------------------------------------------------------
    print("\n=== First look at the data ===")
    print(f"Rows (passengers): {len(titanic)}")
    print(f"Columns: {len(titanic.columns)} -> {', '.join(titanic.columns)}")
    print("\nMissing values per column:")
    missing = titanic.isna().sum()
    print(missing.to_string() if missing.any() else "  none -- the data is clean!")

    # ==================================================================
    # TODO: PROMPT HERE  >>> BEGIN STUDENT EDIT ZONE
    # ==================================================================
    #
    #  Your AI Teaching Assistant will write code here when you ask for
    #  things like: "show me the survival chart" or "compare fares".
    #
    #  Starter content (placeholder): a simple overview table and the
    #  classic survival chart so the workflow is demonstrated end-to-end.
    #
    #  Students: feel free to ask your AI assistant to replace this!
    #
    print("\n=== Survival overview ===")
    group = titanic.groupby("Survived").size()
    survivors = int(group.get(1, 0))
    victims = int(group.get(0, 0))
    print(f"Survivors : {survivors} ({survivors / len(titanic):.1%})")
    print(f"Perished  : {victims} ({victims / len(titanic):.1%})")

    # --- Chart 1: survival by sex -----------------------------------
    chart_path = os.path.join(OUTPUT_DIR, "survival_chart.png")
    by_sex = titanic.groupby(["Sex", "Survived"]).size().unstack("Survived")
    ax = by_sex.plot(kind="bar", figsize=(7, 4.5))
    ax.set_title("Did female passengers survive more often than male passengers?")
    ax.set_xlabel("Sex of passenger")
    ax.set_ylabel("Number of passengers")
    ax.legend(["Perished", "Survived"], title=None)
    ax.set_xticklabels(by_sex.index, rotation=0)
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(chart_path, dpi=150)
    plt.close(fig)
    print(f"\nSaved chart -> {chart_path}")

    # --- Chart 2: survival by ticket class --------------------------
    chart_path = os.path.join(OUTPUT_DIR, "class_chart.png")
    by_class = titanic.groupby(["Pclass", "Survived"]).size().unstack("Survived")
    ax = by_class.plot(kind="bar", figsize=(7, 4.5))
    ax.set_title("Was ticket class linked to survival?")
    ax.set_xlabel("Ticket class (1 = most expensive, 3 = cheapest)")
    ax.set_ylabel("Number of passengers")
    ax.legend(["Perished", "Survived"], title=None)
    ax.set_xticklabels(by_class.index, rotation=0)
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(chart_path, dpi=150)
    plt.close(fig)
    print(f"Saved chart -> {chart_path}")
    #
    # ==================================================================
    # TODO: PROMPT HERE  <<< END STUDENT EDIT ZONE
    # ==================================================================

    return titanic


# ============================================================================
# WEB INTERFACE -- pair this script with a web page (Gradio)
#
# The classroom experience is browser-only: students press one button and
# see the analysis results. The chart logic still lives in analyze_data(),
# so everything the students (or their AI assistant) build inside the
# TODO block automatically appears on the web page too.
#
# HOW TO SERVE JUST THIS PAGE
#     gradio 01_eda.py
#
# HOW TO SERVE ALL SCRIPTS TOGETHER
#     gradio 04_classroom.py
# ============================================================================

import gradio as gr


def run_eda_and_collect():
    """Runs the same analysis as the terminal version and collects web-ready results."""
    titanic = analyze_data()

    # A tiny overview table for the web page.
    group = titanic.groupby("Survived").size()
    summary = pd.DataFrame(
        {
            "Outcome": ["Perished", "Survived"],
            "Number of passengers": [
                int(group.get(0, 0)),
                int(group.get(1, 0)),
            ],
        }
    )
    share = summary["Number of passengers"] / summary["Number of passengers"].sum()
    summary["Share of passengers"] = share.map("{:.1%}".format)

    survival_chart = os.path.join(OUTPUT_DIR, "survival_chart.png")
    class_chart = os.path.join(OUTPUT_DIR, "class_chart.png")
    if not (os.path.exists(survival_chart) and os.path.exists(class_chart)):
        return summary, None, None
    return summary, survival_chart, class_chart


def build_eda_app():
    """Build the web interface for the data exploration steps."""
    with gr.Blocks(title="1 - Meet the Data") as eda:
        gr.Markdown(
            "## Step 1 - Meet the Data\n"
            "Press the button to look at the Titanic passenger list: how "
            "many passengers there were, who survived, and whether you can "
            "spot any patterns by eye."
        )
        run_button = gr.Button("Run the analysis", variant="primary")
        overview = gr.Dataframe(label="Survival overview", interactive=False)
        with gr.Row():
            image_survival = gr.Image(label="Survival by sex", interactive=False)
            image_class = gr.Image(label="Survival by ticket class", interactive=False)
        run_button.click(
            fn=run_eda_and_collect,
            inputs=None,
            outputs=[overview, image_survival, image_class],
        )
    return eda


demo = build_eda_app()

if __name__ == "__main__":
    print(
        "Terminal mode: running the analysis once.\n"
        "For the web version, serve this file with:  gradio 01_eda.py\n"
        "Or serve every workshop step at once:       gradio 04_classroom.py"
    )
    analyze_data()


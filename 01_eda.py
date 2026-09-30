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


if __name__ == "__main__":
    analyze_data()

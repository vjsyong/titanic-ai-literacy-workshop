"""02_train.py -- Train a survival-prediction model (AI Literacy Workshop)

WHAT THIS SCRIPT DOES
    Teaches a computer to guess whether a passenger would have survived the
    Titanic, using the cleaned data. It saves the trained "brain" to a file
    called titanic_model.pkl so the web dashboard (03_dashboard.py) can use it.

WHAT YOU (THE STUDENT) DO
    Everything in the workshop happens inside the block marked:
        # TODO: PROMPT HERE  >>> BEGIN STUDENT EDIT ZONE
        ...
        # TODO: PROMPT HERE  <<< END STUDENT EDIT ZONE
    That is the ONLY part of the file you (or your AI assistant) should change.

HOW TO RUN
    python 02_train.py
"""

import os

import pandas as pd
from sklearn.model_selection import train_test_split

# ----------------------------------------------------------------------------
# PATHS -- never change or move these
# ----------------------------------------------------------------------------
DATA_PATH = os.path.join("data", "titanic.csv")
MODEL_PATH = "titanic_model.pkl"


def train_model():
    """Load data, build features, train a model, and save it.

    This function runs when you type:  python 02_train.py
    """
    titanic = pd.read_csv(DATA_PATH)

    # ------------------------------------------------------------------
    # Baseline plumbing -- converts text columns into plain numbers so
    # that a scikit-learn model can read them. Runs automatically.
    # ------------------------------------------------------------------
    working = titanic.copy()
    working["Sex"] = working["Sex"].map({"male": 0, "female": 1})

    # Pick the numbers the model will learn from (features) and the answer
    # it will try to predict (the label).
    feature_columns = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare"]

    # ==================================================================
    # TODO: PROMPT HERE  >>> BEGIN STUDENT EDIT ZONE
    # ==================================================================
    #
    #  Your AI Teaching Assistant will write code here when you ask for
    #  things like: "use a Random Forest" or "add the class column".
    #
    #  Starter content (placeholder): a simple, solid first model so the
    #  full workflow is demonstrated end-to-end. Students: ask your AI
    #  assistant to replace or improve this!
    #
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score

    x = working[feature_columns]
    y = working["Survived"].astype(int)

    # Hold out part of the data to fairly check how good the model is.
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    # "Scaling" puts age and fare on a similar size scale, which helps
    # this kind of model learn fairly.
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    model = LogisticRegression(max_iter=1000)
    model.fit(x_train_scaled, y_train)

    test_accuracy = accuracy_score(y_test, model.predict(x_test_scaled))
    print(f"Test accuracy: {test_accuracy:.1%}")

    # Save the trained "brain" PLUS the scaler together in one file, so the
    # dashboard can preprocess new passengers exactly the same way.
    import pickle

    artifact = {"model": model, "scaler": scaler, "feature_columns": feature_columns}
    with open(MODEL_PATH, "wb") as handle:
        pickle.dump(artifact, handle)
    print(f"Model saved -> {MODEL_PATH}")

    # Show which numbers mattered most (class 1 = 1st/2nd/3rd ticket class,
    # Sex: 1 = female, 0 = male).
    coefficients = pd.Series(model.coef_[0], index=feature_columns).sort_values()
    print("\nWhat the model paid attention to (positive = pushed toward surviving):")
    print(coefficients.map("{:+.2f}".format).to_string())
    #
    # ==================================================================
    # TODO: PROMPT HERE  <<< END STUDENT EDIT ZONE
    # ==================================================================

    return test_accuracy


# ============================================================================
# WEB INTERFACE -- pair this script with a web page (Gradio)
#
# Students press one button to train the model in the browser. The whole
# training logic still lives in train_model(), so any changes made inside
# the TODO block automatically appear on the web page too.
#
# HOW TO SERVE JUST THIS PAGE
#     gradio 02_train.py
#
# HOW TO SERVE ALL SCRIPTS TOGETHER
#     gradio 04_classroom.py
# ============================================================================

import gradio as gr


def run_training_and_collect():
    """Runs the same training as the terminal version and collects a web-ready result."""
    test_accuracy = train_model()
    headline = (
        f"Training complete! Test accuracy: {test_accuracy:.1%}\n\n"
        "The trained model is saved (titanic_model.pkl) and ready for Step 3, "
        "where you can predict the fate of imaginary passengers."
    )
    return headline


def build_training_app():
    """Build the web interface for the training step."""
    with gr.Blocks(title="2 - Train the Model") as training:
        gr.Markdown(
            "## Step 2 - Train the Model\n"
            "Press the button and the computer will learn survival patterns "
            "from the Titanic data all by itself, then report how good its "
            "guesses are on passengers it was never shown."
        )
        train_button = gr.Button("Train the model", variant="primary")
        summary = gr.Textbox(label="Training result", lines=5, interactive=False)
        train_button.click(
            fn=run_training_and_collect,
            inputs=None,
            outputs=[summary],
        )
    return training


demo = build_training_app()

if __name__ == "__main__":
    print(
        "Terminal mode: training once.\n"
        "For the web version, serve this file with:  gradio 02_train.py\n"
        "Or serve every workshop step at once:       gradio 04_classroom.py"
    )
    train_model()


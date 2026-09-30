"""03_dashboard.py -- Interactive survival web app (AI Literacy Workshop)

WHAT THIS SCRIPT DOES
    Builds a friendly web page where anyone can type in a passenger's details
    (age, ticket class, sex, ...) and instantly see the model's guess: would
    this passenger have survived the Titanic?

WHAT YOU (THE STUDENT) DO
    Everything in the workshop happens inside the block marked:
        # TODO: PROMPT HERE  >>> BEGIN STUDENT EDIT ZONE
        ...
        # TODO: PROMPT HERE  <<< END STUDENT EDIT ZONE
    That is the ONLY part of the file you (or your AI assistant) should change.

HOW TO RUN
    gradio 03_dashboard.py
    (or:  python 03_dashboard.py  -- the run block only explains, never blocks)
"""

import os
import pickle

import gradio as gr

# ----------------------------------------------------------------------------
# PATHS -- never change or move these
# ----------------------------------------------------------------------------
MODEL_PATH = "titanic_model.pkl"


def launch_dashboard():
    """Build and return the Gradio web app (the object named `demo`)."""
    with open(MODEL_PATH, "rb") as handle:
        artifact = pickle.load(handle)
    model = artifact["model"]
    scaler = artifact["scaler"]
    feature_columns = artifact["feature_columns"]

    # ==================================================================
    # TODO: PROMPT HERE  >>> BEGIN STUDENT EDIT ZONE
    # ==================================================================
    #
    #  Your AI Teaching Assistant will write code here when you ask for
    #  things like: "change the slider ranges" or "reword the results
    #  message".
    #
    #  Starter content (placeholder): a simple, working prediction form so
    #  the full workflow is demonstrated end-to-end. Students: ask your AI
    #  assistant to customise this!
    #
    def predict_survival(pclass, sex, age, sibsp, parch, fare):
        """Turn the form inputs into numbers the model understands."""
        import pandas as pd

        sex_as_number = 1 if sex == "female" else 0
        row = pd.DataFrame(
            [[pclass, sex_as_number, age, sibsp, parch, fare]],
            columns=feature_columns,
        )
        features = scaler.transform(row)
        probability = float(model.predict_proba(features)[0][1])

        percent = f"{probability:.0%}"
        if probability >= 0.65:
            headline = f"This passenger would very likely SURVIVE ({percent} chance)."
        elif probability >= 0.35:
            headline = (
                f"This passenger might have survived -- it is a close call "
                f"({percent} chance)."
            )
        else:
            headline = f"This passenger would very likely NOT survive ({percent} chance)."

        explanation = (
            "The model looked at the ticket class, sex, age, and family "
            "details you entered and compared them with patterns in the "
            "real passenger list from 1912. Remember: this is a guess based "
            "on history, not a certainty."
        )
        return headline, explanation

    demo = gr.Interface(
        fn=predict_survival,
        inputs=[
            gr.Radio(choices=[1, 2, 3], value=3, label="Ticket class"),
            gr.Radio(choices=["male", "female"], value="female", label="Sex"),
            gr.Slider(minimum=0, maximum=80, value=25, step=1, label="Age"),
            gr.Slider(minimum=0, maximum=8, value=0, step=1, label="Siblings/spouses aboard"),
            gr.Slider(minimum=0, maximum=9, value=0, step=1, label="Parents/children aboard"),
            gr.Slider(minimum=0, maximum=500, value=30, step=1, label="Ticket fare (pounds, 1912)"),
        ],
        outputs=[
            gr.Textbox(label="Prediction"),
            gr.Textbox(label="How did the model decide?"),
        ],
        title="Titanic Survival Explorer",
        description=(
            "Move the sliders and press Submit to see what an AI model "
            "predicts. The model learned from the real Titanic passenger "
            "list -- it has no magic, just patterns in the data."
        ),
        flagging_mode="never",
    )

    # A tiny self-check so problems show up immediately in the terminal
    # instead of surprising the student in the browser.
    test_headline, _ = predict_survival(3, "male", 25, 0, 0, 8)
    print("Self-check (3rd class, male, 25):", test_headline)

    return demo
    #
    # ==================================================================
    # TODO: PROMPT HERE  <<< END STUDENT EDIT ZONE
    # ==================================================================


demo = launch_dashboard()

if __name__ == "__main__":
    print(
        "This file is meant to be served by Gradio's hot-reload runner:\n"
        "    .venv/bin/gradio 03_dashboard.py\n"
        "The web app object is the variable `demo` defined above."
    )

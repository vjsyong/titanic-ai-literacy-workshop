"""03_dashboard.py -- Step 3 "Survival Explorer" (AI Literacy Workshop)

THE STEP-BY-STEP EXPERIENCE
    Five progressive checkpoints (gates). The page starts as an empty
    explorer; each student prompt to the AI Teaching Assistant unlocks
    one gate: load the trained brain, design the passenger form, wire
    the prediction, make the verdicts kind, then black-box test it.

    The interactive part of the web page fills in as gates unlock:

        Gate 1  -> "the brain woke up" card
        Gate 2  -> the form plan (sliders/radios ranges) card
        Gate 3  -> LIVE passenger form + working prediction button
        Gate 4  -> kinder verdict wording
        Gate 5  -> black-box test bench + graduation message

HOW TO RUN
    gradio 03_dashboard.py       (single-page web view)
    gradio 04_classroom.py       (all steps at once, recommended)
"""

import os
import pickle

import gradio as gr

# ----------------------------------------------------------------------------
# PATH -- never change or move this
# ----------------------------------------------------------------------------
MODEL_PATH = "titanic_model.pkl"

# ----------------------------------------------------------------------------
# SHARED STATE between gates (same contract as 02_train.py) -- the AI
# assistant may read/write entries while building a gate; never rename.
# ----------------------------------------------------------------------------
ARTIFACTS = {}

STEPS_COMPLETED = 0

# The canonical live form, in order. Gate 2 stores its own version here;
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
#   * Gate 3 must expose the prediction function as:
#         ARTIFACTS["predict"](values_dict) -> str verdict (one line or paragraph)
#     where values_dict maps each form label -> its chosen value.
#   * Gate 2 must store the form definition as ARTIFACTS["input_spec"] =
#     a list of dicts like DEFAULT_INPUT_SPEC above.
#   * If a gate needs a missing prerequisite (e.g. no titanic_model.pkl),
#     its function may return a friendly text card telling the student
#     which earlier step to finish -- do NOT raise on missing files.
#   * Bump STEPS_COMPLETED (one at a time) after python/gradio reload
#     shows the gate working on the web page.
# ============================================================================


# === GATE 1 -- "Wake the brain" ==============================================
def step_1_wake_the_brain():
    """Load titanic_model.pkl (trained in Step 2) and prove it works.

    LOOK LIKE: a friendly 'the trained brain is awake' card, including
    one example prediction on a fixed test passenger. If the trained
    brain is missing, return a kind note telling the student to finish
    Step 2 -- checkpoint 7 first (no crash!).
    """
    raise NotImplementedError("Gate 1 is not built yet")


# === GATE 2 -- "Design the passenger form" ===================================
def step_2_design_the_form():
    """Decide which passenger attributes the web form should offer.

    LOOK LIKE: a small table describing each control (name, type,
    sensible range/choices, default). Store the definition in
    ARTIFACTS["input_spec"] (same shape as DEFAULT_INPUT_SPEC).
    """
    raise NotImplementedError("Gate 2 is not built yet")


# === GATE 3 -- "Wire the prediction" =========================================
def step_3_wire_prediction():
    """Make the form actually predict: ARTIFACTS["predict"](values_dict) -> verdict.

    MUST (per the gate contract):
      * read and use ARTIFACTS["input_spec"] labels,
      * encode 'Sex' back to numbers exactly like the model was trained
        (word plain-fare floats are NOT welcome here),
      * scale the numbers with the stored scaler BEFORE predicting,
      * return a human sentence with the probability,
      * confirm with one live example on REAL model output (not mock text).
    """
    raise NotImplementedError("Gate 3 is not built yet")


# === GATE 4 -- "Kind verdicts" ===============================================
def step_4_kind_verdicts():
    """Reword the verdict so it is never scary: 3 probability bands.

    LOOK LIKE: a small table bands -> wording tone. Re-place
    ARTIFACTS["predict"] with a version that uses the kinder wording,
    then re-run one example on the real model to show the new text.
    """
    raise NotImplementedError("Gate 4 is not built yet")


# === GATE 5 -- "Black-box the brain" =========================================
def step_5_black_box_tests():
    """Probe the model with imaginary passengers and discuss unfairness.

    LOOK LIKE: a table of at least 6 imaginary passengers, each with the
    live verdict (e.g. 15-year-old girl in 1st class vs. 60-year-old man
    in 3rd class), plus 2-3 plain-English questions for class discussion
    (is any pattern unfair? what does the model NOT see?).
    """
    raise NotImplementedError("Gate 5 is not built yet")


# ============================================================================
# STEP DESCRIPTIONS (web page reads this).
# ============================================================================
STEPS = [
    {
        "number": 1,
        "title": "Wake the brain",
        "story": (
            "Your Step 2 work saved a trained brain on disk. Wake it up "
            "here and check that it gives sensible guesses."
        ),
        "prompt": (
            "Step 3 of the workshop, checkpoint 1: load the saved model "
            "titanic_model.pkl and prove it is alive by predicting one "
            "fixed test passenger. If the file is missing, tell me kindly "
            "which Step 2 checkpoint to finish first instead of crashing."
        ),
        "fn": "step_1_wake_the_brain",
    },
    {
        "number": 2,
        "title": "Design the passenger form",
        "story": (
            "Before wiring anything: decide which controls the imaginary "
            "passenger form gets (radios for ticket class and sex, sliders "
            "for the numbers) with human-friendly ranges."
        ),
        "prompt": (
            "Step 3, checkpoint 2: propose the passenger web form -- for "
            "each attribute tell me if it should be a dropdown/slider and "
            "what sensible range or choices to give it, and store this "
            "plan where the page can find it."
        ),
        "fn": "step_2_design_the_form",
    },
    {
        "number": 3,
        "title": "Wire the prediction",
        "story": (
            "Time to connect the form to the brain: press predict, and "
            "the model's guess appears. Remember the model was trained on "
            "numbers, so 'female' must turn back into its coded digit "
            "before reaching the model."
        ),
        "prompt": (
            "Step 3, checkpoint 3: connect the form to the model so the "
            "prediction button works. Encode the Sex choices back to "
            "numbers exactly like Step 2 did, use the stored scaler, and "
            "reply with the survival probability in a human sentence. "
            "Show me one live example straight from the model."
        ),
        "fn": "step_3_wire_prediction",
    },
    {
        "number": 4,
        "title": "Kind verdicts",
        "story": (
            "Nobody dies twice -- the passengers in the data are already "
            "history. Trainings models must speak gently: soft wording "
            "for low, medium and high probabilities."
        ),
        "prompt": (
            "Step 3, checkpoint 4: make the browser wording gentler -- "
            "define three probability bands (e.g. unlikely, close call, "
            "likely) and reword the verdicts. Re-run one example on the "
            "live model to show the friendlier message."
        ),
        "fn": "step_4_kind_verdicts",
    },
    {
        "number": 5,
        "title": "Black-box the brain",
        "story": (
            "Final curiosity run: feed the brain imaginary passengers and "
            "discuss whether the patterns are FAIR. A model is a mirror "
            "of its data, nothing more."
        ),
        "prompt": (
            "Step 3, checkpoint 5 (final!): test the live model with at "
            "least six imaginary passengers (young/old, women/men, 1st/3rd "
            "class), show their verdicts in a table, and give me two or "
            "three discussion questions about fairness and what the data "
            "cannot tell us."
        ),
        "fn": "step_5_black_box_tests",
    },
]


# ============================================================================
# ORCHESTRATION -- function name and behavior contract (do not rename).
# ============================================================================
def launch_dashboard():
    """Builds and returns the Step 3 web app (progressive by design).

    The object must be returned as the module-level `demo` so that
    `gradio 04_classroom.py` can serve it with hot reloading.
    """
    completed = int(STEPS_COMPLETED)
    with gr.Blocks(title="3 - Survival Explorer") as dashboard:
        gr.Markdown(
            "## 3 - Survival Explorer\n\n"
            "The trained brain from Step 2 is loaded here. Build the form "
            "checkpoint by checkpoint with your AI Teaching Assistant."
        )
        gr.Markdown(f"**Progress:** {completed} of {len(STEPS)} checkpoints unlocked")

        # --- checkpoint result cards (same style as Steps 1 & 2) ---------
        for step in STEPS:
            if step["number"] > completed:
                if step["number"] == completed + 1:
                    with gr.Group():
                        gr.Markdown(
                            f"#### 🔓 Checkpoint {step['number']} of {len(STEPS)} -- {step['title']}\n"
                            f"{step['story']}\n\n"
                            f"**What to ask your AI Teaching Assistant now:**\n\n"
                            f"> {step['prompt']}"
                        )
                else:
                    gr.Markdown(f"#### 🔒 Step {step['number']} -- locked")
                continue

            with gr.Group():
                gr.Markdown(f"#### ✅ Completed checkpoint {step['number']} -- {step['title']}")
                fn = globals().get(step["fn"])
                if fn is not None:
                    try:
                        workshop_steps.render_result(fn())
                    except Exception as exc:
                        gr.Markdown(
                            f"⚠️ Checkpoint {step['number']} hit an error: "
                            f"`{type(exc).__name__}: {exc}`"
                        )

        # --- the LIVE interactive form appears from checkpoint 3 on ------
        if completed < 3:
            gr.Markdown("🔒 *The live prediction form appears after checkpoint 3.*")
        else:
            input_spec = ARTIFACTS.get("input_spec", DEFAULT_INPUT_SPEC)
            components = []
            with gr.Group():
                gr.Markdown("### Try your own imaginary passenger")
                for item in input_spec:
                    if item["kind"] == "radio":
                        components.append(gr.Radio(choices=item["choices"], value=item["value"], label=item["label"]))
                    else:
                        components.append(
                            gr.Slider(
                                minimum=item["min"],
                                maximum=item["max"],
                                step=item.get("step", 1),
                                value=item["value"],
                                label=item["label"],
                            )
                        )
            verdict = gr.Textbox(label="What the model says", lines=4, interactive=False)
            predict_button = gr.Button("Predict survival", variant="primary")

            def _on_predict(*values):
                values_dict = {item["label"]: value for item, value in zip(input_spec, values)}
                predict = ARTIFACTS.get("predict")
                if predict is None:
                    return "⚠️ The brain is not wired yet -- checkpoint 3 needed."
                try:
                    return str(predict(values_dict))
                except Exception as exc:
                    return f"⚠️ The brain stumbled: {type(exc).__name__}: {exc}"

            def _bind(button):
                button.click(fn=_on_predict, inputs=components, outputs=[verdict])

            _bind(predict_button)

        if STEPS_COMPLETED is not None and int(STEPS_COMPLETED) >= len(STEPS):
            gr.Markdown(
                "🎉 **Workshop complete!** You explored the data, trained a "
                "model, and interrogated it. Go build something of your own!"
            )
    return dashboard


if __name__ == "__main__":
    print(
        "Serve this step with:                gradio 03_dashboard.py\n"
        "Or serve every workshop step at once: gradio 04_classroom.py\n"
        "(The web app object is the variable `demo` below.)"
    )


# ============================================================================
# WEB LAYER -- workshop_steps provides the shared checkpoint machinery.
# ============================================================================
import workshop_steps  # noqa: E402

demo = launch_dashboard()

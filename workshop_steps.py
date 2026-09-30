"""workshop_steps.py -- Shared checkpoint machinery (INSTRUCTOR MANAGED)

HOW THE STEP-BY-STEP EXPERIENCE WORKS
    Every workshop script declares a list of progressive steps (gates).
    Each step is:

        1. A stub function whose body raises NotImplementedError.
        2. A STEPS list entry describing the step for the web page
           (title, story, prompt hint for the student).
        3. A single global counter `STEPS_COMPLETED` (starts at 0).

    During class the student asks their AI Teaching Assistant to unlock
    ONE step at a time. The assistant implements the step function body
    (inside the step's gate markers) and bumps `STEPS_COMPLETED` by one.
    Because Gradio hot-reloads when the file is saved, the web page
    magically updates: the finished step becomes a visible result panel,
    the next step's prompt hint is revealed, later steps stay locked.

    Nobody types any code in class. The only trigger that moves the
    workshop forward is the student asking for intent, e.g.
    "Please show me which columns have holes in the data."

    THIS FILE IS PART OF THE BOOTSTRAP, NOT THE LESSON:
    instructors may extend it; students never touch it.
"""

import gradio as gr

DONE = "✅"
NOW = "🔓"
LOCK = "🔒"


def _progress_line(steps, completed):
    total = len(steps)
    dots = "".join("●" if i < completed else "○" for i in range(total))
    return f"**Progress:** {dots} &nbsp; ({completed} of {total} checkpoints completed)"


def render_result(result):
    """Renders whatever a completed step function returns.

    Steps may return:
        - None                (silent step)
        - str                 (text/markdown)
        - pandas.DataFrame    (table)
        - str path ending .png/.jpg (image)
        - dict combining the above, e.g. {"text": ..., "dataframe": ..., "image": ...}
    """
    if result is None:
        return
    if isinstance(result, str):
        gr.Markdown(result)
        return
    if isinstance(result, dict):
        if "text" in result:
            gr.Markdown(result["text"])
        if result.get("dataframe") is not None:
            gr.Dataframe(result["dataframe"], interactive=False)
        if result.get("image"):
            gr.Image(result["image"], interactive=False)
        return
    gr.Markdown(f"`{result}`")


def make_app(title, intro, steps, module_globals):
    """Builds the progressive web page for one workshop script.

    steps: list of dicts -- number, title, story, prompt, fn (function NAME)
    module_globals: the script module's globals(), used to find step functions
    """
    completed = int(module_globals.get("STEPS_COMPLETED", 0))
    total = len(steps)

    with gr.Blocks(title=title) as app:
        gr.Markdown(f"## {title}\n\n{intro}")
        gr.Markdown(_progress_line(steps, completed))

        for step in steps:
            number = step["number"]
            header = (
                f"#### {DONE} Step {number} of {total} -- {step['title']}"
                if number <= completed
                else (
                    f"#### {NOW} Checkpoint {number} of {total} -- {step['title']}"
                    if number == completed + 1
                    else f"#### {LOCK} Step {number} -- locked"
                )
            )

            with gr.Group():
                gr.Markdown(header)

                if number <= completed:
                    fn = module_globals.get(step["fn"])
                    if fn is None:
                        gr.Markdown("_No output yet._")
                        continue
                    try:
                        render_result(fn())
                    except NotImplementedError as exc:
                        gr.Markdown(f"{LOCK} **not ready:** {exc}")
                    except Exception as exc:  # surface the error so the AI can fix it inside the gate
                        gr.Markdown(
                            f"⚠️ **Step {number} hit an error:** "
                            f"`{type(exc).__name__}: {exc}`\n\n"
                            f"*Ask your AI Teaching Assistant to fix it strictly inside Gate {number}.*"
                        )
                elif number == completed + 1:
                    gr.Markdown(
                        f"{step['story']}\n\n"
                        f"**What to ask your AI Teaching Assistant now:**\n\n"
                        f"> {step['prompt']}"
                    )
                else:
                    gr.Markdown("_Locked -- finish the checkpoint above first._")

    return app

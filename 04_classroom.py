"""04_classroom.py -- One web page for the whole workshop (INSTRUCTOR MANAGED)

WHAT THIS FILE IS
    A thin Gradio wrapper that puts every workshop step on ONE web page as
    browser tabs:

        Tab 1: Meet the Data       (shared from 01_eda.py)
        Tab 2: Train the Model     (shared from 02_train.py)
        Tab 3: Survival Explorer   (shared from 03_dashboard.py)

    Everything still lives inside 01_eda.py / 02_train.py / 03_dashboard.py
    (including the students' TODO zones); this file only displays them in
    the browser.

WHO MAY EDIT THIS FILE
    Instructors only. Students should never edit this file in class, and
    their AI assistant must leave it alone too.

HOW TO RUN
    gradio 04_classroom.py
    (or a single step, e.g.:  gradio 01_eda.py)
"""

import os
import sys

import gradio as gr

HERE = os.path.dirname(os.path.abspath(__file__))


def _load_step(name):
    """Imports the numeric-named workshop scripts (01_eda.py, ...) as modules."""
    import importlib.util

    file_path = os.path.join(HERE, f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


step_eda = _load_step("01_eda")
step_train = _load_step("02_train")
step_dashboard = _load_step("03_dashboard")


def build_classroom_app():
    """Combine every workshop script's web interface into one page with tabs."""
    with gr.Blocks(title="Titanic AI Literacy Workshop") as classroom:
        gr.Markdown(
            "# Titanic AI Literacy Workshop\n"
            "*You are on board in 1912. Explore the passenger list, teach a "
            "computer to spot survival patterns, then test its guesses.*"
        )
        with gr.Tab("1 - Meet the Data"):
            step_eda.demo.render()
        with gr.Tab("2 - Train the Model"):
            step_train.demo.render()
        with gr.Tab("3 - Survival Explorer"):
            step_dashboard.demo.render()
    return classroom


demo = build_classroom_app()

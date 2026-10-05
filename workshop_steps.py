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
    `workshop_server.py` notices the saved file within a fraction of a
    second, re-imports the script and pushes the new state to the open
    page: the finished step becomes a result card and the NEXT prompt
    hint appears. Repeat until all 18 checkpoints are done.

    Nobody types any code in class. The only trigger that moves the
    workshop forward is the student asking for intent, e.g.
    "Please show me which columns have holes in the data."

WHAT A GATE FUNCTION RETURNS (the payload vocabulary)
    text only        ->  return "a friendly markdown sentence"
    table            ->  return df                 (pandas DataFrame)
    multiple parts   ->  return {"text": ..., "dataframe": df}

    interactive chart -> return {
                             "text": "one sentence about the pattern",
                             "chart": workshop_steps.chart(
                                 kind="bar", data=df, x="Sex",
                                 y="Passengers", title="Survival by sex",
                             ),
                         }
    headline number   -> return {"metric": workshop_steps.metric(0.81, "Test accuracy")}

    Any combination of "text", "dataframe", "chart" and "metric" keys in
    one dict renders together on the page, in that order.

OPTIONAL STEP-DESCRIPTION KEYS (read by the page, not the gates):
    "hints":   list of short strings shown under the mission on the
               current card ("Stuck? Think about...").
    "guide":   teacher debrief shown under the result once the step
               completes ("What to notice").
    "context": prep material for a decision the student must make --
               a DataFrame, string, or result dict rendered on the
               current card above the mission ("The raw material").
               Use it whenever a checkpoint asks the student to decide
               something about data they cannot currently see.

CHART KINDS
    bar, pictorial (person icons), line, area, scatter (zoomable),
    pie, donut, histogram, gauge, heatmap.

    `data` may be a pandas DataFrame or a list of row dicts. Wide format:
    one row per x value, one numeric column per series. Example:

        df = titanic.groupby(["Sex", "Survived"]).size().unstack()
        df = df.rename(columns={0: "Perished", 1: "Survived"}).reset_index()
        workshop_steps.chart(
            kind="pictorial", data=df, x="Sex",
            series=["Survived", "Perished"], stacked=True,
        )

THIS FILE IS PART OF THE BOOTSTRAP, NOT THE LESSON:
    instructors may extend it; students never touch it.
"""

from __future__ import annotations

import datetime as _datetime
import math

import pandas as pd

# How many table rows reach the browser per result block (keeps the page
# snappy even if a gate returns a big DataFrame).
MAX_TABLE_ROWS = 250

# Defensive caps for student-written gates: oversized outputs must never
# freeze the shared classroom page.
MAX_CHART_POINTS = 2000
MAX_TEXT_CHARS = 20000

# Every chart kind the web page can draw.
CHART_KINDS = (
    "bar",
    "pictorial",
    "line",
    "area",
    "scatter",
    "pie",
    "donut",
    "histogram",
    "gauge",
    "heatmap",
)


# ---------------------------------------------------------------------------
# Step 0 -- the connection handshake
# ---------------------------------------------------------------------------
# Before Checkpoint 1 opens, the AI Teaching Assistant has to prove it can
# actually reach the workshop project. Its only channel to the web page is
# editing the gate scripts, so the handshake is a one-line flag in 01_eda.py
# inside the GATE 0 markers. Setting PAIRED = True saves the file,
# workshop_server.py notices within a second, the page shows Step 0 complete,
# and Checkpoint 1 unlocks. Instructors may edit the card copy below;
# students never touch it. (See AGENTS.md "Step 0" and the seed prompt.)

CONNECT_FLAG = "PAIRED"

CONNECT_STEP = {
    "number": 0,
    "title": "Connect your assistant",
    "story": (
        "Every session starts with a quick handshake. Your AI Teaching "
        "Assistant has to prove it can reach this workshop project before "
        "Checkpoint 1 opens, by flipping the connection flag in 01_eda.py "
        "and saving the file. This very page refreshes the moment it does."
    ),
    "prompt": (
        "Say hello to your AI Teaching Assistant and ask it to connect to "
        "the workshop. It confirms the handshake in its own words -- and "
        "Checkpoint 1 unlocks right here."
    ),
    "hints": [
        "Your assistant does this once, the first time you say hello.",
        "If nothing moves, ask it to run `python 01_eda.py` and read any error out loud.",
    ],
    "placeholder": "Hi! Are you connected to my workshop page?",
    "guide": (
        "Connection confirmed. The assistant can read and write this "
        "project, so every checkpoint you unlock from here will appear on "
        "this page by itself."
    ),
    "reference": "Hi! Please connect to my workshop project and confirm you are ready.",
    "reference_alt": "Before we start, set up the connection so the page updates as we go.",
}


# ---------------------------------------------------------------------------
# JSON-normalization helpers (numpy / NaN / dates -> plain JSON values)
# ---------------------------------------------------------------------------

def _json_value(value):
    """Turn one pandas/numpy scalar into a plain JSON-friendly value."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None

    item = getattr(value, "item", None)  # numpy scalars expose .item()
    if callable(item):
        try:
            value = value.item()
        except (ValueError, TypeError):
            pass
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (_datetime.datetime, _datetime.date, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, (bool, int, float, str)):
        return value
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return str(value)


def json_ready(value):
    """Recursively convert dicts/lists of numpy values into JSON-safe data."""
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return _json_value(value)


# ---------------------------------------------------------------------------
# Result serialization (what the server sends to the browser)
# ---------------------------------------------------------------------------

def _records(data):
    """Rows as a list of dicts with JSON-friendly values."""
    if data is None:
        return []
    if isinstance(data, pd.DataFrame):
        frame = data.copy()
        if not isinstance(frame.index, pd.RangeIndex):
            frame = frame.reset_index()
        columns = [str(column) for column in frame.columns]
        return [
            dict(zip(columns, (_json_value(value) for value in row)))
            for row in frame.itertuples(index=False, name=None)
        ]
    records = []
    for item in data:
        if not isinstance(item, dict):
            raise TypeError(
                "chart data must be a pandas DataFrame or a list of row dicts"
            )
        records.append({str(key): json_ready(value) for key, value in item.items()})
    return records


def _table_payload(data):
    if isinstance(data, pd.DataFrame):
        frame = data
    else:
        frame = pd.DataFrame(_records(data))
    if not isinstance(frame.index, pd.RangeIndex):
        frame = frame.reset_index()

    total_rows = len(frame)
    truncated = total_rows > MAX_TABLE_ROWS
    if truncated:
        frame = frame.head(MAX_TABLE_ROWS)

    columns = [str(column) for column in frame.columns]
    rows = [
        [_json_value(value) for value in row]
        for row in frame.itertuples(index=False, name=None)
    ]
    return {
        "type": "table",
        "columns": columns,
        "rows": rows,
        "total_rows": total_rows,
        "truncated": truncated,
    }


def _chart_payload(chart):
    """Validate/normalize a chart payload built with workshop_steps.chart()."""
    if not isinstance(chart, dict):
        raise TypeError("chart must be a dict -- build it with workshop_steps.chart(...)")

    kind = str(chart.get("kind", "")).lower()
    if kind not in CHART_KINDS:
        raise ValueError(
            f"unknown chart kind {kind!r}; use one of: {', '.join(CHART_KINDS)}"
        )

    payload = {"kind": kind}
    for key in ("title", "color", "size", "x_label", "y_label"):
        if chart.get(key) is not None:
            payload[key] = json_ready(chart[key])
    for key in ("x",):
        if chart.get(key) is not None:
            payload["x"] = str(chart[key])
    y = chart.get("y")
    if y is not None:
        payload["y"] = [str(item) for item in y] if isinstance(y, (list, tuple)) else str(y)
    for key in ("stacked", "horizontal", "diverging"):
        if chart.get(key):
            payload[key] = True
    if chart.get("series") is not None:
        payload["series"] = [str(item) for item in chart["series"]]
    if chart.get("palette") is not None:
        payload["palette"] = [str(item) for item in chart["palette"]]
    if chart.get("bins") is not None:
        payload["bins"] = int(chart["bins"])

    if kind == "gauge":
        if chart.get("value") is None:
            raise ValueError("gauge charts need value=...")
        payload["value"] = json_ready(chart["value"])
    else:
        records = _records(chart.get("data"))
        if len(records) > MAX_CHART_POINTS:
            records = records[:MAX_CHART_POINTS]
        payload["data"] = records

    return payload


def _metric_block(metric):
    if isinstance(metric, dict):
        block = {"type": "metric"}
        block.update({str(key): json_ready(value) for key, value in metric.items()})
        return block
    return {
        "type": "metric",
        "value": json_ready(metric),
        "label": "",
        "format": "number",
    }


def _cap_text(text):
    """Keep runaway gate output from freezing the shared classroom page."""
    if len(text) <= MAX_TEXT_CHARS:
        return text
    return text[:MAX_TEXT_CHARS] + "\n\n... (output trimmed for the classroom page)"


def serialize_result(result):
    """Turns whatever a gate function returned into JSON blocks for the page.

    Supported returns:
        - None                  (silent step)
        - str                   (text/markdown)
        - pandas.DataFrame      (table)
        - dict with any of "text", "dataframe", "chart", "metric"
    """
    if result is None:
        return None

    blocks = []
    if isinstance(result, str):
        blocks.append({"type": "markdown", "text": _cap_text(result)})
    elif isinstance(result, pd.DataFrame):
        blocks.append(_table_payload(result))
    elif isinstance(result, dict):
        if result.get("text"):
            blocks.append({"type": "markdown", "text": _cap_text(str(result["text"]))})
        if result.get("dataframe") is not None:
            blocks.append(_table_payload(result["dataframe"]))
        if result.get("chart"):
            blocks.append({"type": "chart", "chart": _chart_payload(result["chart"])})
        if result.get("metric"):
            blocks.append(_metric_block(result["metric"]))
    else:
        blocks.append({"type": "markdown", "text": str(result)})

    return {"blocks": blocks} if blocks else None


# ---------------------------------------------------------------------------
# Builders handed to gate functions
# ---------------------------------------------------------------------------

def chart(
    kind,
    data=None,
    *,
    x=None,
    y=None,
    color=None,
    size=None,
    series=None,
    title=None,
    stacked=False,
    horizontal=False,
    diverging=False,
    x_label=None,
    y_label=None,
    bins=10,
    palette=None,
    value=None,
):
    """Build an interactive chart payload for a gate's result dict.

    kind: one of bar, pictorial, line, area, scatter, pie, donut,
          histogram, gauge, heatmap.

    data: pandas DataFrame or list of row dicts (wide format: one row per
          x value, one numeric column per series). Not needed for "gauge".

    x / y: column names. For multi-series charts pass `series=[...]`
           (list of numeric column names) instead of y.
    color / size: optional column names for scatter charts.
    stacked / horizontal / diverging: bar chart styling switches.
    value: the number (0-100) for "gauge" charts.
    bins: histogram bin count (default 10).
    """
    payload = {"kind": str(kind).lower()}
    if payload["kind"] not in CHART_KINDS:
        raise ValueError(
            f"unknown chart kind {kind!r}; use one of: {', '.join(CHART_KINDS)}"
        )
    for key, item in (
        ("data", data),
        ("x", x),
        ("y", y),
        ("color", color),
        ("size", size),
        ("series", series),
        ("title", title),
        ("x_label", x_label),
        ("y_label", y_label),
        ("bins", bins),
        ("palette", palette),
        ("value", value),
    ):
        if item is not None:
            payload[key] = item
    if stacked:
        payload["stacked"] = True
    if horizontal:
        payload["horizontal"] = True
    if diverging:
        payload["diverging"] = True
    return payload


def metric(value, label, *, format="percent"):
    """Build a headline-number block (rendered as an animated ring/number).

    format: "percent" (0.81 -> 81%), "number", or "probability".
    """
    return {"kind": "metric", "value": value, "label": label, "format": format}


def verdict(text, probability=None, band=None):
    """Build the structured result for a Step 3 prediction.

    Gate 3 stores a callable in ARTIFACTS["predict"] that returns this
    dict: the page shows `text`, an animated survival gauge from
    `probability` (0.0-1.0) and a small chip with `band` (e.g. "likely").
    """
    return {"text": str(text), "probability": probability, "band": band}

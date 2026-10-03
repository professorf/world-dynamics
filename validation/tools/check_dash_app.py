# SPDX-License-Identifier: MIT
"""Check that the Dash app (world2_4_dash_app.py) draws exactly what the validated model computes.

Stage 1 checks the standard run, in two ways:
  1. Every curve in the app is simulate()'s output from world2_3_modern.py,
     unchanged, so the app adds nothing of its own to the numbers.
  2. Every curve matches version 1, the card-for-card isomorph of the DYNAMO
     listing, to within floating-point rounding.

Run from the repository root:  python validation/tools/check_dash_app.py

Authors: Nick V. Flor (University of New Mexico) and Claudia (Claude
Interactive Assistant), i.e., Claude, an AI model by Anthropic. See CITE.md.
"""
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO), str(REPO / "validation" / "tools")]

from dash import dcc                                    # noqa: E402

import world2_4_dash_app as app_module                  # noqa: E402
from experiments import LONG, run                       # noqa: E402
from world2_3_modern import simulate                    # noqa: E402

DYNAMO_NAME = {long: short for short, long in LONG.items()}


def graphs(component):
    """Every chart on the page, in page order."""
    if isinstance(component, dcc.Graph):
        return [component]
    children = getattr(component, "children", None)
    if not isinstance(children, (list, tuple)):
        children = [children]
    return [g for child in children if child is not None for g in graphs(child)]


def app_curves():
    """Every curve on the app's page, with the panel it belongs to."""
    traces = [trace for graph in graphs(app_module.app.layout) for trace in graph.figure.data]
    panels = app_module.PLOT_1 + app_module.PLOT_2
    assert len(traces) == len(panels), "one curve per panel"
    return zip(panels, traces)


if __name__ == "__main__":
    version_3 = simulate()
    version_1, _ = run("world2_1_isomorph", "standard")
    print("Stage 1: the standard run")
    print(f"  {'variable':<6} {'same as simulate()':<20} largest relative difference from version 1")
    worst = 0.0
    for (name, _, divide_by, _), trace in app_curves():
        x, y = np.asarray(trace.x), np.asarray(trace.y)
        same = np.array_equal(x, version_3["year"]) and np.array_equal(y, version_3[name] / divide_by)
        assert same, f"{name}: the app's curve is not simulate()'s output"
        assert np.array_equal(x, version_1["TIME"])
        reference = version_1[DYNAMO_NAME[name]] / divide_by
        difference = np.max(np.abs(y - reference) / np.maximum(np.abs(reference), 1e-300))
        worst = max(worst, difference)
        print(f"  {DYNAMO_NAME[name]:<6} {'yes':<20} {difference:.1e}")
    assert worst < 1e-14, "the app's curves drift from version 1"
    print(f"All {len(app_module.PLOT_1) + len(app_module.PLOT_2)} curves pass.")

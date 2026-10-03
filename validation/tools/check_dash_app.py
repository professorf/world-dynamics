# SPDX-License-Identifier: MIT
"""Check that the Dash app (world2_4_dash_app.py) draws exactly what the validated model computes.

The app's callback, rerun(), is called the way Dash calls it, with the sliders
set to each of the book's Chapter 4 experiments that sliders can express:
  standard run       every slider at 100%
  pollution crisis   natural-resource usage at 25%
  crowding           natural-resource usage at 0%, pollution at 10%, run to 2300

For each one, three checks:
  1. The sliders give the book's card values exactly (NRUN1 = .25, and so on).
  2. Every curve the app draws is version 3's validated run of that
     experiment, bit for bit, so the app adds nothing of its own to the numbers.
  3. Every curve matches version 1, the card-for-card isomorph of the DYNAMO
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

import world2_4_dash_app as app_module                       # noqa: E402
from experiments import EXPERIMENTS, LONG, V3_POLICY, run     # noqa: E402

DYNAMO_NAME = {long: short for short, long in LONG.items()}

# experiment: (slider percents that differ from 100, switch year, run to)
SLIDER_SETTINGS = {
    "standard":  ({}, 1970, 2100),
    "pollution": ({"natural_resource_usage_normal": 25}, 1970, 2100),
    "crowding":  ({"natural_resource_usage_normal": 0, "pollution_normal": 10}, 1970, 2300),
}


def check(experiment):
    changed, switch_year, end_year = SLIDER_SETTINGS[experiment]
    percents = [changed.get(name, 100) for name, _, _ in app_module.POLICY_SLIDERS]

    # 1. The sliders give the book's card values exactly
    policy = app_module.policy_from_sliders(percents, switch_year)
    book = {V3_POLICY[card]: value for card, value in EXPERIMENTS[experiment]["constants"].items()}
    for name, (before, after, year) in policy.items():
        assert after == book.get(name, before), f"{name}: slider gives {after}"
        assert year == 1970
    assert end_year == EXPERIMENTS[experiment]["length"]

    # Call the callback as Dash would; its first outputs are the charts, in page order
    outputs = app_module.rerun(*percents, switch_year, end_year)
    panels = app_module.PLOT_1 + app_module.PLOT_2
    figures = outputs[:len(panels)]

    version_3, _ = run("world2_3_modern", experiment)
    version_1, _ = run("world2_1_isomorph", experiment)
    worst = 0.0
    for (name, _, divide_by, _), figure in zip(panels, figures):
        (trace,) = figure.data
        x, y = np.asarray(trace.x), np.asarray(trace.y)
        short = DYNAMO_NAME[name]
        # 2. Bit for bit the validated version 3 run
        assert np.array_equal(x, version_3["TIME"]) and np.array_equal(y, version_3[short] / divide_by), \
            f"{experiment}, {short}: not version 3's validated run"
        # 3. Version 1, to rounding
        assert np.array_equal(x, version_1["TIME"])
        reference = version_1[short] / divide_by
        worst = max(worst, np.max(np.abs(y - reference) / np.maximum(np.abs(reference), 1e-300)))
    assert worst < 1e-14, f"{experiment}: the app's curves drift from version 1"
    return len(figures), len(x), worst


if __name__ == "__main__":
    print(f"  {'experiment':<11} {'curves':>6} {'steps':>6}  card values  same as version 3  "
          "largest relative difference from version 1")
    for experiment in SLIDER_SETTINGS:
        curves, steps, worst = check(experiment)
        print(f"  {experiment:<11} {curves:>6} {steps:>6}  {'exact':<11}  {'bit for bit':<16}  {worst:.1e}")
    print("All checks pass.")

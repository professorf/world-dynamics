# SPDX-License-Identifier: MIT
"""Check that the Dash app (world2_4_dash_app.py) draws exactly what the validated model computes.

For each of the book's four Chapter 4 experiments, the check presses the
app's button for it (by calling preset_values(), which the button's callback
calls), then calls the app's chart callback, rerun(), with those values, the
way Dash would. Then:
  1. The controls hold the book's values exactly: the card values printed in
     the figure's margin (NRUN1 = .25, and so on), the end year, and for the
     food shortage, the two changed tables (BRCMT and DRCMT).
  2. Every blue curve ("this run") is version 3's validated run of that
     experiment, bit for bit, so the app adds nothing of its own to the numbers.
  3. Every blue curve matches version 1, the card-for-card isomorph of the
     DYNAMO listing, to within floating-point rounding.
  4. Every gray curve is version 3's standard run, over the same years.

Run from the repository root:  python validation/tools/check_dash_app.py

Authors: Nick V. Flor (University of New Mexico) and Claudia (Claude
Interactive Assistant), i.e., Claude, an AI model by Anthropic. See CITE.md.
"""
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO), str(REPO / "validation" / "tools")]

import world2_4_dash_app as app_module                                # noqa: E402
from experiments import EXPERIMENTS, LONG, V3_POLICY, V3_TABLE, run   # noqa: E402
from world2_3_modern import simulate                                  # noqa: E402

DYNAMO_NAME = {long: short for short, long in LONG.items()}


def check(experiment):
    values = app_module.preset_values(experiment)
    *percents, switch_year, end_year, crowding = values
    book = EXPERIMENTS[experiment]

    # 1. The controls hold the book's values exactly
    policy = app_module.policy_from_sliders(percents, switch_year)
    book_cards = {V3_POLICY[card]: value for card, value in book["constants"].items()}
    for name, (before, after, year) in policy.items():
        assert after == book_cards.get(name, before), f"{experiment}, {name}: the slider gives {after}"
        assert year == 1970
    assert end_year == book["length"]
    tables = app_module.CROWDING_TABLES[crowding]
    for card, (name, low, high) in V3_TABLE.items():
        xs, ys = tables[name]
        expected = book["tables"].get(card)
        if expected is None:
            assert tables[name] is app_module.STANDARD_TABLES[name], f"{experiment}: {card} changed"
        else:
            assert list(ys) == expected and xs[0] == low and xs[-1] == high, f"{experiment}: {card} differs"

    # Call the chart callback as Dash would; its first outputs are the charts, in page order
    panels = app_module.PLOT_1 + app_module.PLOT_2
    figures = app_module.rerun(*values)[:len(panels)]

    version_3, _ = run("world2_3_modern", experiment)
    version_1, _ = run("world2_1_isomorph", experiment)
    standard = simulate(end_year=end_year)
    worst = 0.0
    for (name, _, divide_by, _), figure in zip(panels, figures):
        gray, blue = figure.data
        short = DYNAMO_NAME[name]
        x, y = np.asarray(blue.x), np.asarray(blue.y)
        # 2. Bit for bit the validated version 3 run
        assert np.array_equal(x, version_3["TIME"]) and np.array_equal(y, version_3[short] / divide_by), \
            f"{experiment}, {short}: not version 3's validated run"
        # 3. Version 1, to rounding
        assert np.array_equal(x, version_1["TIME"])
        reference = version_1[short] / divide_by
        worst = max(worst, np.max(np.abs(y - reference) / np.maximum(np.abs(reference), 1e-300)))
        # 4. The gray curve is the standard run
        assert np.array_equal(np.asarray(gray.x), standard["year"])
        assert np.array_equal(np.asarray(gray.y), standard[name] / divide_by), f"{experiment}, {short}: gray curve"
    assert worst < 1e-14, f"{experiment}: the app's curves drift from version 1"
    return len(figures), len(x), worst


if __name__ == "__main__":
    assert list(app_module.PRESETS) == list(EXPERIMENTS), "one button for each of the book's experiments"
    print(f"  {'experiment':<11} {'curves':>6} {'steps':>6}  book's values  same as version 3  "
          "largest relative difference from version 1")
    for experiment in app_module.PRESETS:
        curves, steps, worst = check(experiment)
        print(f"  {experiment:<11} {curves:>6} {steps:>6}  {'exact':<13}  {'bit for bit':<16}  {worst:.1e}")
    print("All checks pass.")

# SPDX-License-Identifier: MIT
"""
World2, modern Python: the same model and the same single time loop, written the
way you would write it today.

Authors: Nick V. Flor (University of New Mexico, nickflor@unm.edu) and
         Claudia (Claude Interactive Assistant), i.e., Claude, an AI model by Anthropic.
License: MIT (see LICENSE). To cite this code, see CITE.md.
Model:   Jay W. Forrester's World2, from World Dynamics (1971; 2nd ed. 1973).

Source: Jay W. Forrester, World Dynamics (2nd ed., 1973), Appendix B.
The DYNAMO listing is in source-code.dyn; the names are from definition-of-terms.md.

WHAT CHANGED FROM world2_2_readable.py

1. The model is a function, simulate(policy), so you can run it more than once
   and compare runs. Inside it is still one loop you can read top to bottom.
2. The seven policy switches (DYNAMO's CLIP cards) are collected in one
   dictionary at the top. Changing a policy means changing one line there.
3. Tables are pairs of numpy arrays, and one function, lookup(), reads them.
4. The J/K bookkeeping is gone. Each level is updated in place at the end of
   the step: population += dt * (birth_rate - death_rate). This computes the
   same numbers DYNAMO did, because the rates were already calculated from the
   old levels earlier in the same step.
5. Results come back as numpy arrays, and the plot shows each variable in its
   own units instead of DYNAMO's shared fraction-of-scale axis.

WHAT DID NOT CHANGE

The equations, their order within a time step, and the results. The standard
run matches world2_1_isomorph.py to within floating-point rounding.

Run:  python world2_3_modern.py
Needs numpy, and matplotlib for the plot (pip install numpy matplotlib).
It runs the book's standard run (Figure 4-1) and its pollution-crisis
experiment (Figure 4-5), prints a short summary, and saves world2_3_modern_runs.png.
"""

import numpy as np


# ---------------------------------------------------------------------------
# Policy switches
#
# DYNAMO's CLIP cards let seven "normal" values change at a chosen year.
# Each entry is (value before the switch, value after it, switch year).
# In the book's standard run every switch is set, but nothing changes.
# ---------------------------------------------------------------------------

STANDARD_POLICY = {
    #                                         before   after   year     DYNAMO
    "birth_rate_normal":                     (0.04,   0.04,   1970),  # BRN, BRN1, SWT1
    "natural_resource_usage_normal":         (1.0,    1.0,    1970),  # NRUN, NRUN1, SWT2
    "death_rate_normal":                     (0.028,  0.028,  1970),  # DRN, DRN1, SWT3
    "capital_investment_generation_normal":  (0.05,   0.05,   1970),  # CIGN, CIGN1, SWT4
    "capital_investment_discard_normal":     (0.025,  0.025,  1970),  # CIDN, CIDN1, SWT5
    "pollution_normal":                      (1.0,    1.0,    1970),  # POLN, POLN1, SWT6
    "food_coefficient":                      (1.0,    1.0,    1970),  # FC, FC1, SWT7
}

# The book's Figure 4-5 experiment: cut natural-resource usage by 75% in 1970.
POLLUTION_CRISIS_POLICY = {
    **STANDARD_POLICY,
    "natural_resource_usage_normal":         (1.0,    0.25,   1970),
}


def policy_value(policy, name, year):
    """DYNAMO's CLIP time switch: the 'before' value up to and including the
    switch year, the 'after' value from then on."""
    before, after, switch_year = policy[name]
    return before if year <= switch_year else after


# ---------------------------------------------------------------------------
# Constants (equation numbers from source-code.dyn in brackets)
# ---------------------------------------------------------------------------

POPULATION_INITIAL = 1.65e9                                       # [1.2]  PI
NATURAL_RESOURCES_INITIAL = 900e9                                 # [8.2]  NRI
CAPITAL_INVESTMENT_INITIAL = 0.4e9                                # [24.2] CII
POLLUTION_INITIAL = 0.2e9                                         # [30.2] POLI
CAPITAL_INVESTMENT_IN_AGRICULTURE_FRACTION_INITIAL = 0.2          # [35.2] CIAFI

LAND_AREA = 135e6                                                 # [15.1] LA
POPULATION_DENSITY_NORMAL = 26.5                                  # [15.2] PDN
EFFECTIVE_CAPITAL_INVESTMENT_RATIO_NORMAL = 1                     # [4.1]  ECIRN
FOOD_NORMAL = 1                                                   # [19.3] FN
CAPITAL_INVESTMENT_IN_AGRICULTURE_FRACTION_NORMAL = 0.3           # [22.1] CIAFN
POLLUTION_STANDARD = 3.6e9                                        # [29.1] POLS
CAPITAL_INVESTMENT_IN_AGRICULTURE_FRACTION_ADJUSTMENT_TIME = 15   # [35.3] CIAFT
QUALITY_OF_LIFE_STANDARD = 1                                      # [37.1] QLS


# ---------------------------------------------------------------------------
# Tables
#
# A table is a pair of arrays: x values spaced evenly from low to high, and
# the y value at each. table(0, 5, [...]) is DYNAMO's TABHL(..., X, 0, 5, 1).
# ---------------------------------------------------------------------------

def table(x_low, x_high, y_values):
    """A lookup table with y_values spaced evenly from x_low to x_high."""
    y = np.array(y_values, dtype=float)
    return np.linspace(x_low, x_high, len(y)), y


def lookup(tab, x):
    """Straight-line interpolation in a table, holding the end values outside
    its range (DYNAMO's TABHL). DYNAMO's TABLE instead flagged inputs outside
    the range; in the book's runs no input ever leaves its range, so here
    one function serves for both."""
    xs, ys = tab
    return float(np.interp(x, xs, ys))


BIRTH_RATE_FROM_MATERIAL_MULTIPLIER_TABLE = table(0, 5, [1.2, 1, .85, .75, .7, .7])                      # BRMMT  [3.1]
NATURAL_RESOURCE_EXTRACTION_MULTIPLIER_TABLE = table(0, 1, [0, .15, .5, .85, 1])                         # NREMT  [6.1]
DEATH_RATE_FROM_MATERIAL_MULTIPLIER_TABLE = table(0, 5, [3, 1.8, 1, .8, .7, .6, .53, .5, .5, .5, .5])    # DRMMT  [11.1]
DEATH_RATE_FROM_POLLUTION_MULTIPLIER_TABLE = table(0, 60, [.92, 1.3, 2, 3.2, 4.8, 6.8, 9.2])             # DRPMT  [12.1]
DEATH_RATE_FROM_FOOD_MULTIPLIER_TABLE = table(0, 2, [30, 3, 2, 1.4, 1, .7, .6, .5, .5])                  # DRFMT  [13.1]
DEATH_RATE_FROM_CROWDING_MULTIPLIER_TABLE = table(0, 5, [.9, 1, 1.2, 1.5, 1.9, 3])                       # DRCMT  [14.1]
BIRTH_RATE_FROM_CROWDING_MULTIPLIER_TABLE = table(0, 5, [1.05, 1, .9, .7, .6, .55])                      # BRCMT  [16.1]
BIRTH_RATE_FROM_FOOD_MULTIPLIER_TABLE = table(0, 4, [0, 1, 1.6, 1.9, 2])                                 # BRFMT  [17.1]
BIRTH_RATE_FROM_POLLUTION_MULTIPLIER_TABLE = table(0, 60, [1.02, .9, .7, .4, .25, .15, .1])              # BRPMT  [18.1]
FOOD_FROM_CROWDING_MULTIPLIER_TABLE = table(0, 5, [2.4, 1, .6, .4, .3, .2])                              # FCMT   [20.1]
FOOD_POTENTIAL_FROM_CAPITAL_INVESTMENT_TABLE = table(0, 6, [.5, 1, 1.4, 1.7, 1.9, 2.05, 2.2])            # FPCIT  [21.1]
CAPITAL_INVESTMENT_MULTIPLIER_TABLE = table(0, 5, [.1, 1, 1.8, 2.4, 2.8, 3])                             # CIMT   [26.1]
FOOD_FROM_POLLUTION_MULTIPLIER_TABLE = table(0, 60, [1.02, .9, .65, .35, .2, .1, .05])                   # FPMT   [28.1]
POLLUTION_FROM_CAPITAL_MULTIPLIER_TABLE = table(0, 5, [.05, 1, 3, 5.4, 7.4, 8])                          # POLCMT [32.1]
POLLUTION_ABSORPTION_TIME_TABLE = table(0, 60, [.6, 2.5, 5, 8, 11.5, 15.5, 20])                          # POLATT [34.1]
CAPITAL_FRACTION_INDICATED_BY_FOOD_RATIO_TABLE = table(0, 2, [1, .6, .3, .15, .1])                       # CFIFRT [36.1]
QUALITY_OF_LIFE_FROM_MATERIAL_TABLE = table(0, 5, [.2, 1, 1.7, 2.3, 2.7, 2.9])                           # QLMT   [38.1]
QUALITY_OF_LIFE_FROM_CROWDING_TABLE = table(0, 5, [2, 1.3, 1, .75, .55, .45, .38, .3, .25, .22, .2])     # QLCT   [39.1]
QUALITY_OF_LIFE_FROM_FOOD_TABLE = table(0, 4, [0, 1, 1.8, 2.4, 2.7])                                     # QLFT   [40.1]
QUALITY_OF_LIFE_FROM_POLLUTION_TABLE = table(0, 60, [1.04, .85, .6, .3, .15, .05, .02])                  # QLPT   [41.1]
NATURAL_RESOURCE_FROM_MATERIAL_MULTIPLIER_TABLE = table(0, 10, [0, 1, 1.8, 2.4, 2.9, 3.3, 3.6, 3.8, 3.9, 3.95, 4])  # NRMMT [42.1]
CAPITAL_INVESTMENT_FROM_QUALITY_RATIO_TABLE = table(0, 2, [.7, .8, 1, 1.5, 2])                           # CIQRT  [43.1]


# ---------------------------------------------------------------------------
# The model
# ---------------------------------------------------------------------------

def simulate(policy=STANDARD_POLICY, start_year=1900, end_year=2100, dt=0.2):
    """Run World2 from start_year to end_year in steps of dt years.

    Returns a dict of numpy arrays, one value per time step, keyed by name
    ("year", "population", "pollution_ratio", ...).
    """
    n_steps = round((end_year - start_year) / dt)
    # Computing each year directly (instead of adding dt over and over) and
    # rounding avoids floating-point drift, so the switches fire exactly at 1970.
    years = np.round(start_year + dt * np.arange(n_steps + 1), 6)
    history = {}

    # Initial values of the five levels                                   [N cards]
    population = POPULATION_INITIAL
    natural_resources = NATURAL_RESOURCES_INITIAL
    capital_investment = CAPITAL_INVESTMENT_INITIAL
    pollution = POLLUTION_INITIAL
    capital_investment_in_agriculture_fraction = CAPITAL_INVESTMENT_IN_AGRICULTURE_FRACTION_INITIAL

    for step, year in enumerate(years):

        # ---- 1. Auxiliaries, from the levels as they stand this year ----

        # Natural resources and the material standard of living
        natural_resource_fraction_remaining = natural_resources / NATURAL_RESOURCES_INITIAL       # [7]
        natural_resource_extraction_multiplier = lookup(
            NATURAL_RESOURCE_EXTRACTION_MULTIPLIER_TABLE, natural_resource_fraction_remaining)    # [6]
        capital_investment_ratio = capital_investment / population                                # [23]
        effective_capital_investment_ratio = (                                                    # [5]
            capital_investment_ratio
            * (1 - capital_investment_in_agriculture_fraction)
            * natural_resource_extraction_multiplier
            / (1 - CAPITAL_INVESTMENT_IN_AGRICULTURE_FRACTION_NORMAL))
        material_standard_of_living = (effective_capital_investment_ratio                         # [4]
                                       / EFFECTIVE_CAPITAL_INVESTMENT_RATIO_NORMAL)

        # Effects of the material standard of living
        birth_rate_from_material_multiplier = lookup(
            BIRTH_RATE_FROM_MATERIAL_MULTIPLIER_TABLE, material_standard_of_living)               # [3]
        death_rate_from_material_multiplier = lookup(
            DEATH_RATE_FROM_MATERIAL_MULTIPLIER_TABLE, material_standard_of_living)               # [11]
        capital_investment_multiplier = lookup(
            CAPITAL_INVESTMENT_MULTIPLIER_TABLE, material_standard_of_living)                     # [26]
        natural_resource_from_material_multiplier = lookup(
            NATURAL_RESOURCE_FROM_MATERIAL_MULTIPLIER_TABLE, material_standard_of_living)         # [42]
        quality_of_life_from_material = lookup(
            QUALITY_OF_LIFE_FROM_MATERIAL_TABLE, material_standard_of_living)                     # [38]

        # Crowding and its effects
        crowding_ratio = population / (LAND_AREA * POPULATION_DENSITY_NORMAL)                     # [15]
        birth_rate_from_crowding_multiplier = lookup(
            BIRTH_RATE_FROM_CROWDING_MULTIPLIER_TABLE, crowding_ratio)                            # [16]
        death_rate_from_crowding_multiplier = lookup(
            DEATH_RATE_FROM_CROWDING_MULTIPLIER_TABLE, crowding_ratio)                            # [14]
        food_from_crowding_multiplier = lookup(
            FOOD_FROM_CROWDING_MULTIPLIER_TABLE, crowding_ratio)                                  # [20]
        quality_of_life_from_crowding = lookup(
            QUALITY_OF_LIFE_FROM_CROWDING_TABLE, crowding_ratio)                                  # [39]

        # Pollution and its effects
        pollution_ratio = pollution / POLLUTION_STANDARD                                          # [29]
        birth_rate_from_pollution_multiplier = lookup(
            BIRTH_RATE_FROM_POLLUTION_MULTIPLIER_TABLE, pollution_ratio)                          # [18]
        death_rate_from_pollution_multiplier = lookup(
            DEATH_RATE_FROM_POLLUTION_MULTIPLIER_TABLE, pollution_ratio)                          # [12]
        food_from_pollution_multiplier = lookup(
            FOOD_FROM_POLLUTION_MULTIPLIER_TABLE, pollution_ratio)                                # [28]
        pollution_absorption_time = lookup(
            POLLUTION_ABSORPTION_TIME_TABLE, pollution_ratio)                                     # [34]
        pollution_from_capital_multiplier = lookup(
            POLLUTION_FROM_CAPITAL_MULTIPLIER_TABLE, capital_investment_ratio)                    # [32]
        quality_of_life_from_pollution = lookup(
            QUALITY_OF_LIFE_FROM_POLLUTION_TABLE, pollution_ratio)                                # [41]

        # Food and its effects
        capital_investment_ratio_in_agriculture = (                                               # [22]
            capital_investment_ratio
            * capital_investment_in_agriculture_fraction
            / CAPITAL_INVESTMENT_IN_AGRICULTURE_FRACTION_NORMAL)
        food_potential_from_capital_investment = lookup(
            FOOD_POTENTIAL_FROM_CAPITAL_INVESTMENT_TABLE, capital_investment_ratio_in_agriculture)  # [21]
        food_ratio = (food_potential_from_capital_investment                                      # [19]
                      * food_from_crowding_multiplier
                      * food_from_pollution_multiplier
                      * policy_value(policy, "food_coefficient", year)
                      / FOOD_NORMAL)
        birth_rate_from_food_multiplier = lookup(
            BIRTH_RATE_FROM_FOOD_MULTIPLIER_TABLE, food_ratio)                                    # [17]
        death_rate_from_food_multiplier = lookup(
            DEATH_RATE_FROM_FOOD_MULTIPLIER_TABLE, food_ratio)                                    # [13]
        capital_fraction_indicated_by_food_ratio = lookup(
            CAPITAL_FRACTION_INDICATED_BY_FOOD_RATIO_TABLE, food_ratio)                           # [36]
        quality_of_life_from_food = lookup(
            QUALITY_OF_LIFE_FROM_FOOD_TABLE, food_ratio)                                          # [40]

        # Quality of life
        capital_investment_from_quality_ratio = lookup(                                           # [43]
            CAPITAL_INVESTMENT_FROM_QUALITY_RATIO_TABLE,
            quality_of_life_from_material / quality_of_life_from_food)
        quality_of_life = (QUALITY_OF_LIFE_STANDARD                                               # [37]
                           * quality_of_life_from_material
                           * quality_of_life_from_crowding
                           * quality_of_life_from_food
                           * quality_of_life_from_pollution)

        # ---- 2. Rates (per year) for the coming step ----

        birth_rate = (population                                                                  # [2]
                      * policy_value(policy, "birth_rate_normal", year)
                      * birth_rate_from_food_multiplier
                      * birth_rate_from_material_multiplier
                      * birth_rate_from_crowding_multiplier
                      * birth_rate_from_pollution_multiplier)
        death_rate = (population                                                                  # [10]
                      * policy_value(policy, "death_rate_normal", year)
                      * death_rate_from_material_multiplier
                      * death_rate_from_pollution_multiplier
                      * death_rate_from_food_multiplier
                      * death_rate_from_crowding_multiplier)
        natural_resource_usage_rate = (population                                                 # [9]
                                       * policy_value(policy, "natural_resource_usage_normal", year)
                                       * natural_resource_from_material_multiplier)
        capital_investment_generation = (population                                               # [25]
                                         * capital_investment_multiplier
                                         * policy_value(policy, "capital_investment_generation_normal", year))
        capital_investment_discard = (capital_investment                                          # [27]
                                      * policy_value(policy, "capital_investment_discard_normal", year))
        pollution_generation = (population                                                        # [31]
                                * policy_value(policy, "pollution_normal", year)
                                * pollution_from_capital_multiplier)
        pollution_absorption = pollution / pollution_absorption_time                              # [33]

        # ---- 3. Record this year ----

        this_year = {
            "year": year,
            "population": population,
            "natural_resources": natural_resources,
            "capital_investment": capital_investment,
            "pollution": pollution,
            "capital_investment_in_agriculture_fraction": capital_investment_in_agriculture_fraction,
            "birth_rate": birth_rate,
            "death_rate": death_rate,
            "natural_resource_usage_rate": natural_resource_usage_rate,
            "capital_investment_generation": capital_investment_generation,
            "capital_investment_discard": capital_investment_discard,
            "pollution_generation": pollution_generation,
            "pollution_absorption": pollution_absorption,
            "pollution_ratio": pollution_ratio,
            "quality_of_life": quality_of_life,
            "food_ratio": food_ratio,
            "material_standard_of_living": material_standard_of_living,
            "quality_of_life_from_crowding": quality_of_life_from_crowding,
            "quality_of_life_from_pollution": quality_of_life_from_pollution,
        }
        for name, value in this_year.items():
            history.setdefault(name, []).append(value)

        if step == n_steps:
            break

        # ---- 4. Levels move to next year: each changes by its net flow times dt ----

        population += dt * (birth_rate - death_rate)                                              # [1]
        natural_resources -= dt * natural_resource_usage_rate                                     # [8]
        capital_investment += dt * (capital_investment_generation - capital_investment_discard)   # [24]
        pollution += dt * (pollution_generation - pollution_absorption)                           # [30]
        capital_investment_in_agriculture_fraction += (                                           # [35]
            (dt / CAPITAL_INVESTMENT_IN_AGRICULTURE_FRACTION_ADJUSTMENT_TIME)
            * (capital_fraction_indicated_by_food_ratio * capital_investment_from_quality_ratio
               - capital_investment_in_agriculture_fraction))

    return {name: np.array(values) for name, values in history.items()}


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def summarize(label, run):
    """Print a few landmark numbers from a run."""
    years = run["year"]
    def peak(name):
        i = int(np.argmax(run[name]))
        return years[i], run[name][i]
    pop_year, pop = peak("population")
    pol_year, pol = peak("pollution_ratio")
    print(f"{label}")
    print(f"  population peaks at {pop / 1e9:.2f} billion in {pop_year:.0f}, "
          f"ends at {run['population'][-1] / 1e9:.2f} billion in {years[-1]:.0f}")
    print(f"  pollution ratio peaks at {pol:.1f} in {pol_year:.0f}")
    print(f"  natural resources left in {years[-1]:.0f}: "
          f"{run['natural_resources'][-1] / NATURAL_RESOURCES_INITIAL:.0%} of the 1900 stock")


PANELS = [
    # (variable, title, divide values by)
    ("population",                                 "Population (billions)",                        1e9),
    ("natural_resources",                          "Natural resources (billion units)",            1e9),
    ("capital_investment",                         "Capital investment (billion units)",           1e9),
    ("pollution_ratio",                            "Pollution ratio (pollution / standard)",       1),
    ("quality_of_life",                            "Quality of life",                              1),
    ("material_standard_of_living",                "Material standard of living",                  1),
    ("food_ratio",                                 "Food ratio",                                   1),
    ("capital_investment_in_agriculture_fraction", "Capital-investment-in-agriculture fraction",  1),
]

SERIES_STYLE = [  # validated two-color categorical palette; dashes as a second cue
    {"color": "#2a78d6", "linestyle": "-"},
    {"color": "#eb6834", "linestyle": (0, (5, 2))},
]


def plot_runs(runs, filename):
    """Small multiples: one panel per variable, one line per run."""
    import matplotlib.pyplot as plt
    ink, muted, grid, surface = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
    fig, axes = plt.subplots(2, 4, figsize=(15, 7.2), sharex=True, facecolor=surface)
    for ax, (name, title, scale) in zip(axes.flat, PANELS):
        ax.set_facecolor(surface)
        for (label, run), style in zip(runs.items(), SERIES_STYLE):
            ax.plot(run["year"], run[name] / scale, linewidth=1.8, label=label, **style)
        ax.set_title(title, fontsize=10, color=ink, loc="left")
        ax.set_ylim(bottom=0)
        ax.set_xlim(1900, 2100)
        ax.set_xticks(range(1900, 2101, 50))
        ax.grid(True, color=grid, linewidth=0.8)
        ax.tick_params(colors=muted, labelsize=8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(grid)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=len(runs), frameon=False,
               fontsize=10, labelcolor=ink)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(filename, dpi=120, facecolor=surface)
    return fig


# ---------------------------------------------------------------------------
# Run the book's two experiments
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    runs = {
        "Standard run (book Figure 4-1)": simulate(STANDARD_POLICY),
        "Resource usage cut 75% in 1970 (book Figure 4-5)": simulate(POLLUTION_CRISIS_POLICY),
    }
    for label, run in runs.items():
        summarize(label, run)

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed, so the plot is skipped "
              "(pip install matplotlib to see it).")
    else:
        plot_runs(runs, "world2_3_modern_runs.png")
        print("Plot saved to world2_3_modern_runs.png")
        plt.show()

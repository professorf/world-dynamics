# SPDX-License-Identifier: MIT
"""Run each Python version of World2 under each Chapter 4 experiment.

The four experiments are the ones in Chapter 4 of Forrester's World Dynamics.
Their changes are the PRESENT / ORIGINAL values printed in each figure's margin.

Versions 1 and 2 are run the DYNAMO way: a copy of the script with the changed
cards edited, as a DYNAMO user would have changed cards and rerun. Version 3 is
run through its policy dictionary, its table definitions and the end_year
argument of simulate().

Every run comes back in one common form: a dict of numpy arrays keyed by the
DYNAMO names (TIME, P, NR, ...), plus POLAT, derived as POL / POLA (eq. 33).

Run from the repository root:  python validation/tools/experiments.py
It prints how closely versions 2 and 3 agree with version 1 in every experiment.

Authors: Nick V. Flor (University of New Mexico) and Claudia (Claude
Interactive Assistant), i.e., Claude, an AI model by Anthropic. See CITE.md.
"""
import contextlib
import importlib.util
import io
import os
import re
import runpy
import tempfile
import warnings
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
VERSIONS = ["world2_1_isomorph", "world2_2_readable", "world2_3_modern"]

EXPERIMENTS = {
    "standard": dict(constants={}, tables={}, length=2100),
    "pollution": dict(constants={"NRUN1": .25}, tables={}, length=2100),
    "crowding": dict(constants={"NRUN1": 0, "POLN1": .1}, tables={}, length=2300),
    "food": dict(constants={"NRUN1": 0, "POLN1": .1},
                 tables={"BRCMT": [1.05, 1, 1, 1, 1, 1], "DRCMT": [.9, 1, 1, 1, 1, 1]},
                 length=2300),
}

# DYNAMO name -> name in version 2, and in version 3
V2_NAME = {"NRUN1": "natural_resource_usage_normal_1", "POLN1": "pollution_normal_1",
           "BRCMT": "birth_rate_from_crowding_multiplier_table",
           "DRCMT": "death_rate_from_crowding_multiplier_table", "LENGTH": "final_time"}
V3_POLICY = {"NRUN1": "natural_resource_usage_normal", "POLN1": "pollution_normal"}
V3_TABLE = {"BRCMT": ("BIRTH_RATE_FROM_CROWDING_MULTIPLIER_TABLE", 0, 5),
            "DRCMT": ("DEATH_RATE_FROM_CROWDING_MULTIPLIER_TABLE", 0, 5)}

# DYNAMO name -> key in the results of versions 2 and 3
LONG = {"TIME": "time", "P": "population", "NR": "natural_resources", "CI": "capital_investment",
        "POL": "pollution", "CIAF": "capital_investment_in_agriculture_fraction",
        "BR": "birth_rate", "DR": "death_rate", "NRUR": "natural_resource_usage_rate",
        "CIG": "capital_investment_generation", "CID": "capital_investment_discard",
        "POLG": "pollution_generation", "POLA": "pollution_absorption", "POLR": "pollution_ratio",
        "QL": "quality_of_life", "FR": "food_ratio", "MSL": "material_standard_of_living",
        "QLC": "quality_of_life_from_crowding", "QLP": "quality_of_life_from_pollution"}


def _edit(source, name, value):
    """Replace the module-level assignment 'name = ...' (there must be exactly one)."""
    pattern = re.compile(rf"^{re.escape(name)} = .*$", re.M)
    assert len(pattern.findall(source)) == 1, name
    return pattern.sub(f"{name} = {value!r}", source)


def _run_script(version, exp):
    source = (REPO / f"{version}.py").read_text(encoding="utf-8")
    name = (lambda n: n) if version == "world2_1_isomorph" else (lambda n: V2_NAME[n])
    for k, v in {**exp["constants"], **exp["tables"]}.items():
        source = _edit(source, name(k), v)
    source = _edit(source, name("LENGTH"), exp["length"])
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / f"{version}.py"
        path.write_text(source, encoding="utf-8")
        cwd = os.getcwd()
        os.chdir(d)                       # the scripts save their plots in the current folder
        try:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                g = runpy.run_path(str(path))
        finally:
            os.chdir(cwd)
    r = g["results"]
    if version == "world2_1_isomorph":
        return {k: np.array(r[k]) for k in LONG}, out.getvalue()
    return {k: np.array(r[LONG[k]]) for k in LONG}, out.getvalue()


def _run_v3(exp):
    spec = importlib.util.spec_from_file_location("world2_3_modern", REPO / "world2_3_modern.py")
    m3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m3)
    policy = dict(m3.STANDARD_POLICY)
    for k, v in exp["constants"].items():
        before, _, year = policy[V3_POLICY[k]]
        policy[V3_POLICY[k]] = (before, v, year)
    for k, v in exp["tables"].items():
        attr, lo, hi = V3_TABLE[k]
        setattr(m3, attr, m3.table(lo, hi, v))
    r = m3.simulate(policy, end_year=exp["length"])
    return {k: r["year" if k == "TIME" else LONG[k]] for k in LONG}, ""


def run(version, experiment):
    """Run one version under one experiment. Returns (results, printed output)."""
    os.environ.setdefault("MPLBACKEND", "Agg")   # no plot windows during validation
    warnings.filterwarnings("ignore")
    exp = EXPERIMENTS[experiment]
    res, log = _run_v3(exp) if version == "world2_3_modern" else _run_script(version, exp)
    res["POLAT"] = res["POL"] / res["POLA"]
    return res, log


if __name__ == "__main__":
    for e in EXPERIMENTS:
        runs = {v: run(v, e) for v in VERSIONS}
        base = runs["world2_1_isomorph"][0]
        print(f"== {e}: {len(base['TIME'])} time steps, {base['TIME'][0]:.0f} to {base['TIME'][-1]:.0f}")
        for v in VERSIONS:
            if "warning" in runs[v][1].lower():
                print(f"   {v}: {runs[v][1].strip()}")
        for v in VERSIONS[1:]:
            r = runs[v][0]
            assert np.array_equal(r["TIME"], base["TIME"])
            worst = max(np.max(np.abs(r[k] - base[k]) / np.maximum(np.abs(base[k]), 1e-300)) for k in base)
            same = all(np.array_equal(r[k], base[k]) for k in base)
            print(f"   {v} vs world2_1_isomorph: largest relative difference {worst:.1e}"
                  + ("  (bit-identical)" if same else ""))

# SPDX-License-Identifier: MIT
"""Print the numbers that validation/README.md compares with the book's text.

Each line names the claim in Forrester's World Dynamics (with its page or
figure) and gives the value from our run.

Run from the repository root:  python validation/tools/checkpoints.py [version]
where version is world2_1_isomorph (the default), world2_2_readable or
world2_3_modern. All three give the same numbers.

Authors: Nick V. Flor (University of New Mexico) and Claudia (Claude
Interactive Assistant), i.e., Claude, an AI model by Anthropic. See CITE.md.
"""
import sys

import numpy as np

from experiments import run

CR_NORMAL = 135e6 * 26.5        # LA * PDN: the population at which the crowding ratio is 1


def at(r, name, year):
    return r[name][np.argmin(np.abs(r["TIME"] - year))]


def peak(r, name, after=None):
    t = r["TIME"]
    mask = np.ones_like(t, bool) if after is None else t > after
    i = np.flatnonzero(mask)[np.argmax(r[name][mask])]
    return t[i], r[name][i]


def main(version):
    s, _ = run(version, "standard")
    print(f"Checkpoints for {version}\n")
    print("STANDARD RUN")
    y, p = peak(s, "P");     print(f"  Population peaks in 2020 (p. 69): {y:.1f}, at {p / 1e9:.2f} billion")
    y, _ = peak(s, "NRUR");  print(f"  Resource-usage rate peaks about 2010 (Fig. 4-3): {y:.1f}")
    y, _ = peak(s, "CIG");   print(f"  Capital-investment generation declines after 2010 (Fig. 4-4): peaks {y:.1f}")
    t = s["TIME"]; k = np.flatnonzero((t > 1950) & (s["CIG"] < s["CID"]))[0]
    y, _ = peak(s, "CI");    print(f"  ...below discard from 2040, when CI declines (Fig. 4-4): crosses {t[k]:.1f}, CI peaks {y:.1f}")
    y, v = peak(s, "CIAF");  print(f"  CIAF rises from 0.2 to 0.32 (p. 72): peaks at {v:.3f} ({y:.0f})")
    y, _ = peak(s, "MSL");   print(f"  Material standard of living peaks about 2000 (p. 72): {y:.1f}")
    y, v = peak(s, "POL");   print(f"  Pollution peaks 'in 2060 at some 6 times 1970' (p. 70): {y:.1f}, {v / at(s, 'POL', 1970):.1f} times")
    y, _ = peak(s, "QL");    print(f"  Quality of life peaks 'around 1960' (p. 70): {y:.1f}")

    c, _ = run(version, "pollution")
    t, P = c["TIME"], c["P"]
    print("\nPOLLUTION CRISIS (NRUN1 = 0.25)")
    _, v = peak(c, "POL");   print(f"  Pollution rises to more than 40 times 1970 (p. 75): {v / at(c, 'POL', 1970):.0f} times")
    yp, p = peak(c, "P")
    k90 = np.flatnonzero((t > yp) & (P <= 0.9 * p))[0]
    k6 = np.flatnonzero((t > yp) & (P <= p / 6))[0]
    print(f"  Population drops in 20 years to one-sixth of its peak (p. 75): peak {p / 1e9:.2f} billion in {yp:.1f};"
          f" below 90% of peak in {t[k90]:.1f}, one-sixth in {t[k6]:.1f} ({t[k6] - t[k90]:.1f} years)")
    k = np.flatnonzero(t > 2030)[np.argmin(c["QL"][t > 2030])]
    print(f"  Quality of life dips deeply, then rises after 2060 (p. 76): {c['QL'][k]:.2f} in {t[k]:.1f}, {at(c, 'QL', 2070):.1f} in 2070")

    w, _ = run(version, "crowding")
    print("\nCROWDING (NRUN1 = 0, POLN1 = 0.1, run to 2300)")
    _, p = peak(w, "P");     print(f"  Population rises to about 9.7 billion (p. 81): {p / 1e9:.2f} billion")
    print(f"  ...a crowding ratio CR of 2.65 (p. 81): CR peaks at {p / CR_NORMAL:.2f}"
          f" (population {p / at(w, 'P', 1970):.2f} times its 1970 level)")
    print(f"  Population essentially stable by 2200 (p. 81): {at(w, 'P', 2200) / 1e9:.2f} billion in 2200,"
          f" {at(w, 'P', 2300) / 1e9:.2f} in 2300")
    _, v = peak(w, "CI");    print(f"  Capital investment rises to 38 billion (p. 84): {v / 1e9:.1f} billion")
    print(f"  ...a capital-investment ratio CIR of 3.9 (p. 84): {np.max(w['CI'] / w['P']):.2f}")
    print(f"  MSL rises to 2.3 times the 1970 value (p. 84): {np.max(w['MSL']) / at(w, 'MSL', 1970):.2f} times")
    print(f"  CIAF from 0.28 in 1970 to 0.55 in 2300 (p. 84): {at(w, 'CIAF', 1970):.3f} to {at(w, 'CIAF', 2300):.3f}")
    print(f"  Quality of life drops to about 0.8 of its 1970 value (p. 86): {at(w, 'QL', 2300) / at(w, 'QL', 1970):.2f}")

    f, _ = run(version, "food")
    print("\nFOOD SHORTAGE (crowding changes plus flat crowding tables for births and deaths)")
    _, p = peak(f, "P");     print(f"  Population rises to 10.8 billion (p. 88): {p / 1e9:.2f} billion")
    print(f"  The food ratio declines to 0.77 (p. 90): lowest {np.min(f['FR']):.2f}, {at(f, 'FR', 2300):.2f} in 2300")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "world2_1_isomorph")

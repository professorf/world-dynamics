# Validation

This folder records how the three Python versions of World2 were checked against Jay W. Forrester's *World Dynamics* (2nd ed., 1973), and holds the tools to repeat every check.

| Script | What it is |
|---|---|
| `world2_1_isomorph.py` | The DYNAMO listing, card for card |
| `world2_2_readable.py` | The same lines, with readable names |
| `world2_3_modern.py` | Modern Python: the same single time loop, plus policy switches for experiments |

**Summary.** Each version reproduces every figure in Chapter 4 of *World Dynamics*: the standard run and the book's three policy experiments (Figures 4-1 to 4-12, out to the year 2300). Version 2 is bit-for-bit identical to version 1 in every experiment, and version 3 matches version 1 to within floating-point rounding.

## What's in this folder

| Path | What it is |
|---|---|
| `tools/experiments.py` | Runs every version under every experiment and compares them |
| `tools/checkpoints.py` | Prints our numbers for every statement checked in the book's text |
| `tools/extract_pages.py` | Makes page images from your own scan of Chapter 4 |
| `tools/calibrate.py`, `tools/figures.py`, `tools/make_overlays.py` | Draw our runs on the book's figures |
| `world2_1_isomorph_ORIG-A.png`, `world2_1_isomorph_ORIG-B.png` | What version 1 draws from the listing's two PLOT cards |
| `world2_2_readable_ORIG-A.png`, `world2_2_readable_ORIG-B.png` | The same plots from version 2 |
| `world2_3_modern_runs.png` | What version 3 draws: the standard run and the pollution crisis |

Every file name starts with the script that produced it.

## The four experiments

The changes are the ones printed in each figure's margin as PRESENT against ORIGINAL values.

| Experiment | Figures | Changes from the standard run |
|---|---|---|
| Standard run | 4-1 to 4-4 | none |
| Pollution crisis | 4-5 to 4-8 | NRUN1 = 0.25 (was 1) |
| Crowding | 4-9, 4-10 | NRUN1 = 0, POLN1 = 0.1 (was 1), LENGTH = 2300 (was 2100) |
| Food shortage | 4-11, 4-12 | the crowding changes, plus DRCMT = .9/1/1/1/1/1 (was .9/1/1.2/1.5/1.9/3) and BRCMT = 1.05/1/1/1/1/1 (was 1.05/1/.9/.7/.6/.55) |

NRUN1 and POLN1 are the values after the 1970 switch, so every experiment follows the standard run exactly until 1970.

How each version runs an experiment:

- **Versions 1 and 2:** the changed cards are edited in a copy of the script, as a DYNAMO user would have changed cards and rerun. For example `NRUN1 = .25` in version 1, or `natural_resource_usage_normal_1 = .25` in version 2.
- **Version 3:** through its policy dictionary, its table definitions, and the `end_year` argument of `simulate()`.

## 1. Agreement between the three versions

`python validation/tools/experiments.py` gives the largest relative difference from version 1, over every recorded variable at every time step:

| Experiment | Version 2 | Version 3 |
|---|---|---|
| Standard run | bit-identical | 1.3 parts in 10^15 |
| Pollution crisis | bit-identical | 5.1 parts in 10^15 |
| Crowding | bit-identical | 1.4 parts in 10^15 |
| Food shortage | bit-identical | 5.4 parts in 10^16 |

Version 2 changes only names, so its arithmetic is the same operation for operation. Version 3 looks up its tables with numpy, which can differ in the last digit. No table input left its range (the condition DYNAMO's TABLE function flags) in any of the four experiments.

## 2. Overlays on the book's figures

Every version's runs were drawn on scans of all twelve figures in Chapter 4. The curves land on the points Forrester's DYNAMO run printed, in every figure, for every version. Because the three versions agree to rounding, their overlays are pixel-for-pixel identical apart from the header naming the script.

The scans are not distributed with this repository (see `NOTICE.md`). To make the overlays yourself from your own copy of the book:

```
python validation/tools/extract_pages.py chapter4.pdf --first-page 66
python validation/tools/make_overlays.py
```

The first command turns a scanned PDF of Chapter 4 (two book pages per sideways scan, as ours was) into page images `p066.png` ... in `validation/book-pages/`. Scans laid out differently need their own page images, named by book page, and possibly adjusted plot boxes in `tools/figures.py`. The second command writes `validation/book-overlays/<script>_fig4-NN.png`, twelve per version. Both folders are git-ignored, so the book's pages never enter the repository.

How to read an overlay: the header names the script, the book figure and the experiment, and gives a color legend with each curve's name, the symbol the book plots it with, and its scale. Below the header is the scanned page with our curves drawn on top. The black letters on each page are the points Forrester's DYNAMO run printed, one every 4 years (PLTPER = 4). The black ink curves were drawn through those points by hand for publication, so where the ink and the letters disagree, the letters are the data. Two places show this clearly: near the capital-investment peak in Figure 4-5, and at the death-rate spike in Figure 4-8. That spike falls between two 4-year plot points, so the ink could not show its true height. As in the book, any part of a curve beyond its scale is not drawn.

Method: each page is straightened (by up to 2.2 degrees on our scans), its dotted gridlines are located automatically, and every value is mapped onto that figure's own scale as printed on the figure. The two-page figures (4-9 to 4-12) are shown with both pages side by side.

## 3. Checkpoints from the book's text

`python validation/tools/checkpoints.py` prints the right-hand column.

| Book says | Our run |
|---|---|
| **Standard run** | |
| Population peaks in 2020 (p. 69) | 2020.4, at 5.30 billion |
| Natural-resource-usage rate peaks about 2010 (Fig. 4-3) | 2008.8 |
| Capital-investment generation declines after 2010 (Fig. 4-4) | peaks in 2008.8 |
| ...but does not fall below discard until 2040, when capital investment begins to decline (Fig. 4-4) | crosses in 2040.8; CI peaks in 2040.8 |
| CIAF rises during the first hundred years from 0.2 to 0.32 (p. 72) | peaks at 0.321 (2011) |
| Material standard of living peaks at about 2000 (p. 72) | 1993.6 |
| Pollution peaks in the year 2060 at some 6 times the level in 1970 (p. 70) | 2050.6, at 7.1 times (see below) |
| Quality of life peaks around the year 1960 (p. 70) | 1945.2 (see below) |
| **Pollution crisis** | |
| Pollution rises to more than 40 times the condition in 1970 (p. 75) | 54 times its 1970 level |
| Population drops in 20 years to one-sixth of its peak value (p. 75) | 17.4 years from the start of the collapse (below 90% of peak in 2043.2, one-sixth of peak in 2060.6) |
| Quality of life dips suddenly and deeply, with a rapid rise after 2060 (p. 76) | falls to 0.19 in 2054, rises to 5.3 by 2070 |
| **Crowding** | |
| Population rises to about 9.7 billion (p. 81) | 9.69 billion |
| ...a crowding ratio CR of 2.65 (p. 81) | CR peaks at 2.71 (population 2.63 times its 1970 level) |
| Population is essentially stable by 2200 (p. 81) | 9.65 billion in 2200, 9.69 billion in 2300 |
| Capital investment rises to 38 billion units (p. 84) | 37.5 billion |
| ...a capital-investment ratio CIR of 3.9 (p. 84) | 3.88 |
| Material standard of living rises to 2.3 times the 1970 value (p. 84) | 2.32 times |
| CIAF rises from 0.28 in 1970 to 0.55 in 2300 (p. 84) | 0.280 in 1970, 0.552 in 2300 |
| Quality of life drops to about 0.8 of its 1970 value (p. 86) | 0.81 |
| **Food shortage** | |
| Population rises to 10.8 billion (p. 88) | 10.75 billion |
| The food ratio declines to 0.77 (p. 90) | 0.81 (see below) |

Three statements in the text do not match the book's own figures:

- Pollution in the standard run peaks "in the year 2060". Figure 4-1 shows the peak near 2050, as does our run.
- Quality of life in the standard run "peaks around the year 1960". Figure 4-1 shows the peak in the 1940s; ours is 1945.2.
- The food ratio in the food-shortage run "declines to 0.77". In Figure 4-12 the printed F points level off near 0.81 on both pages, as does our run.

In each case our run agrees with the plotted data, so the text's numbers are approximate.

## 4. An independent implementation

[pyworld2](https://github.com/cvanwynsberghe/pyworld2) (version 1.1, Charles Vanwynsberghe, MIT license) is a separate Python implementation of World2 with a different program structure. Over all 1001 time steps of the standard run, its largest relative difference from ours is about 2 parts in 10^15 for every level and the main auxiliaries (P, NR, CI, POL, CIAF, POLR, FR, MSL, QL).

pyworld2 also includes the pollution-crisis experiment, and there the two programs differ by up to 1.8%. The cause is the switch time. pyworld2 builds its time axis with `numpy.arange`, which accumulates rounding, so its "1970" step is really 1970.000000000016. The switch test "is TIME still at or before 1970?" then fails, and the switch fires one step (0.2 years) early. Moving our switch one step earlier, as a diagnostic only, makes the two programs agree to 1.3 parts in 10^15. Our versions follow DYNAMO's definition of CLIP: the old value up to and including the switch year. A 0.2-year shift is far too small to see at the scale of the book's figures, so the book cannot tell us which one Forrester's own run did.

---

Quotations are from Jay W. Forrester, *World Dynamics*, 2nd ed. (Wright-Allen Press, 1973), Chapter 4, reproduced here only for comparison with the model output.

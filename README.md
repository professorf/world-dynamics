# World2 in Python

A staged, validated translation of Jay W. Forrester's **World2** model, from his book *World Dynamics* (1971; 2nd ed. 1973), into Python.

World2 is one of the founding models of system dynamics: five interacting stocks (population, natural resources, capital investment, pollution, and the fraction of capital in agriculture) simulated from 1900 to 2100. Forrester wrote it in DYNAMO, the simulation language of its day. This repository translates it in three stages, each one readable on its own, and checks every stage against the original book.

**Authors:** Nick V. Flor (University of New Mexico, nickflor@unm.edu) and Claudia (Claude Interactive Assistant), i.e., Claude, an AI model by Anthropic. See [How this was made](#how-this-was-made) for who did what, and [CITE.md](CITE.md) to cite it.

## Quick start

```
pip install -r requirements.txt
python world2_1_isomorph.py       # standard library only; matplotlib draws the plots
python world2_2_readable.py
python world2_3_modern.py         # needs numpy
```

Versions 1 and 2 reproduce the book's standard run and draw the two plots defined by the listing's PLOT cards. Version 3 runs the standard run and the book's pollution-crisis experiment, prints a short summary of each, and plots them side by side.

## What's here

| File | What it is |
|---|---|
| `source-code.dyn` | Forrester's DYNAMO listing, transcribed from Appendix B of the book |
| `definition-of-terms.md` | The book's glossary of every variable and constant (Appendix C) |
| `causal-loop-diagram.md` | The model as a Mermaid diagram, generated from the equations, with a + or - sign on every link |
| `world2_1_isomorph.py` | Version 1: the DYNAMO listing, card for card |
| `world2_2_readable.py` | Version 2: the same lines, with readable names |
| `world2_3_modern.py` | Version 3: modern Python, the same single time loop, with policy switches for experiments |
| `validation/` | How each version was checked against the book, with results |
| `tools/make_causal_loop_diagram.py` | Regenerates the diagram from `source-code.dyn` |

## The three versions

The versions change one thing at a time, so a reader can see each change on its own.

**Version 1, `world2_1_isomorph.py`.** Every DYNAMO card appears as a comment, with its Python translation directly below it. Variable names keep DYNAMO's time suffixes (`P_J`, `P_K`, `BR_JK`, `BR_KL`), so the timing of every value stays visible, and DYNAMO's `CLIP`, `TABLE` and `TABHL` functions keep their names and argument order. This is the version to read side by side with the book.

**Version 2, `world2_2_readable.py`.** The same lines in the same order, with every abbreviation spelled out using the book's own definitions (`P` becomes `population`, `MSL` becomes `material_standard_of_living`). The DYNAMO cards stay as comments, so the file also works as a lookup between the two sets of names. Its results are bit-for-bit identical to version 1.

**Version 3, `world2_3_modern.py`.** The same model and the same single loop, read top to bottom, with no classes. The model is a function, `simulate(policy)`, so it can be run under different policies and compared. The seven policy switches (DYNAMO's `CLIP` cards) sit in one dictionary at the top, tables are numpy lookups, and levels update in place at the end of each step. Its results match version 1 to within floating-point rounding.

## Methodology

### 1. Transcribing the source

The DYNAMO listing (Appendix B) and the glossary (Appendix C) were transcribed from scans of the 2nd edition. Each column of each page was then re-read from zoomed-in crops to check the transcription line by line. Two flaws in the scan were resolved against the book's chapter text, where the same equations are printed again: card 22.1 reads `CIAFN= 3` with its decimal point lost (the value is `.3`), and the closing parenthesis of equation 9 is smudged. As a cross-check, every name used in the listing has an entry in the glossary (apart from DT and LENGTH, which are DYNAMO's own run settings), and every glossary entry is used in the listing.

### 2. Reading DYNAMO correctly

Three features of DYNAMO shape the translation:

- **Time suffixes.** `.J` is the previous moment, `.K` the present, `.JK` a rate over the interval just ended, and `.KL` a rate over the coming interval. Each step of DT = 0.2 years computes the levels at K from the levels at J and the rates over JK, then the auxiliaries at K, then the rates over KL.
- **Order.** DYNAMO did not run its listing top to bottom. The compiler sorted the auxiliary equations so that each is computed after everything it uses (equation 3 uses MSL, which is defined in equation 4). Python runs top to bottom, so inside the time loop the auxiliaries appear in sorted order, each still tagged with its book equation number.
- **Switches and tables.** `CLIP(A, B, X, Y)` returns A while X >= Y, so `CLIP(BRN, BRN1, SWT1, TIME)` gives the old value up to and including the switch year 1970 and the new value after it. Repeatedly adding 0.2 in floating point drifts away from round numbers, so TIME is rounded at each step to make the switches fire at exactly the right step. `TABHL` interpolates in a table and holds its end values outside the range; `TABLE` does the same for inputs expected to stay in range, and no input leaves its range in any run.

### 3. The diagram

`causal-loop-diagram.md` was generated from the equations by `tools/make_causal_loop_diagram.py`, not traced from the book's figure. Every variable used on the right side of an equation gets an arrow into the variable on the left. Each arrow's sign comes from the equation's algebra (a numerator gives +, a denominator gives -) or from the slope of its table. Every table in the model only rises or only falls, so each link has a single sign everywhere. The script stops if the parsed arrows and the sign list disagree. The diagram was test-rendered with the Mermaid command-line renderer to confirm it parses.

### 4. Validation against the book

Each version was run under all four experiments in Chapter 4 of *World Dynamics*: the standard run, and the book's pollution-crisis, crowding and food-shortage experiments, using the parameter changes printed in each figure's margin.

- **Against each other.** In every experiment, version 2 is bit-for-bit identical to version 1, and version 3 differs by at most about 5 parts in 10^15.
- **Against the book's figures.** Every run was drawn on scans of all twelve figures in Chapter 4 (4-1 to 4-12, out to the year 2300). The curves land on the points Forrester's DYNAMO run printed. The scans are not distributed here; `validation/tools/` regenerates the overlays from your own copy of the book.
- **Against the book's text.** Twenty-one numerical statements in Chapter 4 were checked: peak years, peak values and ratios.
- **Against an independent implementation.** The standard run matches [pyworld2](https://github.com/cvanwynsberghe/pyworld2) to about 2 parts in 10^15.

Two findings came out of the validation. Three numbers in Chapter 4's text disagree with the book's own plotted data, and in each case our runs agree with the plots. And pyworld2's pollution-crisis run differs from ours by up to 1.8%, because floating-point drift in its time axis fires the 1970 switch one step early. Full results are in [validation/README.md](validation/README.md).

### 5. Known limitations

- Faithful to Forrester's equations is not the same as true of the world. Forrester himself warns that the model's assumptions "will need to be carefully reexamined before substantial dependence is placed on the dynamics" (p. 76).
- The exact behavior of `CLIP` at the step where TIME equals the switch year follows DYNAMO's definition as we understand it; it has not been checked against a DYNAMO manual. It affects a single 0.2-year step and is invisible at the scale of the book's figures.

## How this was made

This project was a collaboration between a person and an AI, carried out in conversation.

**Nick V. Flor** set the goal (a version of World2 that teaches system dynamics from its origins), designed the staged approach (a literal isomorph first, then readable names, then a modern version that keeps the single visible loop), made the design decisions along the way (including the Mermaid diagram and the file naming), supplied the scans of the book, checked the two scan flaws against the book's text, and set the scope of the validation.

**Claudia** (Claude, an AI model by Anthropic) transcribed the listing and glossary from the scans, wrote the three Python versions, the diagram generator and the validation tools, ran and analyzed the validation, and drafted the documentation.

## Reproducing the validation

The cross-version comparison and the checkpoints need only this repository:

```
python validation/tools/experiments.py     # how closely the three versions agree, in all four experiments
python validation/tools/checkpoints.py     # our numbers for every statement checked in the book's text
```

The figure overlays need your own copy of *World Dynamics*, Chapter 4. See [validation/README.md](validation/README.md).

## Citing

See [CITE.md](CITE.md). GitHub's "Cite this repository" button uses [CITATION.cff](CITATION.cff). If you use the model, please cite Forrester's book as well.

## License

The code and documentation written for this project are released under the [MIT License](LICENSE). Material reproduced from *World Dynamics* (the transcribed listing and glossary, and short quotations) is not covered by that license; see [NOTICE.md](NOTICE.md).

## Acknowledgments

Jay W. Forrester (1918-2016), who created World2 and the field of system dynamics. Charles Vanwynsberghe, whose pyworld2 served as an independent check.

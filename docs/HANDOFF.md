# Handoff: start here in a new session

This file brings a new session up to speed on the project. It says where things stand, how we work, how the model is built, and what Stage 5 (extensions) might be. Read it first, then the files it lists.

## The project

Nick V. Flor (University of New Mexico) and Claudia (Claude Interactive Assistant) translated Jay W. Forrester's *World2* from his book *World Dynamics* (MIT Press, 1971; 2nd ed. 1973) from DYNAMO into Python. Each stage was checked against the book before the next one started. This is the first project in the cyber-coding method; Urban Dynamics (also in this account) is the second.

The model is archived on Zenodo ([doi.org/10.5281/zenodo.23126731](https://doi.org/10.5281/zenodo.23126731)).

## Where things stand

| Stage | What | Result |
|---|---|---|
| 0 | The listing and glossary recovered from scanned appendices | Transcribed and re-read; two flaws in the scan resolved against the book's chapter text; cross-check: every name in the listing has a glossary entry and vice versa |
| 1 | Version 1: the listing card for card | The DYNAMO card appears as a comment, Python translation below it. Time suffixes (`_J`, `_K`, `_JK`, `_KL`) kept visible. Checked against the book's standard run and four Chapter 4 experiments in 12 overlaid plots; 21 numerical text statements verified |
| 2 | Version 2: readable names | Every abbreviation spelled out from the glossary. Identical to version 1: bit-for-bit in all runs. Still shows DYNAMO cards as comments |
| 3 | Version 3: modern Python | Single time loop, no classes; one `simulate(policy, tables)` function. Seven policy switches in a dict at the top, 22 tables in another. Results match version 1 to within floating-point rounding (~5 × 10^-15) |
| 4 | Interactive app on version 3 (Dash) | Standard run, Chapter 4 experiments as buttons, sliders for policy switches and run length. Every chart shows the run in blue over the standard run in gray |

All stages done and committed.

## Read these, in this order

1. `README.md`: status, file map, how to run.
2. This file.
3. `source-code.dyn` and `definition-of-terms.md`: the listing and the glossary.
4. `causal-loop-diagram.md`: the model as a causal-loop diagram, generated from the equations.
5. `world2_1_isomorph.py`, then `world2_2_readable.py`, then `world2_3_modern.py`: watch how each stage changes form without changing the numbers.
6. `validation/`: how each version was checked.
7. `world2_4_dash_app.py`: the app.

## How we work

- Nick runs every git command. Claudia does not commit or push. Commit messages have a short subject, a short body, and the last line `Authors: Nick V. Flor & Claudia (Claude Interactive Assistant)`, with no other trailer.
- The model files are generated or curated: version 1 from the listing, version 2 by renaming version 1, version 3 by restructuring version 2. Change the source or the generation step, not a model file.
- Every stage has a target and a check. A check counts only if it can fail, so it is also run against a deliberately broken copy.
- Paper material stays out of tracked files.
- Writing: short paragraphs, one idea at a time. In anything Nick will post: no em dashes, no "this is not X, it's Y" endings, and never the phrase "load bearing".
- Model choice: a larger model for design discussions, a smaller one for building once the design is written down.

## The model in one page

Five interacting global stocks from 1900 to 2100, one 0.2-year time step. Stocks: population (P), natural resources (NR), capital investment (CI), pollution (POLL), and the fraction of capital in agriculture (FIOAC). Time delays (22 delay equations) and table functions (22 lookup tables) govern flows between stocks.

**The core loop:** investment grows capital, capital produces output (food and industrial goods), output depletes resources and creates pollution. Death rate rises with pollution and falls with food and industrial output. Birth rate falls with development (higher standard of living and crowding). Population grows at first, peaks as development advances, then declines as standard of living rises and pollution peaks. Capital grows, peaks, and declines as resources run low and investment switches to agriculture. The model runs to 2100.

**Policy switches.** Seven `CLIP` functions let the model switch between two parameter values at a specified year, so it can run experiments: using non-renewable resources more or less, limiting capital growth, switching investment to agriculture at different times, and adding crowding effects to birth and death rates. The book's four experiments in Chapter 4 are the standard run and three policy shifts.

**What the model does not have.** No distinction between countries, continents or regions. No energy as a separate stock. No technology as a variable (technology is implicit in the tables). Population has no age structure.

## Stage 5: extensions

The earlier work (Stages 1-4) built what Nick calls a metamorph: changed in form, isomorphic to the original in behavior. Stage 5 would co-opt the model for purposes Forrester did not have. No work has been done on extensions to World2 yet, but the method is the same as for Urban Dynamics: the exaptation/secondary-adaptation framework from evolutionary biology (Gould & Vrba, 1982).

**If extending World2:** read `docs/HANDOFF.md` in the Urban Dynamics project for the method and rules (anchor check, one extension at a time, validation criteria).

## Authors

Nick V. Flor (University of New Mexico) and Claudia (Claude Interactive Assistant), i.e., Claude, an AI model by Anthropic.

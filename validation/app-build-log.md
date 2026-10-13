# How the app was built: a stage-by-stage log

`world2_4_dash_app.py` was built in stages, each with its own target and check, and each committed before the next began. This log records what each stage added, how it was checked, and what the checks found. It is part of the record the paper describes as the project's residua: a learner can read it next to the commit history and follow the app from nothing to finished, one idea at a time.

The app holds no model of its own. It imports `simulate()` from `world2_3_modern.py` and only draws what it returns, so every check below compares the app's curves with version 3's validated runs and with version 1, the card-for-card isomorph.

Every stage had two kinds of check:

- **Numeric:** `validation/tools/check_dash_app.py`, which calls the app's callbacks the way Dash does and compares every curve with the validated runs.
- **Visual:** the page loaded in a headless browser and screenshotted at three widths (1440, 1024 and 390 pixels), with sliders moved and buttons pressed.

The numeric check passed on its first run at every stage. Every problem below was found by looking.

## Stage 1: the standard run in the browser

- **Target:** the listing's two PLOT cards (the book's Figures 4-1 and 4-2), drawn from `simulate()`, on the book's scales.
- **New idea in Dash:** a page layout. No callbacks yet; the page is built once, when the app starts.
- **Numeric check:** all ten curves are `simulate()`'s output unchanged; the largest relative difference from version 1 is 1.0 part in 10^15.
- **What looking at the page found:**
  1. Five charts in one wide figure: their titles collided at 1024 pixels. Fixed by giving each variable its own chart in a grid that wraps (simpler code, too).
  2. One title was cut off. Shortened to "Agricultural capital fraction (CIAF)".
  3. Dash's debug mode laid a developer toolbar over the page and logged a connection error. Debug is now off by default, with a comment saying how to turn it on.
  4. Hovering drew two vertical lines. Fixed by removing an explicit hover-line setting.

None of these would show up in a numeric check. An app has two kinds of target: its numbers, and being readable on any screen.

## Stage 2: policy sliders

- **Target:** sliders for the seven policy switches (the value after the switch, as a percent of its standard value), the switch year and the end year.
- **New idea in Dash:** the callback. The charts start empty, and Dash runs the callback once when the page loads to fill them.
- **Numeric check:** set to the book's values, the sliders give the book's card values exactly (NRUN1 = .25, POLN1 = .1), and the charts are version 3's validated standard, pollution-crisis and crowding runs, bit for bit.
- **A floating-point detail caught in design:** `before * percent / 100` turns the death rate normal of 0.028 into 0.028000000000000004 at 100%, so the standard run would no longer be the standard run. `before * (percent / 100)` keeps 100% exact, and gives the book's .25 and .1 exactly.
- **What looking at the page found:** labels repeated the DYNAMO card name; Dash's purple accent competed with the blue data line (set to gray); wrapped labels pushed some sliders out of line (fixed with a column layout); a focused slider covered its label (more spacing).

## A gap in the process

Stage 2 overwrote stage 1 in the working folder before stage 1 had been committed. Neither check could see this, because both looked at the code, and the code was fine. Nick noticed: "We should have checked in stage 1." Stage 1 was restored from a copy Claudia had kept, the two stages were committed in order, and from then on every stage was committed before the next began. A stage is only a stable subassembly once it is committed.

## Stage 3a: `simulate()` takes the tables

- **Why:** the book's food-shortage experiment changes two tables (BRCMT and DRCMT), which no policy switch can express, and `simulate()` accepted only a policy. This was the first change to the recovered model since it was validated, so it was made as its own stage, apart from the interface.
- **The change:** version 3's 22 table constants became one dictionary, `STANDARD_TABLES`, each table filed under the variable it produces, and `simulate(policy, tables)` takes it as an argument. `experiments.py` now passes tables as an argument instead of overwriting the module's constants, which would not be safe in a web server answering several requests at once.
- **Checks:** old and new version 3 are bit-identical in all four experiments, in every variable at every step; `experiments.py` gives the same agreement table as before; `checkpoints.py` prints byte-identical output; version 3's own plot is pixel-identical; the app's check still passes.

## Stage 3b: experiment buttons, the comparison line, the crowding tables

- **Target:** one button for each of the book's four Chapter 4 experiments, the standard run drawn in gray behind every chart, and a control for the crowding tables. The model is untouched.
- **New idea in Dash:** a second callback (the buttons set the controls) chained into the first (the controls redraw the charts). Everything a button sets is visible as a control, so there is no hidden state.
- **Numeric check:** pressing each button gives the book's values exactly, including both changed tables for the food shortage; the blue curves are version 3's validated runs, bit for bit, in all four experiments; the gray curves are the standard run. Largest relative differences from version 1: 1.0, 5.1, 1.0 and 0.30 parts in 10^15.
- **What looking at the page found:** a style meant for slider labels also split the crowding control's options onto two lines (fixed by narrowing the style to slider labels); 400-year runs crowded the year labels until they tilted (100-year ticks for long runs).
- On the page, the food-shortage run levels off near 10.75 billion people with a food ratio near 0.81, as in the book's Figures 4-11 and 4-12.

All checks were rerun in a clean copy of the repository before the stage was committed.

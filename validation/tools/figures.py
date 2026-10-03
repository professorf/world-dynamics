# SPDX-License-Identifier: MIT
"""Every Chapter 4 figure of World Dynamics: its pages, its experiment, and what it plots.

Scales come from each figure's printed scale labels (and, for 4-1 / 4-2, the PLOT
cards in source-code.dyn). A curve is drawn as (value - low) / (high - low) of
the plot's height, exactly as DYNAMO's printer plots did.

Page images are named by book page (p070.png is page 70). Each plot box is a
rough rectangle around the plot on our scans; with different scans, adjust the
boxes so each one contains its plot's gridlines but not the body text.

Authors: Nick V. Flor (University of New Mexico) and Claudia (Claude
Interactive Assistant), i.e., Claude, an AI model by Anthropic. See CITE.md.
"""

# (page image, number of vertical divisions, first year on the page, plot box x0, y0, x1, y1)
PAGE = {
    "4-1":   [("p070.png", 4, 1900, (190, 225, 1065, 870))],
    "4-2":   [("p071.png", 4, 1900, (150, 222, 1030, 865))],
    "4-3":   [("p072.png", 4, 1900, (160, 190, 1035, 840))],
    "4-4":   [("p073.png", 4, 1900, (138, 212, 1015, 855))],
    "4-5":   [("p075.png", 4, 1900, (160, 195, 1035, 840))],
    "4-6":   [("p077.png", 4, 1900, (128, 230, 1005, 875))],
    "4-7":   [("p079.png", 4, 1900, (136, 198, 1015, 842))],
    "4-8":   [("p081.png", 4, 1900, (131, 226, 1010, 868))],
    "4-9":   [("p082.png", 8, 1900, (165, 140, 1085, 1425)),
              ("p083.png", 8, 2100, (90, 170, 990, 1450))],
    "4-10":  [("p084.png", 5, 1900, (150, 190, 1035, 1000)),
              ("p085.png", 5, 2100, (90, 190, 985, 1000))],
    "4-11":  [("p088.png", 6, 1900, (152, 190, 1040, 1150)),
              ("p089.png", 6, 2100, (98, 190, 985, 1150))],
    "4-12":  [("p090.png", 4, 1900, (142, 215, 1035, 875)),
              ("p091.png", 4, 2100, (95, 218, 985, 875))],
}

EXPERIMENT = {"4-1": "standard", "4-2": "standard", "4-3": "standard", "4-4": "standard",
              "4-5": "pollution", "4-6": "pollution", "4-7": "pollution", "4-8": "pollution",
              "4-9": "crowding", "4-10": "crowding", "4-11": "food", "4-12": "food"}

EXPERIMENT_LABEL = {
    "standard": "standard run (no changes)",
    "pollution": "NRUN1 = 0.25 from 1970 (pollution crisis)",
    "crowding": "NRUN1 = 0, POLN1 = 0.1 from 1970, run to 2300 (crowding)",
    "food": "as crowding, plus BRCMT and DRCMT set to 1 above CR = 1 (food shortage)",
}

# Colors for our curves: the validated categorical palette, slots 1-5, assigned
# in the order the curves are listed for each figure.
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]

# variable, plot symbol, scale low, scale high
A_STD = [("P", "P", 0, 8e9), ("POLR", "2", 0, 40), ("CI", "C", 0, 20e9),
         ("QL", "Q", 0, 2), ("NR", "N", 0, 1000e9)]
B_STD = [("FR", "F", 0, 2), ("MSL", "M", 0, 2), ("QLC", "4", 0, 2),
         ("QLP", "5", 0, 2), ("CIAF", "A", .2, .6)]

CURVES = {
    "4-1": A_STD,
    "4-2": B_STD,
    "4-3": [("NR", "N", 0, 1000e9), ("NRUR", "U", 0, 8e9)],
    "4-4": [("CI", "C", 0, 20e9), ("CIG", "G", 0, 400e6), ("CID", "D", 0, 400e6)],
    "4-5": A_STD,
    "4-6": B_STD,
    "4-7": [("POLR", "2", 0, 40), ("POLAT", "T", 0, 16),
            ("POLG", "G", 0, 20e9), ("POLA", "A", 0, 20e9)],
    "4-8": [("P", "P", 0, 8e9), ("BR", "B", 0, 400e6), ("DR", "D", 0, 400e6)],
    # 4-9: the plot is twice as tall; the 8000 M / 40 / 20 B / 2 / 1000 B labels sit at mid-height
    "4-9": [("P", "P", 0, 16e9), ("POLR", "2", 0, 80), ("CI", "C", 0, 40e9),
            ("QL", "Q", 0, 4), ("NR", "N", 0, 2000e9)],
    # 4-10: five divisions, 0 to 2.5 and 0.2 to 0.7
    "4-10": [("FR", "F", 0, 2.5), ("MSL", "M", 0, 2.5), ("QLC", "4", 0, 2.5),
             ("QLP", "5", 0, 2.5), ("CIAF", "A", .2, .7)],
    # 4-11: six divisions, population to 12 B and capital to 30 B
    "4-11": [("P", "P", 0, 12e9), ("POLR", "2", 0, 60), ("CI", "C", 0, 30e9),
             ("QL", "Q", 0, 3), ("NR", "N", 0, 1500e9)],
    "4-12": B_STD,
}

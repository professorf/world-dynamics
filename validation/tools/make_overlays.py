# SPDX-License-Identifier: MIT
"""Draw each Python version's runs on every Chapter 4 figure of World Dynamics.

Input:  page images p070.png ... p091.png in validation/book-pages/, made from
        your own copy of the book (see extract_pages.py).
Output: validation/book-overlays/<script>_fig4-NN.png, 12 figures per version.

Each image has a header naming the script, the figure and the experiment, and
a legend giving every colored curve with its book plot symbol and scale. Below
it is the scanned page (straightened) with our curves drawn on top. As in the
book, any part of a curve beyond its scale is not drawn.

Usage (from the repository root):
    python validation/tools/make_overlays.py                     # all three versions
    python validation/tools/make_overlays.py world2_3_modern     # one version

Needs: numpy, pillow and matplotlib (for its bundled DejaVu fonts).

Authors: Nick V. Flor (University of New Mexico) and Claudia (Claude
Interactive Assistant), i.e., Claude, an AI model by Anthropic. See CITE.md.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import figures
from calibrate import calibrate, PAGES
from experiments import EXPERIMENTS, VERSIONS, run

OUT = Path(__file__).resolve().parents[1] / "book-overlays"
INK, MUTED = (11, 11, 11), (82, 81, 78)

NAME = {"P": "population", "POLR": "pollution ratio", "CI": "capital investment",
        "QL": "quality of life", "NR": "natural resources", "FR": "food ratio",
        "MSL": "material standard of living", "QLC": "quality of life from crowding",
        "QLP": "quality of life from pollution", "CIAF": "capital-investment-in-agriculture fraction",
        "NRUR": "natural-resource-usage rate", "CIG": "capital-investment generation",
        "CID": "capital-investment discard", "POLAT": "pollution-absorption time",
        "POLG": "pollution generation", "POLA": "pollution absorption",
        "BR": "birth rate", "DR": "death rate"}


def fonts():
    from matplotlib import font_manager
    regular = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans"))
    bold = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold"))
    return ImageFont.truetype(bold, 24), ImageFont.truetype(regular, 18)


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def fmt(v):
    if v >= 1e9:
        return f"{v / 1e9:g} B"
    if v >= 1e6:
        return f"{v / 1e6:g} M"
    return f"{v:g}"


def draw_page(img, x_of_year, y_of_frac, result, curves, year_from, year_to):
    rgb = img.convert("RGB")
    d = ImageDraw.Draw(rgb)
    t = result["TIME"]
    keep = (t >= year_from - 1e-9) & (t <= year_to + 1e-9)
    for (var, _symbol, lo, hi), color in zip(curves, figures.SLOTS):
        segment = []
        for year, value in zip(t[keep], result[var][keep]):
            f = (value - lo) / (hi - lo)
            if 0 <= f <= 1:                    # the book only plots inside the frame
                segment.append((x_of_year(year), y_of_frac(f)))
            else:
                if len(segment) > 1:
                    d.line(segment, fill=hex_rgb(color), width=3, joint="curve")
                segment = []
        if len(segment) > 1:
            d.line(segment, fill=hex_rgb(color), width=3, joint="curve")
    return rgb


def header(width, version, fig, curves, f_title, f_text):
    cols = 1 if width < 1600 else 2
    rows = (len(curves) + cols - 1) // cols
    height = 86 + 30 * rows + 14
    im = Image.new("RGB", (width, height), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((24, 14), f"{version}.py  on  World Dynamics, Figure {fig}", font=f_title, fill=INK)
    d.text((24, 52), "Experiment: " + figures.EXPERIMENT_LABEL[figures.EXPERIMENT[fig]], font=f_text, fill=MUTED)
    col_w = width // cols
    for i, ((var, symbol, lo, hi), color) in enumerate(zip(curves, figures.SLOTS)):
        x = 24 + (i // rows) * col_w
        y = 86 + 30 * (i % rows)
        d.line([(x, y + 11), (x + 40, y + 11)], fill=hex_rgb(color), width=5)
        d.text((x + 52, y), f"{var}  {NAME[var]}   [book symbol {symbol}, scale {fmt(lo)} to {fmt(hi)}]",
               font=f_text, fill=INK)
    d.line([(0, height - 2), (width, height - 2)], fill=(200, 200, 200), width=2)
    return im


_calibrations = {}


def overlay(version, fig, result, fonts_):
    curves = figures.CURVES[fig]
    panels = []
    for page, n_div, year0, box in figures.PAGE[fig]:
        if page not in _calibrations:
            _calibrations[page] = calibrate(page, n_div, year0, box, PAGES)
        img, x_of_year, y_of_frac, info = _calibrations[page]
        drawn = draw_page(img, x_of_year, y_of_frac, result, curves, year0, year0 + 200)
        top = max(0, int(info["y_top"]) - 120)
        bottom = min(img.height, int(info["y_zero"]) + 190)
        panels.append(drawn.crop((0, top, img.width, bottom)))
    width, height = sum(p.width for p in panels), max(p.height for p in panels)
    body = Image.new("RGB", (width, height), (255, 255, 255))
    x = 0
    for p in panels:
        body.paste(p, (x, 0))
        x += p.width
    head = header(width, version, fig, curves, *fonts_)
    out = Image.new("RGB", (width, head.height + height), (255, 255, 255))
    out.paste(head, (0, 0))
    out.paste(body, (0, head.height))
    return out


def main(versions):
    missing = [p for pages in figures.PAGE.values() for p, *_ in pages if not (PAGES / p).exists()]
    if missing:
        sys.exit(f"missing page images in {PAGES}: {', '.join(missing)} (see extract_pages.py)")
    OUT.mkdir(parents=True, exist_ok=True)
    fonts_ = fonts()
    for version in versions:
        results = {e: run(version, e)[0] for e in EXPERIMENTS}
        for fig in figures.PAGE:
            name = f"{version}_fig4-{int(fig.split('-')[1]):02d}.png"
            overlay(version, fig, results[figures.EXPERIMENT[fig]], fonts_).save(OUT / name, optimize=True)
            print("wrote", name)


if __name__ == "__main__":
    main(sys.argv[1:] or VERSIONS)

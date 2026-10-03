# SPDX-License-Identifier: MIT
"""Turn a scanned PDF of World Dynamics, Chapter 4, into one image per book page.

The overlays need page images of pp. 70-91 named p070.png ... p091.png in
validation/book-pages/. The book's scans are not distributed with this
repository, so you make these from your own copy of the book.

This script handles scans like ours: each PDF page is one sideways scan of a
two-page spread (left page, right page), with one embedded image per PDF page.
For other scans, adjust --rotate and --first-page, or produce the page images
another way; the overlay tools only need the p###.png files.

Usage (from the repository root):
    python validation/tools/extract_pages.py chapter4.pdf --first-page 66

--first-page is the book page number of the LEFT half of the first PDF page.
Needs: pip install pymupdf pillow

Authors: Nick V. Flor (University of New Mexico) and Claudia (Claude
Interactive Assistant), i.e., Claude, an AI model by Anthropic. See CITE.md.
"""
import argparse
import io
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parents[1] / "book-pages"


def page_image(doc, page, dpi=200):
    """The page's embedded scan at its native resolution, or a rendering if it has none."""
    images = page.get_images(full=True)
    if len(images) == 1:
        data = doc.extract_image(images[0][0])["image"]
        return Image.open(io.BytesIO(data)).convert("L")
    pix = page.get_pixmap(dpi=dpi, colorspace="gray")
    return Image.frombytes("L", (pix.width, pix.height), pix.samples)


def main():
    import pymupdf
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--first-page", type=int, required=True,
                    help="book page number of the left half of the first PDF page")
    ap.add_argument("--rotate", type=int, default=270,
                    help="degrees counterclockwise to turn each scan upright (default 270)")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(args.pdf)
    number = args.first_page
    for page in doc:
        spread = page_image(doc, page).rotate(args.rotate, expand=True)
        w, h = spread.size
        for half in (spread.crop((0, 0, w // 2, h)), spread.crop((w // 2, 0, w, h))):
            half.save(args.out / f"p{number:03d}.png")
            number += 1
    print(f"wrote p{args.first_page:03d}.png to p{number - 1:03d}.png in {args.out}")


if __name__ == "__main__":
    main()

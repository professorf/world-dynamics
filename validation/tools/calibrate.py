# SPDX-License-Identifier: MIT
"""Find the plot frame on a scanned page of World Dynamics.

1. Straighten the page: try small rotations and keep the one whose dark pixels
   line up best in rows. Dotted gridlines and printed text both sharpen when
   the page is level.
2. Find the dotted gridlines: columns and rows crossed by many separate dark runs.
3. Fit the gridlines to an evenly spaced set: 6 vertical lines (40 years apart)
   and n_div + 1 horizontal lines, tolerating a missing or faint line.

calibrate() returns the straightened image and two maps: year -> x pixel, and
fraction of the plot's height -> y pixel.

Authors: Nick V. Flor (University of New Mexico) and Claudia (Claude
Interactive Assistant), i.e., Claude, an AI model by Anthropic. See CITE.md.
"""
from pathlib import Path

import numpy as np
from PIL import Image

PAGES = Path(__file__).resolve().parents[1] / "book-pages"


def _score(img):
    a = np.asarray(img) < 160
    h = a.sum(axis=1).astype(float)
    return float((h ** 2).sum())


def straighten(img, region):
    """Rotate img by the angle (degrees) that best aligns the dark pixels inside region into rows."""
    def score(d):
        return _score(img.rotate(d, resample=Image.BILINEAR, fillcolor=255).crop(region))
    best = max(np.arange(-3, 3.001, 0.1), key=score)
    fine = max(np.arange(best - 0.1, best + 0.1001, 0.02), key=score)
    return img.rotate(fine, resample=Image.BICUBIC, fillcolor=255), float(fine)


def _runs_profile(a, axis):
    """Number of separate dark runs along each column (axis=0) or row (axis=1)."""
    d = np.diff(a.astype(np.int8), axis=axis) == 1
    return d.sum(axis=axis)


def _centers(profile, threshold):
    """Centers of the groups of neighboring positions whose profile reaches threshold."""
    idx = np.where(profile >= threshold)[0]
    groups, cur = [], []
    for i in idx:
        if cur and i - cur[-1] > 2:
            groups.append(cur)
            cur = []
        cur.append(i)
    if cur:
        groups.append(cur)
    return [float(np.average(g, weights=profile[g])) for g in groups]


def _fit_grid(cands, n_lines, s_min, s_max, tol=5):
    """Best evenly spaced set of n_lines among candidate positions."""
    best = None
    for i, x0 in enumerate(cands):
        for x1 in cands[i + 1:]:
            s = (x1 - x0) / (n_lines - 1)
            if not (s_min <= s <= s_max):
                continue
            expected = x0 + s * np.arange(n_lines)
            hits = [min(cands, key=lambda c: abs(c - e)) for e in expected]
            ok = [abs(h - e) <= tol for h, e in zip(hits, expected)]
            if sum(ok) < n_lines - 2:
                continue
            idx = np.array([j for j in range(n_lines) if ok[j]])
            pos = np.array([hits[j] for j in range(n_lines) if ok[j]])
            coef = np.polyfit(idx, pos, 1)
            resid = float(np.abs(np.polyval(coef, idx) - pos).mean())
            key = (sum(ok), -resid)
            if best is None or key > best[0]:
                best = (key, coef, idx, pos)
    return best


def _best_fit(profile, offset, n_lines, s_min, s_max):
    # A dense curve can raise the relative threshold above faint gridlines,
    # so also try a fixed threshold and keep the fit that finds more lines.
    fits = []
    for threshold in (max(25, 0.35 * profile.max()), 30):
        cands = [offset + c for c in _centers(profile, threshold)]
        f = _fit_grid(cands, n_lines, s_min, s_max)
        if f:
            fits.append(f)
    return max(fits, key=lambda f: f[0]) if fits else None


def calibrate(page, n_div, year0, region, pages_dir=PAGES):
    """page: image file name in pages_dir. n_div: number of vertical-scale divisions.
    year0: the first year on the page. region: (x0, y0, x1, y1) box around the plot."""
    img = Image.open(Path(pages_dir) / page).convert("L")
    img, angle = straighten(img, region)
    a = np.asarray(img) < 160
    x0, y0, x1, y1 = region
    sub = a[y0:y1, x0:x1]
    v = _best_fit(_runs_profile(sub, 0), x0, 6, 140, 200)
    h = _best_fit(_runs_profile(sub, 1), y0, n_div + 1, 90, 200)
    if not (v and h):
        raise RuntimeError(f"could not find the plot's gridlines on {page}; check its plot box in figures.py")
    (_, vcoef, vidx, _), (_, hcoef, hidx, _) = v, h
    # x = vcoef[1] + vcoef[0] * k, where year = year0 + 40 k
    # y = hcoef[1] + hcoef[0] * j, where j counts gridlines from the top (full scale) down
    x_of_year = lambda yr: vcoef[1] + vcoef[0] * (yr - year0) / 40
    y_of_frac = lambda f: hcoef[1] + hcoef[0] * (1 - f) * n_div
    info = dict(angle=angle, v_found=len(vidx), h_found=len(hidx),
                y_top=y_of_frac(1), y_zero=y_of_frac(0))
    return img, x_of_year, y_of_frac, info

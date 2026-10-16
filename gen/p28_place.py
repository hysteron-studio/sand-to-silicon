"""28 - The Place & Bond. A die placed face-down onto another, seen through: the lower pad grid
(squares) and the upper pad grid (rings) almost coincide; the residual error of this placement
- a shift plus a tiny rotation drawn from a 100 nm (3 sigma) machine - is magnified 10,000 times
into a field of accent arrows, with the 3-sigma circle and 40 earlier placements at the centre."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "28 - The Place & Bond", "title": "The Place & Bond", "seed": SEED,
  "placement_accuracy_nm_3sigma": 100, "magnification_of_error": 10000, "pad_grid": [21, 21],
  "mapping": {
    "pads": "21 x 21 pads per die; squares = lower die, rings = upper die",
    "error": "translation ~ N(0, 33 nm) per axis, rotation ~ N(0, 8 urad) about the die centre; arrow = error x 10000",
    "centre": "3-sigma circle (100 nm x 10000 = 1 mm -> 178 px) and 40 earlier placements as dots",
  },
  "sources": ["https://www.besi.com/products-technology/product-details/product/datacon-8800-chameo-ultra-plus-ac/ (100 nm @ 3 sigma)"],
}
cv = Canvas(SEED); rng = cv.rng
C = OUT / 2; n = 21; span = OUT - 2 * MARGIN - 200; p = span / (n - 1)
die_mm = 12.0; px_per_um = span / (die_mm * 1000)
mag = DATA["magnification_of_error"]
sig = 100 / 3 / 1000                                     # um
tx, ty = rng.normal(0, sig, 2); rot = rng.normal(0, 8e-6)
DATA["this_placement_nm"] = [round(tx * 1000, 1), round(ty * 1000, 1)]; DATA["this_rotation_urad"] = round(rot * 1e6, 2)
# die outlines (lower die, upper die ghost shifted by magnified error)
half = span / 2 + 70
cv.line([(C - half, C - half), (C + half, C - half), (C + half, C + half), (C - half, C + half), (C - half, C - half)], 2.4)
ux, uy = tx * mag * px_per_um, ty * mag * px_per_um
for i in range(n):
    for j in range(n):
        x = C - span / 2 + i * p; y = C - span / 2 + j * p
        sq = 9
        cv.line([(x - sq, y - sq), (x + sq, y - sq), (x + sq, y + sq), (x - sq, y + sq), (x - sq, y - sq)], 1.3)
        rx, ry = (x - C) / px_per_um, (y - C) / px_per_um     # um from centre
        ex = (tx - rot * ry) * mag * px_per_um; ey = (ty + rot * rx) * mag * px_per_um
        cv.circle(x + ex, y + ey, 13, 1.3)
        L = math.hypot(ex, ey)
        if L > 6:
            cv.seg(x, y, x + ex, y + ey, 1.6, 'accent')
            a = math.atan2(ey, ex)
            for b in (a + 2.6, a - 2.6): cv.seg(x + ex, y + ey, x + ex + 9 * math.cos(b), y + ey + 9 * math.sin(b), 1.6, 'accent')
# centre: 3-sigma circle and previous placements
r3 = 0.1 * mag * px_per_um
DATA["three_sigma_radius_px"] = round(r3, 1)
cv.erase_circle(C, C, r3 + 40)
cv.circle(C, C, r3, 2.6, 'accent'); cv.circle(C, C, r3 * 2 / 3, 0.9, 'accent'); cv.circle(C, C, r3 / 3, 0.9, 'accent')
cv.seg(C - r3 - 25, C, C + r3 + 25, C, 0.8); cv.seg(C, C - r3 - 25, C, C + r3 + 25, 0.8)
for k in range(40):
    a, b = rng.normal(0, sig, 2); cv.dot(C + a * mag * px_per_um, C + b * mag * px_per_um, 4.5)
cv.dot(C + ux, C + uy, 8, 'accent')
cv.plate_number(28)
write_data(28, DATA)
render(cv, 28, 'place')

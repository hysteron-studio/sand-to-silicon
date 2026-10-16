"""30 - The Glass. A plain-weave glass cloth for package cores, magnified until every filament
shows: warp and weft yarns of 36 filaments pass over and under one another; beneath the
weave, two engraved bars give the thermal expansion of the low-CTE glass (2.8 ppm/C, accent)
and of silicon (2.6 ppm/K, ink) - nearly the same length, which is the whole point."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "30 - The Glass", "title": "The Glass", "seed": SEED,
  "glass_cte_ppm_per_C": 2.8, "silicon_cte_ppm_per_K": 2.6,
  "weave": "plain (1/1)", "yarns": [11, 11], "filaments_per_yarn_drawn": 36,
  "mapping": {
    "weave": "11 x 11 yarns; a yarn is visible where it lies on top ((i + j) even = warp over); its filaments taper into the crossing",
    "accent": "one weft yarn in accent, and the glass expansion bar",
    "bars": "bar length = CTE x 600 px; glass 1680 px, silicon 1560 px",
  },
  "sources": [
    "https://www.nittobo.co.jp/eng/business/electronicmaterials/t-glass.htm (T-glass CTE 2.8 ppm/C)",
    "https://doi.org/10.1063/1.333965 (Okada & Tokumaru 1984: Si ~2.6 ppm/K at room temperature)",
  ],
}
cv = Canvas(SEED); rng = cv.rng
n = 11; x0, y0 = MARGIN + 30, MARGIN + 10; span = OUT - 2 * MARGIN - 60; p = span / n
yw = 0.92 * p; nf = DATA["filaments_per_yarn_drawn"]
acc_row = int(rng.integers(3, n - 3))
wob = [rng.normal(0, 3, 4) for _ in range(2 * n)]
def yarn(cxx, cyy, vertical, lay, wb):
    for f in range(nf):
        u = (f + 0.5) / nf - 0.5
        off = u * yw
        # filament runs the full cell, emerging from under the crossing yarn; it is shaded (heavier)
        # towards both ends where it dives, and towards the yarn edges (round cross-section)
        ts = np.linspace(0, 1, 13)
        for t0, t1 in zip(ts[:-1], ts[1:]):
            tm = (t0 + t1) / 2; dive = abs(tm - 0.5) * 2
            w = 0.7 + 1.6 * dive ** 3 + 0.9 * (2 * abs(u)) ** 4
            a0 = -p / 2 + 4 + (p - 8) * t0; a1 = -p / 2 + 4 + (p - 8) * t1
            bend = wb * math.sin(math.pi * tm)
            if vertical: cv.seg(cxx + off + bend, cyy + a0, cxx + off + bend, cyy + a1, w, lay)
            else: cv.seg(cxx + a0, cyy + off + bend, cxx + a1, cyy + off + bend, w, lay)
for i in range(n):          # warp yarn i (vertical)
    for j in range(n):      # weft yarn j (horizontal)
        cxx = x0 + (i + 0.5) * p; cyy = y0 + (j + 0.5) * p
        if (i + j) % 2 == 0: yarn(cxx, cyy, True, 'ink', wob[i][0])
        else: yarn(cxx, cyy, False, 'accent' if j == acc_row else 'ink', wob[n + j][0])
# bars
by = OUT - MARGIN + 40; bx = MARGIN + 30
for k, (val, lay) in enumerate(((2.8, 'accent'), (2.6, 'ink'))):
    L = val * 600; y = by + k * 36 - 10
    cv.seg(bx, y, bx + L, y, 5, lay)
    for m in range(0, 29):
        x = bx + m * 60
        if x <= bx + L + 1: cv.seg(x, y - (12 if m % 5 == 0 else 6), x, y, 1.2, lay)
DATA["accent_weft_row"] = acc_row
cv.plate_number(30)
write_data(30, DATA)
render(cv, 30, 'glass')

"""38 - The Final Test. A system-level tester's 48 sites seen from above, each a packaged chip
running at up to 1.4 kW under its liquid cold plate: the die's heat drawn as engraved
isotherms around seeded hot spots, the coolant as one accent serpentine per site; two sites
run hot and are struck through."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "38 - The Final Test", "title": "The Final Test", "seed": SEED,
  "sites": 48, "power_per_site_kW_max": 1.4, "cooling": "liquid, active thermal control",
  "mapping": {
    "grid": "8 x 6 sites; socket, package and die outlines per site",
    "heat": "per site, temperature field = sum of 3-5 Gaussian hot spots scaled by a seeded load (0.6-1.4 kW); isotherms every 8 K",
    "cooling": "accent serpentine of 7 passes across each cold plate",
    "result": "2 seeded sites over limit: extra isotherms + struck through",
  },
  "sources": [
    "https://www.advantest.com/en/products/component-test-system/system-level-test-systems/7038-str/ (up to 1.4 kW per site, up to 48 sites)",
    "https://www.advantest.com/en/news/2025/20250918.html",
  ],
}
cv = Canvas(SEED); rng = cv.rng
cols, rows = 8, 6; cell = (OUT - 2 * MARGIN) / cols
Y0 = (OUT - rows * cell) / 2; X0 = MARGIN
bad = set(rng.choice(48, 2, replace=False).tolist())
loads = []
g = 2; N = int(cell // g)
yy, xx = (np.mgrid[0:N, 0:N] + 0.5) * g
for idx in range(48):
    c, r = idx % cols, idx // cols
    x0, y0 = X0 + c * cell, Y0 + r * cell
    cv.line([(x0 + 8, y0 + 8), (x0 + cell - 8, y0 + 8), (x0 + cell - 8, y0 + cell - 8), (x0 + 8, y0 + cell - 8), (x0 + 8, y0 + 8)], 1.4)
    pk = 34; dk = 92
    cv.line([(x0 + pk, y0 + pk), (x0 + cell - pk, y0 + pk), (x0 + cell - pk, y0 + cell - pk), (x0 + pk, y0 + cell - pk), (x0 + pk, y0 + pk)], 1.8)
    load = rng.uniform(0.6, 1.4) * (1.25 if idx in bad else 1.0); loads.append(round(load, 2))
    T = np.zeros((N, N))
    for _ in range(int(rng.integers(3, 6))):
        hx, hy = rng.uniform(dk, cell - dk, 2); sg = rng.uniform(16, 34)
        T += load * 40 * np.exp(-((xx - hx) ** 2 + (yy - hy) ** 2) / (2 * sg * sg))
    T += load * 10 * np.exp(-((xx - cell / 2) ** 2 + (yy - cell / 2) ** 2) / (2 * 60 ** 2))
    for lev in np.arange(8, T.max(), 8):
        for cl in contours(T, lev, g, g, x0, y0):
            if len(cl) > 5: cv.line(cl, 1.4 if lev % 24 == 0 else 0.8, val=255 if lev % 24 == 0 else 190)
    # serpentine
    n = 7; a = pk + 12; b = cell - pk - 12; pts = []
    for k in range(n):
        y = y0 + a + (b - a) * k / (n - 1)
        xa, xb = (x0 + a, x0 + b) if k % 2 == 0 else (x0 + b, x0 + a)
        pts += [(xa, y), (xb, y)]
    cv.erase_poly([(x0 + pk + 2, y0 + pk + 2), (x0 + cell - pk - 2, y0 + pk + 2), (x0 + cell - pk - 2, y0 + pk + 6), (x0 + pk + 2, y0 + pk + 6)])
    cv.line(pts, 3.4, 'accent')
    cv.seg(pts[0][0] - 26, pts[0][1], pts[0][0], pts[0][1], 2.2, 'accent'); cv.seg(pts[-1][0], pts[-1][1], pts[-1][0] + 26, pts[-1][1], 2.2, 'accent')
    if idx in bad:
        cv.seg(x0 + 14, y0 + 14, x0 + cell - 14, y0 + cell - 14, 2.6); cv.seg(x0 + cell - 14, y0 + 14, x0 + 14, y0 + cell - 14, 2.6)
DATA["loads_kW"] = loads; DATA["failed_sites"] = sorted(int(b) for b in bad)
cv.plate_number(38)
write_data(38, DATA)
render(cv, 38, 'finaltest')

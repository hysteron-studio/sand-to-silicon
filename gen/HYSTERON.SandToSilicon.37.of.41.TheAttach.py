"""37 - The Attach. Underfill wicking under a flip-chip die, seen through the silicon: a bead
dispensed along one edge is drawn in by capillarity, its front advancing between 18 x 18
solder bumps, splitting and rejoining around each one; every front is an accent contour of
equal arrival time on a seeded, slightly uneven gap."""
import math, numpy as np
from scipy import ndimage
from skimage.graph import MCP_Geometric
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "37 - The Attach", "title": "The Attach", "seed": SEED,
  "underfill_cte_ppm_per_C_below_Tg": 19, "bumps": [18, 18],
  "mapping": {
    "flow": "arrival time = geodesic travel cost from the dispense edge (skimage MCP), cost = 1 + 0.35 x smooth noise, bumps impassable; 22 equal-time contours in accent",
    "bumps": "18 x 18 engraved solder balls, shaded; die edge as a heavy square",
    "bead": "stippled dispense bead outside the left edge",
  },
  "sources": [
    "https://datasheets.tdx.henkel.com/LOCTITE-ECCOBOND-UF-9000AG-en_GL.pdf (CTE 19 ppm/C below Tg)",
    "https://www.henkel.com/press-and-media/press-releases-and-kits/2022-09-19-henkel-unveils-semiconductor-capillary-underfill-for-advanced-silicon-node-flip-chip-applications-1752358",
  ],
}
cv = Canvas(SEED); rng = cv.rng
g = 3; S0 = 2140; X0 = (OUT - S0) / 2 + 60; Y0 = (OUT - S0) / 2
n = S0 // g
nb = 18; pitch = S0 / nb; rb = pitch * 0.22
yy, xx = (np.mgrid[0:n, 0:n] + 0.5) * g
obst = np.zeros((n, n), bool); centres = []
for i in range(nb):
    for j in range(nb):
        cx, cy = (i + 0.5) * pitch, (j + 0.5) * pitch; centres.append((cx, cy))
        obst |= (xx - cx) ** 2 + (yy - cy) ** 2 < (rb + 6) ** 2
noise = fbm((n, n), rng, 4, 3)
cost = 1 + 0.35 * noise; cost = np.where(obst, 1e6, cost)
m = MCP_Geometric(cost)
starts = [(r, 0) for r in range(n)]
Tm, _ = m.find_costs(starts)
Tm = np.where(obst, np.nan, Tm)
fin = np.nanmax(Tm[np.isfinite(Tm) & (Tm < 1e5)])
Tf = np.where(np.isfinite(Tm) & (Tm < 1e5), Tm, fin * 1.2)
Tf = ndimage.gaussian_filter(Tf, 1.0)
stop = 0.86 * fin
nfr = 22
for k in range(1, nfr + 1):
    lev = stop * k / nfr
    for c in contours(Tf, lev, g, g, X0, Y0):
        if len(c) > 8: cv.line(c, 4.0 if k % 5 == 0 else 2.4, 'accent')
# wetted region light hatch
for cx, cy in centres:
    x, y = X0 + cx, Y0 + cy
    cv.sphere(x, y, rb, spacing=6.0, wmax=2.4, outline=2.2)
die = [(X0, Y0), (X0 + S0, Y0), (X0 + S0, Y0 + S0), (X0, Y0 + S0)]
cv.line(die + [die[0]], 3.2)
# dispense bead
bx = rng.uniform(X0 - 110, X0 - 10, 2600); by = rng.uniform(Y0, Y0 + S0, 2600)
keep = rng.random(2600) < (bx - (X0 - 110)) / 100
cv.stipple(bx[keep], by[keep], 1.8, 'accent')
cv.line([(X0 - 116 + 8 * math.sin(t / 40), t) for t in np.linspace(Y0, Y0 + S0, 80)], 1.2, 'accent')
DATA["front_stop_fraction"] = 0.86
cv.plate_number(37)
write_data(37, DATA)
render(cv, 37, 'attach')

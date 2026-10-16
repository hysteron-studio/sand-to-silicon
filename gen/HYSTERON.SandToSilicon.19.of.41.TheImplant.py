"""19 - The Implant. Boron ions at 30 keV enter a silicon crystal, tilted 7 degrees to avoid
channelling, and come to rest in a Gaussian cloud (projected range 98 nm, straggle 36 nm);
every track is a straight run that breaks into nuclear-collision zigzags near its end, and
every resting dopant is an accent dot - beside it, the dose profile drawn as a rule."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "19 - The Implant", "title": "The Implant", "seed": SEED,
  "ion": "B+", "energy_keV": 30, "tilt_deg": 7, "projected_range_nm": 98, "straggle_nm": 36,
  "dose_cm2": 1e15, "tool_range": {"energy_max_MeV": 15, "dose_max_cm2": 1e16},
  "mapping": {
    "scale": "8.5 px per nm; the crystal is drawn as the projected diamond-cubic dumbbell lattice (a = 0.543 nm, x10 for legibility)",
    "tracks": "~520 ion tracks tilted 7 deg; depth drawn from N(Rp, dRp), lateral straggle ~0.7 dRp; last third of each track zigzags (nuclear stopping)",
    "dopants": "each resting ion an accent dot; the Gaussian dose profile at the right edge",
  },
  "sources": [
    "https://www.axcelis.com/products/purion-xe-series-high-energy-ion-implantation/ (up to 15 MeV)",
    "https://www.axcelis.com/wp-content/uploads/2024/04/Introducing_the_PurionH200_Single_Wafer_High_Current_Implanter.pdf (doses to 1e16, extendable to 1e17)",
    "Gibbons, Johnson & Mylroie, Projected Range Statistics (1975): B in Si at 30 keV, Rp ~ 98 nm, dRp ~ 36 nm",
  ],
}
cv = Canvas(SEED); rng = cv.rng
S = 8.5; y_s = 900; xL, xR = MARGIN + 40, OUT - MARGIN - 300
Rp, dR = DATA["projected_range_nm"], DATA["straggle_nm"]
# lattice: dumbbells
a = 0.543 * 10 * S
nd = 0
for j, y in enumerate(np.arange(y_s + 20, y_s + 2.05 * Rp * S + 40 + 400, a / 2)):
    if y > OUT - MARGIN - 40: break
    for x in np.arange(xL + (a / 4 if j % 2 else 0), xR, a / 2):
        cv.dot(x, y, 2.1); cv.dot(x + a / 8, y + a / 8, 2.1); cv.seg(x, y, x + a / 8, y + a / 8, 0.9); nd += 1
cv.line([(xL, y_s), (xR, y_s)], 2.8)
# ion tracks
tilt = math.radians(DATA["tilt_deg"]); N = 520; rest = []
for i in range(N):
    depth = rng.normal(Rp, dR)
    if depth < 5: continue
    x_in = rng.uniform(xL + 60, xR - 260)
    L = depth / math.cos(tilt) * S
    x_in_top = x_in - math.tan(tilt) * (y_s - MARGIN)
    if i % 4 == 0: cv.seg(x_in - math.tan(tilt) * (y_s - MARGIN - 150), MARGIN + 150 + rng.uniform(0, 260), x_in, y_s, 0.5, val=170)
    pts = [(x_in, y_s)]; x, y = x_in, y_s; steps = 26
    for k in range(steps):
        frac = (k + 1) / steps
        dx = math.sin(tilt) * L / steps; dy = math.cos(tilt) * L / steps
        if frac > 0.62:
            ang = rng.normal(0, 0.9); dx, dy = dx * math.cos(ang) - dy * math.sin(ang), dx * math.sin(ang) + dy * math.cos(ang)
        x += dx; y += abs(dy) * 0.95 + 0.05 * dy
        pts.append((x, y))
    x += rng.normal(0, 0.7 * dR * S * 0.4)
    pts[-1] = (x, pts[-1][1])
    if not all(xL + 4 < p[0] < xR - 4 for p in pts): continue
    cv.line(pts, 0.55, val=210)
    rest.append((x, pts[-1][1]))
for x, y in rest: cv.dot(x, y, 8.0, 'accent')
DATA["tracks"] = len(rest); DATA["lattice_dumbbells"] = nd
# profile at right
px0 = OUT - MARGIN - 200
cv.line([(px0, y_s), (px0, y_s + 2.3 * Rp * S)], 1.6)
z = np.linspace(0, 2.3 * Rp, 200); g = np.exp(-0.5 * ((z - Rp) / dR) ** 2)
cv.line(list(zip(px0 + g * 180, y_s + z * S)), 2.6, 'accent')
for k in range(0, 21):
    yy = y_s + k * 10 * S; cv.seg(px0 - (14 if k % 5 == 0 else 7), yy, px0, yy, 1.2)
cv.seg(px0, y_s + Rp * S, px0 + 190, y_s + Rp * S, 1.0)
cv.plate_number(19)
write_data(19, DATA)
render(cv, 19, 'implant')

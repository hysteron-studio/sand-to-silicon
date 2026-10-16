"""36 - The Mold. Long hair-thin bond wires (15 um across, up to 5 mm long) arc from a die to
their fingers on the substrate, a fan of loops in depth; the molding resin rises around them
in 20 level contours (accent), calm and horizontal, and not one wire is swept aside."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "36 - The Mold", "title": "The Mold", "seed": SEED,
  "wire_diameter_um": 15, "wire_length_mm_max": 5, "panel_mm": 320, "wafer_inch": 12,
  "mapping": {
    "scale": "horizontal 360 px per mm (5 mm span = 1800 px); vertical exaggerated x4 so loop heights read",
    "wires": "24 loops in four depth rows; spans 3.2-5 mm; loop height 0.16-0.52 mm; back rows lighter",
    "resin": "20 level lines rising from substrate to cap, very small seeded ripple; each line breaks where a wire crosses in front",
    "sweep": "zero: every wire drawn exactly on its planned path",
  },
  "sources": [
    "https://www.towajapan.co.jp/en/technology/molding/ (15 um x 5 mm wires molded without sweep)",
    "https://www.towajapan.co.jp/en/products/molding/cpm/ (12-inch WLP, 320 mm PLP)",
  ],
}
cv = Canvas(SEED); rng = cv.rng
sx = 360.0; vz = 4.0 * sx
xL, xR = MARGIN, OUT - MARGIN
y_sub = 2250; y_cap = y_sub - 0.56 * vz
# substrate
cv.line([(xL, y_sub), (xR, y_sub)], 2.6)
cv.hatch_poly([(xL, y_sub + 4), (xR, y_sub + 4), (xR, y_sub + 260), (xL, y_sub + 260)], 45, 12, 1.0)
cv.line([(xL, y_sub + 260), (xR, y_sub + 260)], 1.6)
# die
dx0, dx1 = xL + 60, xL + 640; dh = 0.1 * vz
die = [(dx0, y_sub), (dx1, y_sub), (dx1, y_sub - dh), (dx0, y_sub - dh)]
cv.hatch_poly(die, -45, 6, 1.0); cv.line(die + [die[0]], 2.2)
# wires
wires = []
for row in range(4):
    for k in range(6):
        span = rng.uniform(2.4, 5.0) * sx
        x0 = dx1 - 40 - row * 120 - k * 18; x1 = min(xR - 20, x0 + span)
        hgt = (0.16 + 0.06 * k + 0.02 * row) * vz
        wires.append((row, x0, x1, hgt))
wires.sort(key=lambda w: w[0])
paths = []
for row, x0, x1, hgt in wires:
    t = np.linspace(0, 1, 160)
    # ball bond rises steeply, long gentle span down to the stitch
    x = x0 + (x1 - x0) * t
    y0 = y_sub - dh
    y = y0 + (y_sub - y0) * t - hgt * (np.sin(np.pi * np.clip(t * 1.25, 0, 1) ** 0.6) * (1 - t) ** 0.6)
    pts = list(zip(x, y)); paths.append(pts)
    w = 2.6 - 0.35 * row
    cv.line(pts, w, val=255 - row * 25)
    cv.dot(x0, y0 - 3, 6 - row * 0.6); cv.line([(x1 - 14, y_sub), (x1 + 10, y_sub - 4)], 3.0)
# resin levels
nlev = 20
for k in range(1, nlev + 1):
    y = y_sub - (y_sub - y_cap) * k / nlev
    xs = np.linspace(xL, xR, 600)
    ys = y + 2.0 * np.sin(xs / (90 + 7 * k) + k) + rng.normal(0, 0.3, xs.size)
    # break where any wire crosses (wire in front)
    seg = []; 
    def near(x, yy):
        for pts in paths:
            P = np.array(pts); d = np.min(np.hypot(P[:, 0] - x, P[:, 1] - yy))
            if d < 9: return True
        return False
    for x, yy in zip(xs, ys):
        if near(x, yy):
            if len(seg) > 1: cv.line(seg, 2.8 if k % 5 == 0 else 1.6, 'accent')
            seg = []
        else: seg.append((x, yy))
    if len(seg) > 1: cv.line(seg, 2.8 if k % 5 == 0 else 1.6, 'accent')
# mold cap / cavity
cv.line([(xL, y_cap - 6), (xR, y_cap - 6)], 2.4)
cv.hatch_poly([(xL, y_cap - 10), (xR, y_cap - 10), (xR, y_cap - 300), (xL, y_cap - 300)], -45, 14, 0.9)
cv.line([(xL, y_cap - 300), (xR, y_cap - 300)], 1.6)
DATA["wires_drawn"] = len(wires)
cv.plate_number(36)
write_data(36, DATA)
render(cv, 36, 'mold')

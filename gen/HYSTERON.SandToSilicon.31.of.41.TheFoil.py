"""31 - The Foil. An ultra-thin copper foil (3 um) peeled from its 18 um carrier, drawn in side
elevation with the two thicknesses held to their true 3 : 18 ratio; once free, the foil
curls on an Euler spiral into a loose scroll, its rough treated underside stippled and its
body in accent."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "31 - The Foil", "title": "The Foil", "seed": SEED,
  "foil_um": 3, "carrier_um": 18, "foil_range_um": [1.5, 5], "carrier_options_um": [12, 18],
  "mapping": {
    "scale": "14 px per um: carrier 252 px, foil 42 px",
    "carrier": "a straight band of rolled copper, hatched along the rolling direction",
    "peel": "the foil leaves the carrier at x = 0.42 W and follows an Euler spiral (curvature rising linearly with arc length), ~1.3 turns",
    "release layer": "a fine dashed line between foil and carrier where still attached",
  },
  "sources": ["https://em.mitsui-kinzoku.com/en/copper-foil/products/ultra-thin-copper-foil/ (1.5-5 um foil on 12 or 18 um carrier, peeled after lamination)"],
}
cv = Canvas(SEED); rng = cv.rng
k = 14.0; tc = 18 * k; tf = 3 * k
xL, xR = MARGIN, OUT - MARGIN
yc = 2250                      # top of carrier
cv.line([(xL, yc), (xR, yc)], 2.0); cv.line([(xL, yc + tc), (xR, yc + tc)], 2.6)
for m in range(1, 18):
    y = yc + m * tc / 18
    xa = xL; 
    while xa < xR:
        L = rng.uniform(80, 400); cv.seg(xa, y, min(xR, xa + L), y, 0.7); xa += L + rng.uniform(10, 50)
x_peel = xL + 0.42 * (xR - xL)
# attached foil on the left
cv.line([(xL, yc - tf), (x_peel, yc - tf)], 2.2, 'accent')
cv.hatch_poly([(xL, yc - 2), (x_peel, yc - 2), (x_peel, yc - tf), (xL, yc - tf)], 0, 5, 1.1, 'accent')
for x in np.arange(xL, x_peel, 22): cv.seg(x, yc - 1, x + 10, yc - 1, 1.0)
# free foil: Euler spiral from the peel point, lower face = path
def spiral(c1):
    pts = [(x_peel, yc - 1)]; th = 0.0; ds = 3.0; s = 0.0; x, y = pts[0]
    while th < 2 * math.pi * 1.3:
        s += ds; th = c1 * s * s
        x += ds * math.cos(-th); y += ds * math.sin(-th); pts.append((x, y))
    return pts, s
c1 = 1.9e-7
while True:
    pts, s = spiral(c1); A = np.array(pts)
    if A[:, 0].max() < xR - 40 and A[:, 1].min() > MARGIN + 60: break
    c1 *= 1.08
DATA["euler_c_per_px2"] = c1
P = np.array(pts)
# fit: scale curl into the frame (keep start fixed)
DATA["arc_length_px"] = round(s)
nrm = []
for i in range(len(P)):
    a = P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]; a = a / (np.linalg.norm(a) + 1e-9); nrm.append((a[1], -a[0]))
nrm = np.array(nrm)
up = P + nrm * tf
cv.line([tuple(q) for q in P], 1.6, 'accent'); cv.line([tuple(q) for q in up], 2.2, 'accent')
# body hatch across the band (short strokes normal to the path)
for i in range(0, len(P), 4):
    a, b = P[i] + nrm[i] * 2, up[i] - nrm[i] * 2
    cv.seg(a[0], a[1], b[0], b[1], 1.0, 'accent')
# treated (nodular) underside of the free foil
for i in range(0, len(P), 2):
    q = P[i] - nrm[i] * rng.uniform(1, 7); cv.dot(q[0], q[1], rng.uniform(1.0, 2.2))
DATA["spiral_points"] = len(P); DATA["bbox"] = [int(P[:, 0].min()), int(P[:, 1].min()), int(P[:, 0].max()), int(P[:, 1].max())]
cv.plate_number(31)
write_data(31, DATA)
render(cv, 31, 'foil')
print(DATA["bbox"])

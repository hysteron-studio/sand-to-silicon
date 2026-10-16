"""20 - The Clean. A magnified side view of a wafer surface under a sweeping rinse: the
liquid's boundary-layer streamlines bend over particles and residue films on the left,
lift them (accent) along the flow, and leave clean surface behind; the stipple of trace
metal on the surface halves from left to right, from 10 ppt to 5 ppt."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "20 - The Clean", "title": "The Clean", "seed": SEED,
  "metal_impurity_ppt_each": 10, "target_ppt": 5,
  "mapping": {
    "flow": "34 boundary-layer streamlines, spacing growing with height (log-law), each deflected over the particles beneath it",
    "particles": "seeded residue particles and film patches on the left; in the middle band they detach and ride the streamlines up (accent with motion strokes)",
    "trace metal": "surface stipple density proportional to ppt: 10 on the dirty side, 5 on the clean side",
  },
  "sources": [
    "https://www.mgc.co.jp/eng/ir/files/2410023e.pdf (metal impurities 10 ppt each, tightening to 5 ppt)",
    "https://www.mgc.co.jp/eng/rd/technology/super-pure-hydrogen-peroxide.html",
  ],
}
cv = Canvas(SEED); rng = cv.rng
xL, xR = MARGIN, OUT - MARGIN
ys = 2050
# substrate
cv.line([(xL, ys), (xR, ys)], 3.0)
cv.hatch_poly([(xL, ys + 6), (xR, ys + 6), (xR, ys + 420), (xL, ys + 420)], 90, 11, 1.0)
cv.line([(xL, ys + 420), (xR, ys + 420)], 1.6)
# particles on the left 45%
parts = []
for _ in range(70):
    x = rng.uniform(xL + 30, xL + 0.46 * (xR - xL)); r = rng.lognormal(2.7, 0.5)
    parts.append((x, r))
films = [(rng.uniform(xL + 20, xL + 900), rng.uniform(60, 220)) for _ in range(7)]
for x, w in films:
    pts = [(x + t * w, ys - 7 * math.sin(math.pi * t) - 1) for t in np.linspace(0, 1, 30)]
    cv.hatch_poly(pts + [(x + w, ys), (x, ys)], 0, 3, 0.9); cv.line(pts, 1.4)
def bump(x):
    h = np.zeros_like(x)
    for px, r in parts: h = np.maximum(h, 1.5 * r * np.exp(-((x - px) / (2.2 * r)) ** 2))
    return h
for px, r in parts:
    th = np.linspace(0, 2 * math.pi, 18); rr = r * (1 + 0.25 * rng.standard_normal(18)); rr = np.convolve(np.r_[rr, rr[:2]], [1/3]*3, 'valid')
    poly = [(px + q * math.cos(t), ys - r + q * math.sin(t)) for q, t in zip(rr, th)]
    cv.erase_poly(poly); cv.line(poly + [poly[0]], 1.8); cv.hatch_poly(poly, 60, 3.2, 0.9)
# streamlines
xx = np.linspace(xL, xR, 900); B = bump(xx)
nl = 34
for k in range(nl):
    h = 10 * (1.16 ** k)
    if ys - h < MARGIN + 60: break
    damp = math.exp(-h / 120)
    y = ys - h - B * damp - 18 * damp * np.exp(-((xx - (xL + 0.55 * (xR - xL))) / 400) ** 2)
    y += 3 * np.sin(xx / (140 + 9 * k) + k) * (1 - damp)
    cv.line(list(zip(xx, y)), 1.0 + 0.6 * (k % 4 == 0))
DATA["streamlines"] = k
# lifted particles: ride up and to the right
lifted = 0
for _ in range(46):
    t = rng.random(); x = xL + (0.36 + 0.5 * t) * (xR - xL) + rng.normal(0, 70)
    h = 30 + (t ** 1.3) * 1100 * rng.uniform(0.35, 1.0); y = ys - h; r = rng.lognormal(2.4, 0.4)
    th = np.linspace(0, 2 * math.pi, 16)
    poly = [(x + r * (1 + 0.2 * rng.standard_normal()) * math.cos(a), y + r * math.sin(a)) for a in th]
    cv.erase_poly(poly); cv.poly(poly, 'accent')
    for m in range(3):
        L = rng.uniform(40, 120) * (1 + t); dy = rng.normal(0, 4)
        cv.seg(x - r - 8 - L, y + (m - 1) * r * 0.6 + dy + L * 0.25, x - r - 8, y + (m - 1) * r * 0.6, 1.0, 'accent')
    lifted += 1
DATA["particles_on_surface"] = len(parts); DATA["particles_lifted"] = lifted
# trace-metal stipple, density 10 : 5
mid = xL + 0.5 * (xR - xL)
for x0, x1, ppt in ((xL, mid, 10), (mid, xR, 5)):
    n = int(ppt * 60)
    xs = rng.uniform(x0, x1, n); yv = ys - 3 - rng.exponential(5, n)
    cv.stipple(xs, yv, 1.6)
cv.plate_number(20)
write_data(20, DATA)
render(cv, 20, 'clean')

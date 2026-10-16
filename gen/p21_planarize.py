"""21 - The Planarize. Copper damascene in section under chemical-mechanical polishing: the
plated copper blanket (bumpy over dense lines, sunken over wide ones) is planed down pass by
pass, each pass an engraved profile, high spots removed fastest (Preston: rate ~ pressure),
until the barrier is cleared and only flush inlaid wires remain in accent, with the slight
dishing of the widest line."""
import math, numpy as np
from scipy import ndimage
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "21 - The Planarize", "title": "The Planarize", "seed": SEED,
  "slurry_families": ["oxide", "tungsten", "polysilicon", "copper", "barrier"],
  "passes_drawn": 31,
  "mapping": {
    "section": "oxide with trenches of four widths (dense narrow lines, isolated, medium, one wide pad)",
    "blanket": "initial electroplated Cu surface: conformal plus overplate bumps over dense arrays",
    "passes": "31 profiles; each step removes rate = k * (1 + 1.6 * local height above the pad-smoothed surface)",
    "result": "copper left in the trenches in accent; the wide line dishes",
    "pad": "the pad above as a rough engraved band with slurry abrasive stipple",
  },
  "sources": [
    "https://www.fujimiinc.co.jp/english/service/cmp/lineup.html (separate slurries for oxide, W, poly-Si, Cu, barrier)",
    "https://www.fujimi.com/catalog/planerlite-7000/",
    "Preston, J. Soc. Glass Technol. 11 (1927): removal rate proportional to pressure x velocity",
  ],
}
cv = Canvas(SEED); rng = cv.rng
xL, xR = MARGIN, OUT - MARGIN
n = int(xR - xL); X = np.arange(n) + xL
y_ox = 1950.0; tdep = 300.0
# trenches
T = np.zeros(n, bool)
groups = [(140, 16, 20, 11), (760, 1, 60, 0), (980, 3, 110, 90), (1500, 1, 520, 0)]
for x0, cnt, w, gap in groups:
    for k in range(cnt): T[x0 + k * (w + gap): x0 + k * (w + gap) + w] = True
# initial surface (height above oxide, positive up)
plate = 560.0
Tf = T.astype(float)
dense = ndimage.uniform_filter1d(Tf, 160)
h = plate - 230 * ndimage.gaussian_filter1d(Tf * (dense < 0.5), 40) + 150 * ndimage.gaussian_filter1d((dense > 0.5).astype(float), 50)
h = ndimage.gaussian_filter1d(h, 8)
dish = 3 + 34 * ndimage.uniform_filter1d(Tf, 480) ** 1.5         # wide lines dish deepest
profiles = [h.copy()]
for p in range(DATA["passes_drawn"] - 1):
    sm = ndimage.gaussian_filter1d(h, 220)
    rate = 21.0 * (1 + 1.6 * np.clip(h - sm, 0, None) / 40)
    hn = ndimage.gaussian_filter1d(h - rate, 2.0)
    hn = np.where(T, np.maximum(hn, -dish * min(1, max(0, p - 18) / 10)), np.maximum(hn, 0.0))
    h = hn; profiles.append(h.copy())
final = h
# oxide body
top_line = [(x, y_ox - (0 if not t else -tdep)) for x, t in zip(X, T)]
ox_poly = [(xL, y_ox + tdep + 380), *top_line, (xR, y_ox + tdep + 380)]
cv.hatch_poly(ox_poly, 45, 13, 1.0)
cv.line(top_line, 2.4)
cv.line([(xL, y_ox + tdep + 380), (xR, y_ox + tdep + 380)], 1.6)
# final copper in trenches (accent) via mask
mask = np.zeros((OUT, OUT), np.float32)
for i, (x, t) in enumerate(zip(X, T)):
    if t:
        top = int(y_ox - min(final[i], 0) - 0) if final[i] < 0 else int(y_ox)
        mask[top:int(y_ox + tdep), int(x)] = 1
yy_, xx_ = np.mgrid[0:OUT, 0:OUT]; cv.paint(mask * ((xx_ % 7) < 3), 'accent', 1.0)
for i0 in np.flatnonzero(np.diff(T.astype(int))): cv.line([(X[i0] + 0.5, y_ox), (X[i0] + 0.5, y_ox + tdep)], 1.6, 'accent')
# passes
for k, pr in enumerate(profiles):
    y = y_ox - pr
    pts = [(x, yy) for x, yy in zip(X[::3], y[::3])]
    cv.line(pts, 2.4 if k == 0 else (1.6 if k % 5 == 0 else 0.9), 'ink', val=255 if k % 5 == 0 else 210)
# pad above the first profile
yp = y_ox - profiles[0].max() - 400
pad = yp + 6 * np.sin(X / 37) + 4 * rng.standard_normal(n).cumsum() / 30
cv.line(list(zip(X[::2], pad[::2] + 300)), 2.0)
cv.hatch_poly([(xL, yp + 60)] + list(zip(X[::6], pad[::6] + 300)) + [(xR, yp + 60)], -30, 16, 0.8)
cv.line([(xL, yp + 60), (xR, yp + 60)], 1.6)
gx = rng.uniform(xL, xR, 1400); gy = np.interp(gx, X, pad + 300) + rng.uniform(6, 44, 1400)
cv.stipple(gx, gy, 2.0)
cv.plate_number(21)
write_data(21, DATA)
render(cv, 21, 'planarize')

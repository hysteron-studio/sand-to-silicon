"""18 - The Flow. An eight-channel strip chart from a gas box: on each channel the inlet
pressure (ink) is kicked by random upstream disturbances, while the mass-flow controller's
output (accent) stays level and recovers from every kick within its 100 ms settling time,
drawn on a 10 s chart ruled every 100 ms."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "18 - The Flow", "title": "The Flow", "seed": SEED,
  "settling_time_ms": 100, "channels": 8, "chart_seconds": 10, "rule_ms": 100,
  "mapping": {
    "chart": "10 s across 2340 px; fine rules every 100 ms (one settling time), heavy every 1 s",
    "ink trace": "inlet pressure per channel: random steps and ripples (Poisson upsets, ~0.5 per s)",
    "accent trace": "controlled flow: each pressure step leaves a transient that decays with tau = 100/4.6 ms (within 1% after 100 ms)",
  },
  "sources": [
    "https://www.horiba.com/int/semiconductor/products/detail/action/show/Product/d700t-6146/ (settling <=100 ms)",
    "https://www.horiba.com/int/semiconductor/products/detail/action/show/Product/sec-z700s-series-2038/ (pressure-insensitive MFC)",
  ],
}
cv = Canvas(SEED); rng = cv.rng
xL, xR = MARGIN, OUT - MARGIN
yT, yB = MARGIN + 40, OUT - MARGIN - 40
T = DATA["chart_seconds"]; nch = DATA["channels"]
px_s = (xR - xL) / T
# sprocket holes + chart edges
for y in (yT - 30, yB + 30):
    cv.line([(xL, y), (xR, y)], 2.4)
for x in np.arange(xL + 20, xR, 58):
    cv.circle(x, yT - 15, 5, 1.2); cv.circle(x, yB + 15, 5, 1.2)
# rules
for i in range(0, int(T * 10) + 1):
    x = xL + i * px_s / 10
    cv.line([(x, yT), (x, yB)], 1.4 if i % 10 == 0 else 0.5, val=255 if i % 10 == 0 else 120)
band = (yB - yT) / nch
tt = np.linspace(0, T, 4000); tau = 0.1 / 4.6
ups = 0
for c in range(nch):
    yc = yT + band * (c + 0.5)
    cv.line([(xL, yT + band * c), (xR, yT + band * c)], 0.9) if c else None
    # pressure: steps at Poisson times + slow ripple
    n = rng.poisson(0.5 * T); ts = np.sort(rng.uniform(0.2, T - 0.2, n)); amp = rng.normal(0, 1, n) * 0.9
    ups += n
    p = 0.12 * np.sin(2 * math.pi * tt * rng.uniform(0.3, 1.2) + rng.uniform(0, 6)) + 0.05 * np.cumsum(rng.normal(0, 0.03, tt.size))
    f = np.zeros_like(tt)
    for t0, a in zip(ts, amp):
        p += a * (tt >= t0)
        dt = tt - t0; m = dt >= 0
        f[m] += a * 0.55 * np.exp(-dt[m] / tau) * np.cos(dt[m] / tau * 1.7)
    p -= p.mean()
    sc = band * 0.3 / max(1e-6, np.abs(p).max())
    cv.line(list(zip(xL + tt * px_s, yc - band * 0.12 - p * sc)), 2.0, jitter=0.25)
    fy = yc + band * 0.3 - f * band * 0.16
    cv.line(list(zip(xL + tt * px_s, fy)), 3.4, 'accent')
    for t0 in ts:                                     # 100 ms settle bracket
        x0 = xL + t0 * px_s; x1 = x0 + 0.1 * px_s; y = yc + band * 0.42
        cv.line([(x0, y - 6), (x0, y), (x1, y), (x1, y - 6)], 1.2, 'accent')
DATA["pressure_upsets"] = int(ups)
cv.plate_number(18)
write_data(18, DATA)
render(cv, 18, 'flow')
